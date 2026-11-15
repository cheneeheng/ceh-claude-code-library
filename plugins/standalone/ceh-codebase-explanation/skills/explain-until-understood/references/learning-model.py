"""learning/v2: the learning record's model and its Markdown renderer.

The format in code, per learning-schema.md beside this file: `artifact.py` validates a
`<subject>.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the `learning/v1`
layout.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "learning"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
Subject = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Term(_Strict):
    term: Line
    definition: Line


class SelfTest(_Strict):
    question: Line
    last_answer: Literal["unaided", "missed", "not asked"]
    date: Optional[dt.date]

    @model_validator(mode="after")
    def _date(self):
        if (self.last_answer == "not asked") != (self.date is None):
            raise ValueError("date is null exactly when last_answer is 'not asked'")
        return self


class Learning(_Strict):
    schema_: Literal["learning/v2"] = Field(alias="schema")
    subject: Subject
    goal: Line
    next: Line
    terms: list[Term]
    rules: list[Line]
    self_test: list[SelfTest]
    open_questions: list[Line]


MODEL = Learning


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _cell(text: str) -> str:
    return text.replace("\\|", "&#92;|").replace("|", "\\|")


def render(doc: Learning, source: str) -> str:
    """The record in the learning/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("subject", doc.subject),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Learning: {doc.subject}",
        "",
        f"**Goal:** {doc.goal}",
        f"**Next:** {doc.next}",
        "",
        "## Terms",
        "",
    ]
    if doc.terms:
        out += [
            "| Term | Definition, as the reader put it back |",
            "| --- | --- |",
            *(f"| {_cell(t.term)} | {_cell(t.definition)} |" for t in doc.terms),
        ]
    else:
        out.append("None")
    out += ["", "## Rules of thumb", ""]
    out += [f"- {r}" for r in doc.rules] or ["None"]
    out += ["", "## Self-test", ""]
    if doc.self_test:
        out += [
            "| Question | Last answer | Date |",
            "| --- | --- | --- |",
            *(
                f"| {_cell(s.question)} | {'—' if s.last_answer == 'not asked' else s.last_answer}"
                f" | {s.date.isoformat() if s.date else '—'} |"
                for s in doc.self_test
            ),
        ]
    else:
        out.append("None")
    out += ["", "## Open questions", ""]
    out += [f"- {q}" for q in doc.open_questions] or ["None"]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
