"""error-messages-audit/v2: the error-messages audit's model and its Markdown renderer.

The format in code, per error-messages-audit-schema.md beside this file: `artifact.py` validates an
`ERROR_MESSAGES.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the
`error-messages-audit/v1` layout. Copied word for word into every skill that holds
error-messages-audit-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "error-messages-audit"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
# write-evidence-report runs `git log <commit>..HEAD` on it, so a name such as HEAD is refused.
Commit = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{7,40}$")]
Count = Annotated[int, Field(ge=0)]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Row(_Strict):
    location: Line
    current: Line
    checks: list[bool] = Field(min_length=3, max_length=3)
    severity: Literal["Blocker", "Detour", "Friction", "Polish"]
    rewrite: Line
    applied: bool
    reason: Optional[Line] = None

    @model_validator(mode="after")
    def _reason(self) -> Row:
        if self.applied == (self.reason is not None):
            raise ValueError("reason is required exactly when applied is false")
        return self


class Systemic(_Strict):
    handler: Line
    rows: list[Annotated[int, Field(ge=1)]] = Field(min_length=1)
    fixed: bool


class ErrorMessagesAudit(_Strict):
    schema_: Literal["error-messages-audit/v2"] = Field(alias="schema")
    target: Line
    run: Annotated[int, Field(ge=1)]
    date: dt.date
    commit: Commit
    harvested: Count
    already_complete: Count
    rows: list[Row]
    systemic: list[Systemic]

    @model_validator(mode="after")
    def _counts(self) -> ErrorMessagesAudit:
        if self.already_complete > self.harvested:
            raise ValueError("already_complete must not exceed harvested")
        for n, s in enumerate(self.systemic):
            missing = [r for r in s.rows if r > len(self.rows)]
            if missing:
                raise ValueError(
                    f"systemic.{n}.rows names row {missing[0]}, past the {len(self.rows)} rows"
                )
        return self


MODEL = ErrorMessagesAudit


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _cell(text: str) -> str:
    return text.replace("\\|", "&#92;|").replace("|", "\\|")


def render(doc: ErrorMessagesAudit, source: str) -> str:
    """The report in the error-messages-audit/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("target", doc.target),
        f"run: {doc.run:03d}",
        f"date: {doc.date.isoformat()}",
        _key("commit", doc.commit),
        f"harvested: {doc.harvested}",
        f"already_complete: {doc.already_complete}",
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Error messages — {doc.target}, run {doc.run:03d}",
        "",
        f"**Messages harvested:** {doc.harvested}",
        f"**Complete before rewriting:** {doc.already_complete} of {doc.harvested}",
        "",
        "## Triage",
        "",
    ]
    if doc.rows:
        out += [
            "| # | Location | Current text | 1 | 2 | 3 | Severity | Rewrite | Applied |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for n, r in enumerate(doc.rows, 1):
            marks = " | ".join("✓" if c else "✗" for c in r.checks)
            applied = "yes" if r.applied else f"no: {_cell(r.reason)}"
            out.append(
                f"| {n} | `{_cell(r.location)}` | `{_cell(r.current)}` | {marks} | {r.severity}"
                f" | `{_cell(r.rewrite)}` | {applied} |"
            )
    else:
        out.append("None")
    out += ["", "## Systemic causes", ""]
    out += [
        f"- {s.handler}: rows {', '.join(str(r) for r in s.rows)}, "
        + ("fixed once" if s.fixed else "not fixed")
        for s in doc.systemic
    ] or ["None"]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
