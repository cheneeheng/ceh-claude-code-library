"""business-plan/v3: the business plan's model and its Markdown renderer.

The format in code, per business-plan-schema.md beside this file: `artifact.py` validates a
`BUSINESS_PLAN.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the
`business-plan/v2` layout, with every heading number and the Contents list generated. Copied word
for word into every skill that holds business-plan-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "business-plan"
VERSION = 3

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
# A section body may be empty: a v0 plan opens with the 13 headings and nothing under them.
Body = Annotated[str, StringConstraints(strip_whitespace=True)]
Owner = Literal[
    "develop-business-plan",
    "find-product-market-fit",
    "plan-go-to-market",
    "run-premortem",
    "set-operating-plan",
    "sharpen-strategy",
    "stress-test-unit-economics",
]
TITLES = {
    "executive_summary": "Executive Summary",
    "problem": "Problem",
    "target_customer": "Target Customer",
    "value_proposition": "Value Proposition",
    "solution": "Solution / Product",
    "alternatives": "Alternatives & Competition",
    "market": "Market",
    "business_model": "Business Model & Pricing",
    "go_to_market": "Go-to-Market",
    "traction": "Traction & Validation",
    "financials": "Financials",
    "risks": "Risks & Unknowns",
    "milestones": "Milestones",
}
# h2 is the section, so a subsection may nest four deep, down to h6.
MAX_DEPTH = 4


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Subsection(_Strict):
    title: Line
    owner: Owner
    body: Body
    subsections: list[Subsection]


class Section(_Strict):
    body: Body
    subsections: list[Subsection]


class Sections(_Strict):
    executive_summary: Section
    problem: Section
    target_customer: Section
    value_proposition: Section
    solution: Section
    alternatives: Section
    market: Section
    business_model: Section
    go_to_market: Section
    traction: Section
    financials: Section
    risks: Section
    milestones: Section


class BusinessPlan(_Strict):
    schema_: Literal["business-plan/v3"] = Field(alias="schema")
    status: Literal["draft", "validated"]
    created: dt.date
    updated: dt.date
    product: Line
    stage: Literal["idea", "prototype", "launched", "revenue"]
    derived_from: list[Line]
    pmf_gate: int = Field(ge=0, le=8)
    sections: Sections

    @model_validator(mode="after")
    def _rules(self) -> BusinessPlan:
        if self.updated < self.created:
            raise ValueError("updated is before created")
        if self.status == "validated" and self.pmf_gate < 8:
            raise ValueError("status validated needs pmf_gate 8, set draft")

        def depth(subs: list[Subsection], level: int, where: str) -> None:
            for s in subs:
                if level > MAX_DEPTH:
                    raise ValueError(f"{where}: '{s.title}' nests below h6")
                depth(s.subsections, level + 1, where)

        for key in TITLES:
            depth(getattr(self.sections, key).subsections, 1, f"sections.{key}")
        return self


MODEL = BusinessPlan


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def anchor(heading: str) -> str:
    """GitHub's heading anchor: lowercase, keep letters, digits, spaces, - and _, spaces to -."""
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


def render(doc: BusinessPlan, source: str) -> str:
    """The plan in the business-plan/v2 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    contents: list[str] = []
    body: list[str] = []

    def emit(
        level: int, number: str, title: str, text: str, subs: list[Subsection]
    ) -> None:
        head = f"§{number} {title}"
        contents.append(f"{'  ' * (level - 2)}- [{head}](#{anchor(head)})")
        body.extend(["", f"{'#' * level} {head}"])
        if text:
            body.extend(["", text])
        for i, s in enumerate(subs, 1):
            emit(level + 1, f"{number}.{i:02d}", s.title, s.body, s.subsections)

    for n, (key, title) in enumerate(TITLES.items(), 1):
        sec = getattr(doc.sections, key)
        emit(2, f"{n:02d}", title, sec.body, sec.subsections)
    front = [
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("status", doc.status),
        _key("created", doc.created),
        _key("updated", doc.updated),
        _key("product", doc.product),
        _key("stage", doc.stage),
        f"derived_from: {json.dumps(doc.derived_from, ensure_ascii=False)}",
        f"pmf_gate: {doc.pmf_gate}/8",
    ]
    out = [
        "---",
        *front,
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        "**Contents**",
        "",
    ]
    out += contents + body + ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
