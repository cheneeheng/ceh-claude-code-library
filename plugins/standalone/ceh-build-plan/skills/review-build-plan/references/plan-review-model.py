"""plan-review/v2: the plan review's model and its Markdown renderer.

The format in code, per plan-review-schema.md beside this file: `artifact.py` validates a
`<YYYYMMDD-HHMMSS>-<session-id>-<slug>.yaml` with `MODEL` and writes `render(doc, source)` beside
it, in the `plan-review/v1` layout.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "plan-review"
VERSION = 2

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Skipped(_Strict):
    lens: Line
    reason: Line


class Finding(_Strict):
    lens: Line
    severity: Literal["blocking", "advisory"]
    plan_line: Line
    finding: Line
    fix: Line


class Question(_Strict):
    question: Line
    recommended: Line


class Unverified(_Strict):
    finding: Line
    why: Line


class PlanReview(_Strict):
    schema_: Literal["plan-review/v2"] = Field(alias="schema")
    plan: Line
    date: dt.date
    verdict: Literal["Ready to build", "Revise first", "Rethink"]
    lenses: list[Line] = Field(min_length=1)
    skipped: list[Skipped]
    findings: list[Finding]
    questions: list[Question]
    unverified: list[Unverified]
    # Fix mode only: null outside it, and the section is left out.
    fixes_made: Optional[list[Line]] = None

    @model_validator(mode="after")
    def _verdict(self):
        blocking = any(f.severity == "blocking" for f in self.findings)
        if self.verdict == "Ready to build" and blocking:
            raise ValueError("verdict Ready to build allows no blocking finding")
        if self.verdict == "Revise first" and not blocking:
            raise ValueError("verdict Revise first needs a blocking finding")
        return self


MODEL = PlanReview


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _cell(text: str) -> str:
    return text.replace("\\|", "&#92;|").replace("|", "\\|")


def _stop(text: str) -> str:
    return text if text[-1] in ".!?" else text + "."


def render(doc: PlanReview, source: str) -> str:
    """The review in the plan-review/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    lenses = _stop(", ".join(doc.lenses)) + "".join(
        f" Skipped {s.lens}: {_stop(s.reason)}" for s in doc.skipped
    )
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("plan", doc.plan),
        f"date: {doc.date.isoformat()}",
        _key("verdict", doc.verdict),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"## Plan review: {doc.plan}",
        "",
        f"**Verdict:** {doc.verdict}",
        f"**Lenses:** {lenses}",
        "",
    ]
    if doc.findings:
        out += [
            "| # | Lens | Severity | Plan line | Finding | Fix |",
            "| --- | --- | --- | --- | --- | --- |",
            *(
                f"| {n} | {_cell(f.lens)} | {f.severity} | {_cell(f.plan_line)} | "
                f"{_cell(f.finding)} | {_cell(f.fix)} |"
                for n, f in enumerate(doc.findings, 1)
            ),
        ]
    else:
        out.append("No findings.")
    out += ["", "## Questions for the owner", ""]
    out += [f"- {q.question} Recommended: {q.recommended}" for q in doc.questions] or [
        "None"
    ]
    out += ["", "## Unverified", ""]
    out += [f"- {u.finding}: {u.why}" for u in doc.unverified] or ["None"]
    if doc.fixes_made is not None:
        out += ["", "## Fixes made", ""]
        out += [f"- {f}" for f in doc.fixes_made] or ["None"]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
