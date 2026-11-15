"""investor-outreach/v2: the investor outreach notes' model and their Markdown renderer.

The format in code, per investor-outreach-schema.md beside this file: `artifact.py` validates an
`INVESTOR_OUTREACH.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the
`investor-outreach/v1` layout.
"""

from __future__ import annotations

import json
from typing import Annotated, Literal

import yaml
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

NAME = "investor-outreach"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]


def _short(text: str) -> str:
    if not text.strip():
        raise ValueError("is empty or only whitespace")
    if (n := len(text.split())) > 120:
        raise ValueError(f"is {n} words, at most 120")
    return text


# The email body is kept as written, line breaks included, for pasting.
Body = Annotated[str, AfterValidator(_short)]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Fit(_Strict):
    stage: Line
    cheque: Line
    sector: Line
    thesis: Line


class Email(_Strict):
    subject: Line
    body: Body


class InvestorOutreach(_Strict):
    schema_: Literal["investor-outreach/v2"] = Field(alias="schema")
    plan: Line
    pmf_gate: int = Field(ge=0, le=8)
    draft: bool
    fit: Fit
    investors: list[Line]
    email: Email
    follow_up: Line

    @model_validator(mode="after")
    def _draft(self):
        if self.pmf_gate < 8 and not self.draft:
            raise ValueError(f"pmf_gate {self.pmf_gate}/8 needs draft: true")
        return self


MODEL = InvestorOutreach


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def render(doc: InvestorOutreach, source: str) -> str:
    """The notes in the investor-outreach/v1 layout. The same YAML renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    f = doc.fit
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("plan", doc.plan),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
    ]
    if doc.draft:
        out += [f"Draft: gate {doc.pmf_gate}/8", ""]
    out += [
        "# Investor outreach",
        "",
        f"**Fit:** {f.stage}, {f.cheque}, {f.sector}, {f.thesis}",
        f"**Investors:** {', '.join(doc.investors) or 'none supplied'}",
        "",
        "**Email**",
        "",
        f"Subject: {doc.email.subject}",
        "",
        doc.email.body.strip("\n"),
        "",
        f"**Follow-up** (two weeks later): {doc.follow_up}",
        "",
        "<!-- prettier-ignore-end -->",
    ]
    return "\n".join(out) + "\n"
