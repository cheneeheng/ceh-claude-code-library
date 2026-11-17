"""stress-test/v2: the stress test outcome's model and its Markdown renderer.

The format in code, per stress-test-schema.md beside this file: `artifact.py` validates a
`<YYYYMMDD-HHMMSS>-<topic>.yaml`, one file per topic that later runs update, with `MODEL` and
writes `render(doc, source)` beside it, in the `stress-test/v1` layout.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NAME = "stress-test"
VERSION = 2

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
Topic = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Decision(_Strict):
    question: Line
    answer: Line
    reason: Line


class Open(_Strict):
    question: Line
    # assumed: the recommendation taken, not confirmed. blocked: the prerequisite it waits on.
    state: Literal["assumed", "blocked"]
    detail: Line


class StressTest(_Strict):
    schema_: Literal["stress-test/v2"] = Field(alias="schema")
    date: dt.date
    topic: Topic
    plan: Text
    decisions: list[Decision]
    open: list[Open]


MODEL = StressTest


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _stop(text: str) -> str:
    return text if text[-1] in ".!?" else text + "."


def _open(o: Open) -> str:
    if o.state == "assumed":
        return f"- {o.question} — assumed {o.detail}, not confirmed"
    return f"- {o.question} — blocked on {o.detail}"


def render(doc: StressTest, source: str) -> str:
    """The outcome in the stress-test/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        f"date: {doc.date.isoformat()}",
        _key("topic", doc.topic),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        doc.plan,
        "",
        "## Decisions",
        "",
        *(
            [
                f"- {d.question} — {_stop(d.answer)} {_stop(d.reason)}"
                for d in doc.decisions
            ]
            or ["None"]
        ),
        "",
        "## Open",
        "",
        *([_open(o) for o in doc.open] or ["None"]),
        "",
        "<!-- prettier-ignore-end -->",
    ]
    return "\n".join(out) + "\n"
