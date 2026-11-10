"""strategy/v2: the strategy document's model and its Markdown renderer.

The format in code, per strategy-schema.md beside this file: `artifact.py` validates a
`STRATEGY.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the `strategy/v1`
layout. Copied word for word into every skill that holds strategy-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "strategy"
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


class Parts(_Strict):
    columns: list[Line] = Field(min_length=2)
    rows: list[list[Line]] = Field(min_length=1)

    @model_validator(mode="after")
    def _rows_fit(self) -> Parts:
        for n, row in enumerate(self.rows):
            if len(row) != len(self.columns):
                raise ValueError(
                    f"row {n} has {len(row)} cells, columns has {len(self.columns)}"
                )
        return self


class Next(_Strict):
    work: Line
    why: Text


class Work(_Strict):
    rule: Line
    reason: Text
    next: list[Next] = Field(min_length=1)


class Rejected(_Strict):
    approach: Line
    reason: Text


class OpenItem(_Strict):
    question: Line
    assumption: Text


class Section(_Strict):
    title: Line
    body: Text


class Strategy(_Strict):
    schema_: Literal["strategy/v2"] = Field(alias="schema")
    status: Literal["draft", "adopted"]
    updated: dt.date
    concept: Text
    parts: Parts
    work: Work
    measuring: Text
    not_to_do: list[Rejected]
    gaps: list[Text]
    open: list[OpenItem]
    extra_sections: list[Section]
    changing: Text

    @model_validator(mode="after")
    def _adopted_has_no_assumption(self) -> Strategy:
        if self.status == "adopted" and any(
            "[assumed]" in s for s in _strings(self.model_dump())
        ):
            raise ValueError("status adopted allows no [assumed], set draft")
        return self


MODEL = Strategy


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


def _row(cells: list[str]) -> str:
    return "| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |"


def render(doc: Strategy, source: str) -> str:
    """The strategy in the strategy/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
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
        "# Strategy",
        "",
        "## The concept",
        "",
        doc.concept,
        "",
        "## The parts",
        "",
        _row(doc.parts.columns),
        _row(["---"] * len(doc.parts.columns)),
        *[_row(r) for r in doc.parts.rows],
        "",
        "## How work is chosen",
        "",
        f"**{doc.work.rule}** {doc.work.reason}",
        "",
        "The likely order next:",
        "",
        *[
            _item(f"{n}. ", f"**{w.work}.** {w.why}")
            for n, w in enumerate(doc.work.next, 1)
        ],
        "",
        "## Measuring progress",
        "",
        doc.measuring,
        "",
        "## What not to do",
        "",
        *(
            [_item("- ", f"**{r.approach}.** {r.reason}") for r in doc.not_to_do]
            or ["None"]
        ),
        "",
        "## Where the repo does not match yet",
        "",
        *(
            [_item("- ", g) for g in doc.gaps]
            or [f"No known gaps as of {doc.updated.isoformat()}."]
        ),
        "",
        "## Open questions",
        "",
        *(
            [_item("- ", f"**{o.question}.** {o.assumption}") for o in doc.open]
            or ["None"]
        ),
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
