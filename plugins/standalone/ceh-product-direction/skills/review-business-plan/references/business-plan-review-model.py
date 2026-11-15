"""business-plan-review/v2: the business plan review's model and its Markdown renderer.

The format in code, per business-plan-review-schema.md beside this file: `artifact.py` validates
a `<YYYYMMDD-HHMMSS>-<session-id>-business-plan-review.yaml` with `MODEL` and writes
`render(doc, source)` beside it, in the `business-plan-review/v1` layout.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "business-plan-review"
VERSION = 2

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


class BusinessPlanReview(_Strict):
    schema_: Literal["business-plan-review/v2"] = Field(alias="schema")
    plan: Line
    product: Line
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
    def _scores(self):
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
    """The review in the business-plan-review/v1 layout. The same YAML renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    run_next = ", ".join(f"{r.skill} for {r.lens}" for r in doc.run_next) or "none"
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("plan", doc.plan),
        f"date: {doc.date.isoformat()}",
        _key("verdict", doc.verdict),
        f"score: {doc.score}/14",
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"## Business plan review: {doc.product}",
        "",
        f"**Verdict:** {doc.verdict} — {doc.verdict_reason}",
        f"**Score:** {doc.score}/14",
        f"**Headline finding:** {doc.headline_finding}",
        "",
        "| Lens | Score | Evidence from the plan | Gap |",
        "| --- | --- | --- | --- |",
        *(
            f"| {lens.lens} | {lens.score} | {_cell(lens.evidence)} | {_cell(lens.gap)} |"
            for lens in doc.lenses
        ),
        "",
        f"**A fresh owner would:** stop {doc.fresh_owner.stop}, start with {doc.fresh_owner.start}.",
        f"**Strongest part:** {doc.strongest_part.quote} — {doc.strongest_part.why}",
        f"**Run next:** {run_next}",
        "",
        "<!-- prettier-ignore-end -->",
    ]
    return "\n".join(out) + "\n"
