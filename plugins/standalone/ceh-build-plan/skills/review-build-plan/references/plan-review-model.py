"""plan-review/v3: the plan review's model and its Markdown renderer.

The format in code, per plan-review-schema.md beside this file: `artifact.py` validates a
`<YYYYMMDD-HHMMSS>-<plan-slug>.yaml` with `MODEL` and writes `render(doc, source)` beside it. One
file per plan holds every review round and every finding with its status.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "plan-review"
VERSION = 3

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Skipped(_Strict):
    lens: Line
    reason: Line


class Question(_Strict):
    question: Line
    recommended: Line


class Unverified(_Strict):
    finding: Line
    why: Line


class Round(_Strict):
    date: dt.date
    verdict: Literal["Ready to build", "Revise first", "Rethink"]
    lenses: list[Line] = Field(min_length=1)
    skipped: list[Skipped]
    questions: list[Question]
    unverified: list[Unverified]
    # Fix mode only: null outside it, and the section is left out.
    fixes_made: Optional[list[Line]] = None


class Finding(_Strict):
    round: int = Field(ge=1)
    lens: Line
    severity: Literal["blocking", "advisory"]
    plan_line: Line
    finding: Line
    fix: Line
    status: Literal["open", "fixed", "won't fix"]
    # The edit, commit or PR that fixed it, or why it will not be fixed.
    resolution: Optional[Line] = None

    @model_validator(mode="after")
    def _resolution(self) -> Finding:
        if (self.status == "open") != (self.resolution is None):
            raise ValueError(
                "resolution is required when status is not open, and only then"
            )
        return self


class PlanReview(_Strict):
    schema_: Literal["plan-review/v3"] = Field(alias="schema")
    plan: Line
    rounds: list[Round] = Field(min_length=1)
    findings: list[Finding]

    @model_validator(mode="after")
    def _rounds(self) -> PlanReview:
        for f in self.findings:
            if f.round > len(self.rounds):
                raise ValueError(f"findings: round {f.round} does not exist")
        for n, r in enumerate(self.rounds, 1):
            blocking = any(
                f.round == n and f.severity == "blocking" for f in self.findings
            )
            if r.verdict == "Ready to build" and blocking:
                raise ValueError(
                    f"rounds.{n - 1}: verdict Ready to build allows no blocking finding"
                )
            if r.verdict == "Revise first" and not blocking:
                raise ValueError(
                    f"rounds.{n - 1}: verdict Revise first needs a blocking finding"
                )
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


def _status(f: Finding) -> str:
    return f"{f.status}: {_cell(f.resolution)}" if f.resolution else f.status


def render(doc: PlanReview, source: str) -> str:
    """The review: the latest verdict, every finding with its status, then each round. The same
    YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    last = doc.rounds[-1]
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("plan", doc.plan),
        f"date: {last.date.isoformat()}",
        _key("verdict", last.verdict),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"## Plan review: {doc.plan}",
        "",
        f"**Verdict:** {last.verdict} (round {len(doc.rounds)})",
        "",
    ]
    if doc.findings:
        out += [
            "| # | Round | Lens | Severity | Plan line | Finding | Fix | Status |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
            *(
                f"| {n} | {f.round} | {_cell(f.lens)} | {f.severity} | {_cell(f.plan_line)} | "
                f"{_cell(f.finding)} | {_cell(f.fix)} | {_status(f)} |"
                for n, f in enumerate(doc.findings, 1)
            ),
        ]
    else:
        out.append("No findings.")
    for n, r in enumerate(doc.rounds, 1):
        lenses = _stop(", ".join(r.lenses)) + "".join(
            f" Skipped {s.lens}: {_stop(s.reason)}" for s in r.skipped
        )
        out += ["", f"## Round {n}: {r.date.isoformat()}, {r.verdict}", ""]
        out += [f"**Lenses:** {lenses}", "", "### Questions for the owner", ""]
        out += [
            f"- {q.question} Recommended: {q.recommended}" for q in r.questions
        ] or ["None"]
        out += ["", "### Unverified", ""]
        out += [f"- {u.finding}: {u.why}" for u in r.unverified] or ["None"]
        if r.fixes_made is not None:
            out += ["", "### Fixes made", ""]
            out += [f"- {f}" for f in r.fixes_made] or ["None"]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
