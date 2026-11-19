"""general-audit/v1: the general audit's model and its Markdown renderer.

The format in code, per general-audit-schema.md beside this file: `artifact.py` validates a
`<YYYYMMDD-HHMMSS>-<session-id>-<target>.yaml` with `MODEL` and writes `render(doc, source)`
beside it. Each run writes a new file, never edited after.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "general-audit"
VERSION = 1

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
# A path, optionally followed by :<line>.
Location = Annotated[str, StringConstraints(pattern=r"^\S+?(:\d+)?$")]
RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Finding(_Strict):
    severity: Literal["HIGH", "MEDIUM", "LOW"]
    location: Location
    finding: Line


class GeneralAudit(_Strict):
    schema_: Literal["general-audit/v1"] = Field(alias="schema")
    date: dt.date
    target: Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")]
    subject: list[Line] = Field(min_length=1)
    criteria: list[Line] = Field(min_length=1)
    summary: Text
    findings: list[Finding]
    not_covered: list[Line]

    @model_validator(mode="after")
    def _worst_first(self) -> GeneralAudit:
        ranks = [RANK[f.severity] for f in self.findings]
        if ranks != sorted(ranks):
            raise ValueError(
                "findings: order them worst first, HIGH, then MEDIUM, then LOW"
            )
        return self


MODEL = GeneralAudit


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def render(doc: GeneralAudit, source: str) -> str:
    """The audit: what was audited against what, the summary, the findings worst first, and what
    was not covered. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("target", doc.target),
        f"date: {doc.date.isoformat()}",
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Audit: {doc.target}",
        "",
        "## Subject",
        "",
        *(f"- `{s}`" for s in doc.subject),
        "",
        "## Criteria",
        "",
        *(f"- {c}" for c in doc.criteria),
        "",
        "## Summary",
        "",
        doc.summary,
        "",
        "## Findings",
        "",
        *(f"- {f.severity} `{f.location}` {f.finding}" for f in doc.findings),
        *([] if doc.findings else ["None"]),
        "",
        "## Not covered",
        "",
        *(f"- {x}" for x in doc.not_covered),
        *([] if doc.not_covered else ["None"]),
        "",
        "<!-- prettier-ignore-end -->",
    ]
    return "\n".join(out) + "\n"
