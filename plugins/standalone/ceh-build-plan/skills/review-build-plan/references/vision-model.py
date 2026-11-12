"""vision/v2: the vision document's model and its Markdown renderer.

The format in code, per vision-schema.md beside this file: `artifact.py` validates a `VISION.yaml`
with `MODEL` and writes `render(doc, source)` beside it, in the `vision/v1` layout. Copied word for
word into every skill that holds vision-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "vision"
VERSION = 2

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
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


class Trait(_Strict):
    trait: Line
    meaning: Text


class Identity(_Strict):
    name: Line
    sentence: Text
    is_: list[Trait] = Field(alias="is", min_length=1)
    is_not: list[Text] = Field(min_length=1)


class Scope(_Strict):
    text: Text
    test: Line
    refuses: Text


class Goal(_Strict):
    goal: Line
    measure: Text


class NonGoal(_Strict):
    thing: Line
    reason: Text


class Principle(_Strict):
    name: Line
    rule: Text
    ask: Text


class Rank(_Strict):
    principle: Line
    protects: Text


class Conflicts(_Strict):
    order: list[Rank] = Field(min_length=1)
    example: Text


class Section(_Strict):
    title: Line
    body: Text


class Vision(_Strict):
    schema_: Literal["vision/v2"] = Field(alias="schema")
    status: Literal["draft", "adopted"]
    updated: dt.date
    identity: Identity
    vision: Text
    scope: Scope
    goals: list[Goal] = Field(min_length=1)
    non_goals: list[NonGoal]
    principles: list[Principle] = Field(min_length=1)
    conflicts: Conflicts
    gaps: list[Text]
    extra_sections: list[Section]
    changing: Text

    @model_validator(mode="after")
    def _rules(self) -> Vision:
        if self.status == "adopted" and any(
            "[assumed]" in s for s in _strings(self.model_dump())
        ):
            raise ValueError("status adopted allows no [assumed], set draft")
        names = {p.name for p in self.principles}
        for r in self.conflicts.order:
            if r.principle not in names:
                raise ValueError(
                    f"conflicts.order names '{r.principle}', not a principle"
                )
        return self


MODEL = Vision


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _item(prefix: str, text: str) -> str:
    """A list item: continuation lines indented under its text, blank lines kept blank."""
    lines = text.split("\n")
    pad = " " * len(prefix)
    return prefix + "\n".join([lines[0]] + [pad + ln if ln else "" for ln in lines[1:]])


def render(doc: Vision, source: str) -> str:
    """The vision in the vision/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    i = doc.identity
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
        "# Vision",
        "",
        "## Identity",
        "",
        f"{i.name} is {i.sentence}",
        "",
        "It is:",
        "",
        *[_item("- ", f"**{t.trait}.** {t.meaning}") for t in i.is_],
        "",
        "It is not:",
        "",
        *[_item("- ", t) for t in i.is_not],
        "",
        "## Vision",
        "",
        doc.vision,
        "",
        "## Scope",
        "",
        doc.scope.text,
        "",
        f"The test: **{doc.scope.test}** {doc.scope.refuses}",
        "",
        "## Goals",
        "",
        *[
            _item(f"{n}. ", f"**{g.goal}.** {g.measure}")
            for n, g in enumerate(doc.goals, 1)
        ],
        "",
        "## Non-goals",
        "",
        *(
            [_item("- ", f"**{g.thing}.** {g.reason}") for g in doc.non_goals]
            or ["None"]
        ),
        "",
        "## Principles",
    ]
    for n, p in enumerate(doc.principles, 1):
        out += ["", f"### {n}. {p.name}", "", p.rule, f"**Ask:** {p.ask}"]
    out += ["", "## When principles conflict", ""]
    out += [
        _item(f"{n}. ", f"**{r.principle}.** {r.protects}")
        for n, r in enumerate(doc.conflicts.order, 1)
    ]
    out += ["", doc.conflicts.example, "", "## Where the repo does not match yet", ""]
    out += [_item("- ", g) for g in doc.gaps] or [
        f"No known gaps as of {doc.updated.isoformat()}."
    ]
    for s in doc.extra_sections:
        out += ["", f"## {s.title}", "", s.body]
    out += [
        "",
        "## Changing this file",
        "",
        doc.changing,
        "",
        "<!-- prettier-ignore-end -->",
    ]
    return "\n".join(out) + "\n"
