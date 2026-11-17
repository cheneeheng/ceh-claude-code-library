"""business-plan-review/v3: the business plan review's model and its Markdown renderer.

The format in code, per business-plan-review-schema.md beside this file: `artifact.py` validates
a `<YYYYMMDD-HHMMSS>-business-plan-review.yaml` with `MODEL` and writes `render(doc, source)`
beside it. One file holds every review round and a finding per lens scored below 2.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "business-plan-review"
VERSION = 3

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
LENSES = ("Customer", "Edge", "Focus", "Money", "Reach", "Survival", "Execution")


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Lens(_Strict):
    lens: Literal[LENSES]
    score: int = Field(ge=0, le=2)
    evidence: Line
    gap: Line


class FreshOwner(_Strict):
    stop: Line
    start: Line


class Strongest(_Strict):
    quote: Line
    why: Line


class RunNext(_Strict):
    skill: Line
    lens: Literal[LENSES]


class Round(_Strict):
    date: dt.date
    verdict: Literal["build", "fix first", "do not build"]
    verdict_reason: Line
    score: int = Field(ge=0, le=14)
    headline_finding: Line
    lenses: list[Lens]
    fresh_owner: FreshOwner
    strongest_part: Strongest
    run_next: list[RunNext]

    @model_validator(mode="after")
    def _scores(self) -> Round:
        names = tuple(lens.lens for lens in self.lenses)
        if names != LENSES:
            raise ValueError(f"lenses must be the seven, in order: {', '.join(LENSES)}")
        total = sum(lens.score for lens in self.lenses)
        if self.score != total:
            raise ValueError(f"score {self.score} is not the lens total {total}")
        builds = all(lens.score for lens in self.lenses) and total >= 10
        if (self.verdict == "build") != builds:
            raise ValueError(
                "verdict build is exactly no lens at 0 and a total of 10 or more"
            )
        if self.verdict == "do not build" and self.lenses[0].score != 0:
            raise ValueError("verdict do not build needs Customer at 0")
        low = [lens.lens for lens in self.lenses if lens.score < 2]
        if [r.lens for r in self.run_next] != low:
            raise ValueError(
                f"run_next must name each lens below 2, in order: {', '.join(low) or 'none'}"
            )
        return self


class Finding(_Strict):
    round: int = Field(ge=1)
    lens: Literal[LENSES]
    gap: Line
    status: Literal["open", "fixed", "won't fix"]
    # The plan edit that closed the gap, or why it will not be closed.
    resolution: Optional[Line] = None

    @model_validator(mode="after")
    def _resolution(self) -> Finding:
        if (self.status == "open") != (self.resolution is None):
            raise ValueError(
                "resolution is required when status is not open, and only then"
            )
        return self


class BusinessPlanReview(_Strict):
    schema_: Literal["business-plan-review/v3"] = Field(alias="schema")
    plan: Line
    product: Line
    rounds: list[Round] = Field(min_length=1)
    findings: list[Finding]

    @model_validator(mode="after")
    def _findings(self) -> BusinessPlanReview:
        for f in self.findings:
            if f.round > len(self.rounds):
                raise ValueError(f"findings: round {f.round} does not exist")
            raised = self.rounds[f.round - 1]
            if next(x for x in raised.lenses if x.lens == f.lens).score == 2:
                raise ValueError(
                    f"findings: {f.lens} scored 2 in round {f.round}, no gap to raise"
                )
        latest = self.rounds[-1]
        still_open = {f.lens for f in self.findings if f.status == "open"}
        for lens in latest.lenses:
            if lens.score < 2 and lens.lens not in still_open:
                raise ValueError(
                    f"findings: {lens.lens} scored below 2 in the latest round and has no open finding"
                )
        return self


MODEL = BusinessPlanReview


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _cell(text: str) -> str:
    return text.replace("\\|", "&#92;|").replace("|", "\\|")


def render(doc: BusinessPlanReview, source: str) -> str:
    """The latest round in full, every finding with its status, then the earlier rounds. The same
    YAML renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    r = doc.rounds[-1]
    run_next = ", ".join(f"{x.skill} for {x.lens}" for x in r.run_next) or "none"
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("plan", doc.plan),
        f"date: {r.date.isoformat()}",
        _key("verdict", r.verdict),
        f"score: {r.score}/14",
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"## Business plan review: {doc.product}",
        "",
        f"**Verdict:** {r.verdict} (round {len(doc.rounds)}) — {r.verdict_reason}",
        f"**Score:** {r.score}/14",
        f"**Headline finding:** {r.headline_finding}",
        "",
        "| Lens | Score | Evidence from the plan | Gap |",
        "| --- | --- | --- | --- |",
        *(
            f"| {lens.lens} | {lens.score} | {_cell(lens.evidence)} | {_cell(lens.gap)} |"
            for lens in r.lenses
        ),
        "",
        f"**A fresh owner would:** stop {r.fresh_owner.stop}, start with {r.fresh_owner.start}.",
        f"**Strongest part:** {r.strongest_part.quote} — {r.strongest_part.why}",
        f"**Run next:** {run_next}",
        "",
        "## Findings",
        "",
    ]
    for f in doc.findings:
        status = f"{f.status}: {f.resolution}" if f.resolution else f.status
        out.append(f"- {f.lens} (round {f.round}): {f.gap} — {status}")
    if not doc.findings:
        out.append("None")
    if len(doc.rounds) > 1:
        out += ["", "## Earlier rounds", ""]
        out += [
            f"- Round {n}: {x.date.isoformat()}, {x.verdict}, {x.score}/14 — {x.headline_finding}"
            for n, x in enumerate(doc.rounds[:-1], 1)
        ]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
