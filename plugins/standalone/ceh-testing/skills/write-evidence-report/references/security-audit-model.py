"""security-audit/v2: the security audit's model and its Markdown renderer.

The format in code, per security-audit-schema.md beside this file: `artifact.py` validates a
`SECURITY_AUDIT-<YYYYMMDD-HHMM>.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the
`security-audit/v1` layout. Copied word for word into every skill that holds
security-audit-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NAME = "security-audit"
VERSION = 2

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
# write-evidence-report runs `git log <commit>..HEAD` on it, so a name such as HEAD is refused.
Commit = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{7,40}$")]
Location = Annotated[str, StringConstraints(pattern=r"^[^\s:]+:\d+$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Finding(_Strict):
    severity: Literal["critical", "high", "medium", "low"]
    confidence: Literal["confirmed", "likely"]
    category: Line
    attacker: Line
    location: Location
    attack: Line
    fix: Line


class Possible(_Strict):
    lead: Line
    settle: Text


class NotChecked(_Strict):
    check: Line
    reason: Text
    command: Line


class SecurityAudit(_Strict):
    schema_: Literal["security-audit/v2"] = Field(alias="schema")
    repo: Line
    commit: Commit
    date: dt.date
    attack_surface: Text
    findings: list[Finding]
    possible: list[Possible]
    not_checked: list[NotChecked]


MODEL = SecurityAudit


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


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def render(doc: SecurityAudit, source: str) -> str:
    """The report in the security-audit/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    date = doc.date.isoformat()
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("repo", doc.repo),
        _key("commit", doc.commit),
        f"date: {date}",
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Security audit: {doc.repo} at {doc.commit}, {date}",
        "",
        "## Attack surface",
        "",
        doc.attack_surface,
        "",
        "## Findings",
        "",
    ]
    if doc.findings:
        out += [
            "| # | Severity | Confidence | Category | Attacker | Location | Attack | Fix |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        out += [
            f"| {n} | {f.severity} | {f.confidence} | {_cell(f.category)} | {_cell(f.attacker)}"
            f" | `{f.location}` | {_cell(f.attack)} | {_cell(f.fix)} |"
            for n, f in enumerate(doc.findings, 1)
        ]
    else:
        out.append("None")
    out += ["", "## Possible", ""]
    out += [_bullet(f"{p.lead}: {p.settle}") for p in doc.possible] or ["None"]
    out += ["", "## Not checked", ""]
    out += [
        _bullet(f"{c.check}: {c.reason}, `{c.command}`") for c in doc.not_checked
    ] or ["None"]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
