"""fix-record/v3: the fix record's model and its Markdown renderer.

The format in code, per fix-record-schema.md beside this file: `artifact.py` validates a
`.agents_workspace/product/fix/<YYYYMMDD-HHMMSS>-<slug>.yaml` with `MODEL` and writes
`render(doc, source)` beside it. Copied word for word into every skill that holds
fix-record-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "fix-record"
VERSION = 3

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
# The workspace path, or the old root form a record saved before 2026-11-14 holds, and the
# plural folder names a record saved before 2026-11-16 holds.
PlanPath = Annotated[
    str, StringConstraints(pattern=r"^(\.agents_workspace/)?product/plans?/\S+$")
]
# The earlier record's .yaml (v2, v3) or .md (v1).
FixPath = Annotated[
    str,
    StringConstraints(
        pattern=r"^(\.agents_workspace/)?product/fix(es)?/\S+\.(yaml|md)$"
    ),
]
Status = Literal["diagnosed", "fixed", "unreproduced", "declined"]


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


class Issue(_Strict):
    title: Line
    status: Status
    symptom: Symptom
    diagnosis: Diagnosis
    cause: Optional[Cause] = None
    prediction: list[Prediction]
    fix: Optional[Text] = None
    tests: list[Test]
    unverified: Text

    @model_validator(mode="after")
    def _status(self) -> Issue:
        """The Sections-by-status rules, per issue. Moving forward only compares a record with its
        history, so it stays prose."""
        rows = self.diagnosis.rows or []
        confirmed = any(r.result == "confirmed" for r in rows)
        s = self.status
        if self.diagnosis.known_from_report is not None and s != "fixed":
            raise ValueError(
                f"diagnosis.known_from_report: only a fixed issue skips the investigation, not a {s} one"
            )
        if s in ("diagnosed", "fixed", "declined"):
            if self.cause is None:
                raise ValueError(f"cause: a {s} issue names its cause")
            if self.diagnosis.rows is not None and not confirmed:
                raise ValueError(
                    f"diagnosis.rows: a {s} issue needs a confirmed hypothesis"
                )
        if s in ("diagnosed", "declined") and self.fix is not None:
            raise ValueError(f"fix: a {s} issue has no fix here, set status: fixed")
        if s in ("diagnosed", "declined") and self.tests:
            raise ValueError(f"tests: a {s} issue has no tests here, set status: fixed")
        if s == "fixed" and self.fix is None:
            raise ValueError("fix: a fixed issue says what changed")
        if s == "fixed" and not self.tests:
            raise ValueError("tests: a fixed issue names at least one regression test")
        if s == "unreproduced":
            if confirmed:
                raise ValueError(
                    "diagnosis.rows: an unreproduced issue has no confirmed hypothesis"
                )
            for key in ("cause", "fix"):
                if getattr(self, key) is not None:
                    raise ValueError(f"{key}: an unreproduced issue has none")
            for key in ("prediction", "tests"):
                if getattr(self, key):
                    raise ValueError(f"{key}: an unreproduced issue has none, use []")
        return self


def record_status(issues: list[Issue]) -> str:
    """diagnosed while any issue is, else fixed, else declined, else unreproduced."""
    found = {i.status for i in issues}
    return next(
        s for s in ("diagnosed", "fixed", "declined", "unreproduced") if s in found
    )


class FixRecord(_Strict):
    schema_: Literal["fix-record/v3"] = Field(alias="schema")
    status: Status
    date: dt.date
    issue: Optional[Line] = None
    plan: Optional[PlanPath] = None
    previous: Optional[FixPath] = None
    title: Line
    issues: list[Issue] = Field(min_length=1)

    @model_validator(mode="after")
    def _derived(self) -> FixRecord:
        want = record_status(self.issues)
        if self.status != want:
            raise ValueError(f"status: the issues make this record {want}")
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
    return text.replace("\\|", "&#92;|").replace("|", "\\|")


def _run(command: Optional[str], result: str) -> str:
    return f"`{command}` → {result}" if command else result


def _issue(n: int, i: Issue) -> list[str]:
    out = [
        f"## {n}. {i.title}",
        "",
        f"**Status:** {i.status}",
        "",
        f"**Symptom:** {_run(i.symptom.command, i.symptom.output)}",
        "",
        "### Diagnosis",
        "",
    ]
    if i.diagnosis.rows is None:
        out.append(f"Cause known from the report: {i.diagnosis.known_from_report}")
    else:
        out += ["| Hypothesis | Refuted by | Result |", "| --- | --- | --- |"]
        out += [
            f"| {_cell(r.hypothesis)} | {_cell(r.refuted_by)} | {r.result}: {_cell(r.output)} |"
            for r in i.diagnosis.rows
        ]
    if i.cause:
        out += ["", f"**Cause:** {i.cause.location}: {i.cause.chain}"]
    if i.prediction:
        runs = (_run(p.command, p.result).rstrip(".") + "." for p in i.prediction)
        out += ["", "**Prediction:** " + " ".join(runs)]
    if i.fix:
        out += ["", "### Fix", "", i.fix, "", "**Tests:**", ""]
        out += [
            f"- `{t.test}` — protects: {t.protects}; fails_when: {t.fails_when}; why_new: {t.why_new}"
            for t in i.tests
        ]
    return out + ["", f"**Unverified:** {i.unverified}", ""]


def render(doc: FixRecord, source: str) -> str:
    """The record as Markdown, one numbered section per issue. The same YAML always renders to
    the same text."""
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
    out += ["---", "", "<!-- prettier-ignore-start -->", "", f"# {doc.title}", ""]
    for n, i in enumerate(doc.issues, 1):
        out += _issue(n, i)
    out.append("<!-- prettier-ignore-end -->")
    return "\n".join(out) + "\n"
