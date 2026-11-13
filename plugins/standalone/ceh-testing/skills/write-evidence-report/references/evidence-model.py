"""evidence/v2: the evidence report's model and its Markdown renderer.

The format in code, per evidence-schema.md beside this file: `artifact.py` validates an
`EVIDENCE.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the `evidence/v1`
layout. Copied word for word into every skill that holds evidence-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "evidence"
VERSION = 2

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
AreaKey = Literal["tests", "qa", "performance", "security", "usability", "plan"]
# Display names in the template's row order.
AREAS = {
    "tests": "Tests",
    "qa": "QA",
    "performance": "Performance",
    "security": "Security",
    "usability": "Usability",
    "plan": "Plan",
}
Status = Annotated[
    str, StringConstraints(pattern=r"^(passed|open issues|stale \(\d+\)|not run)$")
]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Area(_Strict):
    status: Status
    result: Optional[Line] = None
    checked_at: Optional[Line] = None

    @model_validator(mode="after")
    def _filled_unless_not_run(self) -> Area:
        filled = self.result is not None and self.checked_at is not None
        if self.status != "not run" and not filled:
            raise ValueError(
                "result and checked_at are required unless status is not run"
            )
        return self


class TestsArea(Area):
    status: Literal["passed", "failed", "not run"]


class Areas(_Strict):
    tests: TestsArea
    qa: Area
    performance: Area
    security: Area
    usability: Area
    plan: Area


class Issue(_Strict):
    area: AreaKey
    issue: Text
    severity: Optional[Line] = None


class Claim(_Strict):
    claim: Text
    area: AreaKey
    figure: Line


class NotRun(_Strict):
    area: AreaKey
    reason: Text
    skill: Line


class Run(_Strict):
    date: dt.date
    sha: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{7,40}$")]
    tree: Annotated[str, StringConstraints(pattern=r"^(clean|dirty \(\d+ files\))$")]
    areas: Areas
    open_issues: list[Issue]
    claims: list[Claim]
    not_run: list[NotRun]

    @model_validator(mode="after")
    def _not_run_listed(self) -> Run:
        listed = {n.area for n in self.not_run}
        for key in AREAS:
            if getattr(self.areas, key).status == "not run" and key not in listed:
                raise ValueError(f"area {key} is not run but has no not_run entry")
        return self


class Evidence(_Strict):
    schema_: Literal["evidence/v2"] = Field(alias="schema")
    product: Line
    runs: list[Run] = Field(min_length=1)

    @model_validator(mode="after")
    def _newest_first(self) -> Evidence:
        dates = [r.date for r in self.runs]
        if dates != sorted(dates, reverse=True):
            raise ValueError("runs must be newest first")
        return self


MODEL = Evidence


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _bullet(text: str) -> str:
    lines = text.split("\n")
    return "- " + "\n".join([lines[0]] + [f"  {ln}" if ln else "" for ln in lines[1:]])


def _cell(text: Optional[str]) -> str:
    return (text or "").replace("\\|", "&#92;|").replace("|", "\\|")


def render(doc: Evidence, source: str) -> str:
    """The report in the evidence/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("product", doc.product),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Evidence: {doc.product}",
    ]
    for r in doc.runs:
        out += [
            "",
            f"## {r.date.isoformat()} at {r.sha}",
            "",
            f"**Tree:** {r.tree}",
            "",
        ]
        out += ["| Area | Status | Result | Checked at |", "| --- | --- | --- | --- |"]
        for key, name in AREAS.items():
            a = getattr(r.areas, key)
            out.append(
                f"| {name} | {a.status} | {_cell(a.result)} | {_cell(a.checked_at)} |"
            )
        out += ["", "### Open issues", ""]
        out += [
            _bullet(
                f"{AREAS[i.area]}: {i.issue}"
                + (f" ({i.severity})" if i.severity else "")
            )
            for i in r.open_issues
        ] or ["None"]
        out += ["", "### Claims", ""]
        out += [
            _bullet(f"{c.claim} ({AREAS[c.area]}, {c.figure})") for c in r.claims
        ] or ["None"]
        out += ["", "### Not run", ""]
        out += [
            _bullet(f"{AREAS[n.area]}: {n.reason}, {n.skill}") for n in r.not_run
        ] or ["None"]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
