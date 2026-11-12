"""repeat-mistake/v2: the repeat-mistake report's model and its Markdown renderer.

The format in code, per repeat-mistake-schema.md beside this file: `artifact.py` validates a
`<YYYYMMDD-HHMMSS>-<session-id>-repeat-mistake.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the
`repeat-mistake/v1` layout.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from typing import Annotated, Literal, Optional

import yaml
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

NAME = "repeat-mistake"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]


def _not_blank(text: str) -> str:
    # Evidence and drafts are kept as written, code fences included: checked, never stripped.
    if not text.strip():
        raise ValueError("is empty or only whitespace")
    return text


Text = Annotated[str, AfterValidator(_not_blank)]
Status = Literal["applied", "awaiting approval", "rejected"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Fix(_Strict):
    id: int = Field(ge=1)
    mistake: Line
    evidence: Text
    rung: int = Field(ge=1, le=5)
    fix: Text
    proof: Literal["yes", "not provable"]
    status: Status
    why_rung: Text
    draft: Optional[Text] = None

    @model_validator(mode="after")
    def _rules(self):
        if self.status == "awaiting approval" and self.draft is None:
            raise ValueError(f"fix {self.id}: awaiting approval needs its full draft")
        if self.rung == 5 and self.proof != "not provable":
            raise ValueError(
                f"fix {self.id}: rung 5 is written guidance, so its proof is 'not provable'"
            )
        return self


class RepeatMistake(_Strict):
    schema_: Literal["repeat-mistake/v2"] = Field(alias="schema")
    date: dt.date
    other_file: Optional[Line]
    fixes: list[Fix] = Field(min_length=1)
    notes: Optional[Text] = None

    @model_validator(mode="after")
    def _ids(self):
        ids = [f.id for f in self.fixes]
        if dupes := sorted({i for i in ids if ids.count(i) > 1}):
            raise ValueError(f"fix ids repeat: {dupes}")
        return self


MODEL = RepeatMistake


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _cell(text: str) -> str:
    """A table cell: a bare `|` would split the row and a line break would end it."""
    text = re.sub(r"(?<!\\)\|", r"\\|", text.strip())
    return re.sub(r"\s*\n\s*", "<br>", text)


def _block(text: str) -> str:
    return text.rstrip("\n")


def _drafts(fixes: list[Fix], label: bool) -> list[str]:
    out = []
    for f in fixes:
        head = f"### {f.id}: {f.mistake}" + (f" ({f.status})" if label else "")
        out += [head, "", _block(f.draft), ""]
    return out


def render(doc: RepeatMistake, source: str) -> str:
    """The report in the repeat-mistake/v1 layout, titled from `date`, never the clock."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    # The other report's Markdown: its YAML path with the suffix swapped.
    other = re.sub(r"\.yaml$", ".md", doc.other_file) if doc.other_file else "none"
    day = doc.date.isoformat()
    pending = [f for f in doc.fixes if f.status == "awaiting approval"]
    previous = [f for f in doc.fixes if f.status != "awaiting approval" and f.draft]
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        f"date: {day}",
        _key("other_file", other),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Repeat mistakes — {day}",
        "",
    ]
    if doc.notes:
        out += ["## Context", "", _block(doc.notes), ""]
    out += [
        "| # | Mistake | Evidence | Rung | Fix | Proof | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        *(
            f"| {f.id} | {_cell(f.mistake)} | {_cell(f.evidence)} | {f.rung} | "
            f"{_cell(f.fix)} | {f.proof} | {f.status} |"
            for f in doc.fixes
        ),
        "",
        "## Why this rung",
        "",
        *(
            f"- {f.id}, {f.mistake}: {_block(f.why_rung).replace(chr(10), chr(10) + '  ')}"
            for f in doc.fixes
        ),
        "",
        "## Pending drafts",
        "",
        *(_drafts(pending, False) or ["None.", ""]),
    ]
    if previous:
        out += ["## Previous drafts", "", *_drafts(previous, True)]
    out.append("<!-- prettier-ignore-end -->")
    return "\n".join(out) + "\n"
