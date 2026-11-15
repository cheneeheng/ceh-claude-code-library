"""test-audit/v2: the test suite audit's model and its Markdown renderer.

The format in code, per test-audit-schema.md beside this file: `artifact.py` validates a
`<YYYYMMDD-HHMMSS>-<session-id>-test-audit.yaml` with `MODEL` and writes `render(doc, source)`
beside it, in the `test-audit/v1` layout.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "test-audit"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
Commit = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{7,40}$")]
SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW")


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Finding(_Strict):
    severity: Literal[SEVERITIES]
    # A path:line, or the module, for a mutation result.
    location: Annotated[str, StringConstraints(pattern=r"^\S+$")]
    finding: Line


class Fix(_Strict):
    fix: Line
    closes: Line


class Decision(_Strict):
    finding: Line
    options: Line


class Command(_Strict):
    command: Line
    verdict: Line


class TestAudit(_Strict):
    schema_: Literal["test-audit/v2"] = Field(alias="schema")
    date: dt.date
    commit: Commit
    mode: Literal["fix", "report-only"]
    findings: list[Finding]
    # Fix mode only: null in report-only mode, and the section is left out.
    fixed: Optional[list[Fix]]
    needs_decision: list[Decision]
    unverified: list[Line]
    commands: list[Command] = Field(min_length=1)

    @model_validator(mode="after")
    def _rules(self):
        if (self.mode == "fix") != (self.fixed is not None):
            raise ValueError("fixed is a list in fix mode and null in report-only mode")
        ranks = [SEVERITIES.index(f.severity) for f in self.findings]
        if ranks != sorted(ranks):
            raise ValueError(
                "findings must run worst first: CRITICAL, HIGH, MEDIUM, LOW"
            )
        return self


MODEL = TestAudit


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def render(doc: TestAudit, source: str) -> str:
    """The report in the test-audit/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        f"date: {doc.date.isoformat()}",
        _key("commit", doc.commit),
        _key("mode", doc.mode),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        "# Test suite audit",
        "",
        "## Findings",
        "",
    ]
    if doc.findings:
        width = max(len(f.location) for f in doc.findings)
        out += [
            "```",
            *(
                f"{f.severity:<9} {f.location:<{width}}  {f.finding}"
                for f in doc.findings
            ),
            "```",
        ]
    else:
        out.append("None")
    if doc.fixed is not None:
        out += ["", "## Fixed", ""]
        out += [f"- {f.fix}: closes {f.closes}" for f in doc.fixed] or ["None"]
    out += ["", "## Needs a decision", ""]
    out += [f"- {d.finding}: {d.options}" for d in doc.needs_decision] or ["None"]
    out += ["", "## Unverified", ""]
    out += [f"- {u}" for u in doc.unverified] or ["None"]
    out += ["", "## Commands run", ""]
    out += [f"- `{c.command}`: {c.verdict}" for c in doc.commands]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
