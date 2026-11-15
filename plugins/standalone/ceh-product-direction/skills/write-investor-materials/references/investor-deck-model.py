"""investor-deck/v2: the investor deck outline's model and its Markdown renderer.

The format in code, per investor-deck-schema.md beside this file: `artifact.py` validates an
`INVESTOR_DECK.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the
`investor-deck/v1` layout.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "investor-deck"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Proof(_Strict):
    text: Line
    tag: Literal["evidence", "assumption", "hypothesis-to-test"]


class Slide(_Strict):
    headline: Line
    lines: list[Proof] = Field(min_length=1)
    # The plan section every line traces to, rendered §NN.
    source: int = Field(ge=1, le=99)


class InvestorDeck(_Strict):
    schema_: Literal["investor-deck/v2"] = Field(alias="schema")
    plan: Line
    pmf_gate: int = Field(ge=0, le=8)
    plan_updated: dt.date
    draft: bool
    company: Line
    one_liner: Line
    slides: list[Slide] = Field(min_length=1)

    @model_validator(mode="after")
    def _draft(self):
        if self.pmf_gate < 8 and not self.draft:
            raise ValueError(f"pmf_gate {self.pmf_gate}/8 needs draft: true")
        return self


MODEL = InvestorDeck


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def render(doc: InvestorDeck, source: str) -> str:
    """The deck in the investor-deck/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("plan", doc.plan),
        f"pmf_gate: {doc.pmf_gate}/8",
        f"plan_updated: {doc.plan_updated.isoformat()}",
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
    ]
    if doc.draft:
        out += [f"Draft: gate {doc.pmf_gate}/8", ""]
    out += [f"# {doc.company}: {doc.one_liner}", ""]
    for n, s in enumerate(doc.slides, 1):
        out += [f"## {n}. {s.headline}", ""]
        out += [f"- {p.text} [{p.tag}]" for p in s.lines]
        out += ["", f"Source: §{s.source:02d}", ""]
    out.append("<!-- prettier-ignore-end -->")
    return "\n".join(out) + "\n"
