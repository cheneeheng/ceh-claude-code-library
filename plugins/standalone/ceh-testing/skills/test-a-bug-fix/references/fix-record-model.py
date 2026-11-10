"""fix-record/v2: the fix record's model and its Markdown renderer.

The format in code, per fix-record-schema.md beside this file: `artifact.py` validates a
`product/fixes/<slug>.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the
`fix-record/v1` layout. Copied word for word into every skill that holds fix-record-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "fix-record"
VERSION = 2

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
PlanPath = Annotated[str, StringConstraints(pattern=r"^product/plans/\S+$")]
# The earlier record's .md, which exists for a v1 and a v2 record alike.
FixPath = Annotated[str, StringConstraints(pattern=r"^product/fixes/\S+\.md$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Symptom(_Strict):
    command: Optional[Line] = None
    output: Line


class Row(_Strict):
    hypothesis: Line
    refuted_by: Line
    result: Literal["refuted", "standing", "confirmed"]
    output: Line


class Diagnosis(_Strict):
    rows: Optional[list[Row]] = Field(default=None, min_length=1)
    known_from_report: Optional[Line] = None

    @model_validator(mode="after")
    def _one(self) -> Diagnosis:
        if (self.rows is None) == (self.known_from_report is None):
            raise ValueError("diagnosis needs exactly one of rows or known_from_report")
        return self


class Cause(_Strict):
    location: Line
    chain: Text


class Prediction(_Strict):
    command: Optional[Line] = None
    result: Line


class Test(_Strict):
    test: Line
    protects: Line
    fails_when: Line
    why_new: Line


class FixRecord(_Strict):
    schema_: Literal["fix-record/v2"] = Field(alias="schema")
    status: Literal["diagnosed", "fixed", "unreproduced"]
    date: dt.date
    issue: Optional[Line] = None
    plan: Optional[PlanPath] = None
    previous: Optional[FixPath] = None
    title: Line
    symptom: Symptom
    diagnosis: Diagnosis
    cause: Optional[Cause] = None
    prediction: list[Prediction]
    fix: Optional[Text] = None
    tests: list[Test]
    unverified: Text

    @model_validator(mode="after")
    def _status(self) -> FixRecord:
        """The v1 "Sections by status" rules. Moving forward only and the same-commit rule compare
        a record with its history, so they stay prose."""
        rows = self.diagnosis.rows or []
        confirmed = any(r.result == "confirmed" for r in rows)
        s = self.status
        if self.diagnosis.known_from_report is not None and s != "fixed":
            raise ValueError(
                f"diagnosis.known_from_report: only a fixed record skips the investigation, not a {s} one"
            )
        if s in ("diagnosed", "fixed"):
            if self.cause is None:
                raise ValueError(f"cause: a {s} record names its cause")
            if self.diagnosis.rows is not None and not confirmed:
                raise ValueError(
                    f"diagnosis.rows: a {s} record needs a confirmed hypothesis"
                )
        if s == "diagnosed" and self.fix is not None:
            raise ValueError(
                "fix: a diagnosed record has no fix yet, set status: fixed"
            )
        if s == "diagnosed" and self.tests:
            raise ValueError(
                "tests: a diagnosed record has no tests yet, set status: fixed"
            )
        if s == "fixed" and self.fix is None:
            raise ValueError("fix: a fixed record says what changed")
        if s == "fixed" and not self.tests:
            raise ValueError("tests: a fixed record names at least one regression test")
        if s == "unreproduced":
            if confirmed:
                raise ValueError(
                    "diagnosis.rows: an unreproduced record has no confirmed hypothesis"
                )
            for key in ("cause", "fix"):
                if getattr(self, key) is not None:
                    raise ValueError(f"{key}: an unreproduced record has none")
            for key in ("prediction", "tests"):
                if getattr(self, key):
                    raise ValueError(f"{key}: an unreproduced record has none, use []")
        return self


MODEL = FixRecord


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def _run(command: Optional[str], result: str) -> str:
    return f"`{command}` → {result}" if command else result


def render(doc: FixRecord, source: str) -> str:
    """The record in the fix-record/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("status", doc.status),
        f"date: {doc.date.isoformat()}",
    ]
    out += [
        _key(k, getattr(doc, k))
        for k in ("issue", "plan", "previous")
        if getattr(doc, k)
    ]
    out += [
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# {doc.title}",
        "",
        f"**Symptom:** {_run(doc.symptom.command, doc.symptom.output)}",
        "",
        "## Diagnosis",
        "",
    ]
    if doc.diagnosis.rows is None:
        out.append(f"Cause known from the report: {doc.diagnosis.known_from_report}")
    else:
        out += ["| Hypothesis | Refuted by | Result |", "| --- | --- | --- |"]
        out += [
            f"| {_cell(r.hypothesis)} | {_cell(r.refuted_by)} | {r.result}: {_cell(r.output)} |"
            for r in doc.diagnosis.rows
        ]
    if doc.cause:
        out += ["", f"**Cause:** {doc.cause.location}: {doc.cause.chain}"]
    if doc.prediction:
        runs = (_run(p.command, p.result).rstrip(".") + "." for p in doc.prediction)
        out += ["", "**Prediction:** " + " ".join(runs)]
    if doc.fix:
        out += ["", "## Fix", "", doc.fix, "", "**Tests:**", ""]
        out += [
            f"- `{t.test}` — protects: {t.protects}; fails_when: {t.fails_when}; why_new: {t.why_new}"
            for t in doc.tests
        ]
    out += ["", f"**Unverified:** {doc.unverified}", "", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
