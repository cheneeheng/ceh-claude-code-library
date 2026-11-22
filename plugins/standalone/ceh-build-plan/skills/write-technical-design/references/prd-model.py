"""prd/v1: the product requirements' model and its Markdown renderer.

The format in code, per prd-schema.md beside this file: `artifact.py` validates a `PRD.yaml` with
`MODEL` and writes `render(doc, source)` beside it. Copied word for word into every skill that
holds prd-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "prd"
VERSION = 1

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
# A heading the renderer numbers: no em dash, which leaves a double hyphen in the anchor.
Heading = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n—]*$")
]
FeatureId = Annotated[str, StringConstraints(pattern=r"^F\d{2,}$")]
# Repo-relative with forward slashes only, so one plan has one spelling on every OS: no leading
# slash, no backslash and no drive colon. An empty, `.` or `..` segment is refused in the
# model's rules, since pydantic's regex has no look-around.
PlanPath = Annotated[
    str, StringConstraints(pattern=r"^[A-Za-z0-9_.-][A-Za-z0-9_./-]*\.yaml$")
]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


def _strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from _strings(v)


class Feature(_Strict):
    id: FeatureId
    name: Heading
    user: Line
    requirements: list[Text] = Field(min_length=1)
    acceptance: list[Text] = Field(min_length=1)
    depends_on: list[FeatureId]
    status: Literal["todo", "planned", "built"]
    plans: list[PlanPath]


class NonGoal(_Strict):
    # The id of a feature that was dropped, kept so it is never given to another feature.
    id: Optional[FeatureId] = None
    item: Line
    reason: Text


class Replaced(_Strict):
    # A feature a later version replaced: history, never a requirement.
    id: FeatureId
    name: Heading
    date: dt.date
    replaced_by: list[FeatureId] = Field(min_length=1)
    reason: Text
    plans: list[PlanPath]


def _entry_lists(owner: str, lists: tuple[tuple[str, list[str]], ...]) -> None:
    for name, items in lists:
        if len(set(items)) != len(items):
            raise ValueError(f"{owner}: {name} lists an entry twice")
        if name == "plans" and any(
            s in ("", ".", "..") for p in items for s in p.split("/")
        ):
            raise ValueError(
                f"{owner}: plans holds a path with an empty, . or .. segment"
            )


class Prd(_Strict):
    schema_: Literal["prd/v1"] = Field(alias="schema")
    status: Literal["draft", "adopted"]
    updated: dt.date
    features: list[Feature] = Field(min_length=1)
    non_functional: list[Text]
    non_goals: list[NonGoal]
    replaced: list[Replaced] = []

    @model_validator(mode="after")
    def _rules(self) -> Prd:
        if self.status == "adopted" and any(
            "[assumed]" in s for s in _strings(self.model_dump())
        ):
            raise ValueError("status adopted allows no [assumed], set draft")
        ids = [f.id for f in self.features]
        retired = [g.id for g in self.non_goals if g.id] + [r.id for r in self.replaced]
        for i in retired:
            if retired.count(i) > 1 or i in ids:
                raise ValueError(f"{i}: id is used twice")
        # A successor is live, a non-goal, or replaced later, which rules out itself and a cycle.
        successors = set(ids) | {g.id for g in self.non_goals if g.id}
        for r in reversed(self.replaced):
            _entry_lists(r.id, (("replaced_by", r.replaced_by), ("plans", r.plans)))
            for by in r.replaced_by:
                if by not in successors:
                    raise ValueError(
                        f"{r.id}: replaced_by names {by}, not a feature, a non-goal or a"
                        " later replaced entry"
                    )
            successors.add(r.id)
        earlier: set[str] = set()
        for f in self.features:
            if f.id in earlier:
                raise ValueError(f"{f.id}: id is used twice")
            _entry_lists(f.id, (("depends_on", f.depends_on), ("plans", f.plans)))
            for dep in f.depends_on:
                if dep not in ids:
                    raise ValueError(f"{f.id}: depends_on names {dep}, not a feature")
                # Only an earlier feature, which also rules out itself and any cycle.
                if dep not in earlier:
                    raise ValueError(
                        f"{f.id}: depends_on names {dep}, which must be listed before it"
                    )
            if f.status == "todo" and f.plans:
                raise ValueError(f"{f.id}: status todo allows no plans, set planned")
            if f.status == "planned" and not f.plans:
                raise ValueError(f"{f.id}: status planned needs a plan in plans")
            earlier.add(f.id)
        return self


MODEL = Prd


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def anchor(heading: str) -> str:
    """GitHub's heading anchor: lowercase, keep letters, digits, spaces, - and _, spaces to -."""
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


def _item(prefix: str, text: str) -> str:
    """A list item: continuation lines indented under its text, blank lines kept blank."""
    lines = text.split("\n")
    pad = " " * len(prefix)
    return prefix + "\n".join([lines[0]] + [pad + ln if ln else "" for ln in lines[1:]])


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def render(doc: Prd, source: str) -> str:
    """The product requirements as Markdown. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    heads = [f"01.{n:02d} {f.id}: {f.name}" for n, f in enumerate(doc.features, 1)]
    sections = [
        ("01. Features", heads),
        ("02. Non-functional requirements", []),
        ("03. Non-goals", []),
    ]
    if doc.replaced:
        sections.append(("04. Replaced features", []))
    contents = []
    for head, subs in sections:
        contents.append(f"- [{head}](#{anchor(head)})")
        contents += [f"  - [{s}](#{anchor(s)})" for s in subs]
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("status", doc.status),
        _key("updated", doc.updated),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        "# Product requirements",
        "",
        f"**Status:** {doc.status}, updated {doc.updated.isoformat()}",
        "",
        "## Contents",
        "",
        *contents,
        "",
        "## 01. Features",
        "",
        "| Id | Feature | Status | Depends on |",
        "| --- | --- | --- | --- |",
        *[
            f"| {f.id} | {_cell(f.name)} | {f.status} | {', '.join(f.depends_on) or 'None'} |"
            for f in doc.features
        ],
    ]
    for head, f in zip(heads, doc.features):
        out += [
            "",
            f"### {head}",
            "",
            f"**User:** {f.user}",
            "",
            f"**Status:** {f.status}",
            "",
            "**Requirements:**",
            "",
            *[_item("- ", r) for r in f.requirements],
            "",
            "**Acceptance:**",
            "",
            *[_item("- ", a) for a in f.acceptance],
            "",
            f"**Depends on:** {', '.join(f.depends_on) or 'None'}",
            "",
            f"**Plans:** {', '.join(f'`{p}`' for p in f.plans) or 'None'}",
        ]
    out += ["", "## 02. Non-functional requirements", ""]
    out += [_item("- ", r) for r in doc.non_functional] or ["None"]
    out += ["", "## 03. Non-goals", ""]
    out += [
        _item("- ", f"**{g.item}{f' (was {g.id})' if g.id else ''}.** {g.reason}")
        for g in doc.non_goals
    ] or ["None"]
    if doc.replaced:
        out += [
            "",
            "## 04. Replaced features",
            "",
            "History, not requirements: nothing below describes the product as it is now.",
            "",
        ]
        for r in doc.replaced:
            out += [
                _item(
                    "- ",
                    f"**{r.id}: {r.name}.** Replaced by {', '.join(r.replaced_by)}"
                    f" on {r.date.isoformat()}. {r.reason}",
                ),
                f"  - Plans: {', '.join(f'`{p}`' for p in r.plans) or 'None'}",
            ]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
