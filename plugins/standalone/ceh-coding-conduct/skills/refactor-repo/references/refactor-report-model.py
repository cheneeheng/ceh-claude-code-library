"""refactor-report/v2: the refactor report's model and its Markdown renderer.

The format in code, per refactor-report-schema.md beside this file: `artifact.py` validates a
`<YYYYMMDD-HHMMSS>-<session-id>-refactor.yaml` with `MODEL` and writes `render(doc, source)`
beside it, in the `refactor-report/v1` layout.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NAME = "refactor-report"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
Commit = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{7,40}$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Applied(_Strict):
    candidate: Line
    before: Line
    after: Line


class Skipped(_Strict):
    candidate: Line
    reason: Literal["coverage", "size", "risk"]
    note: Line


class Bug(_Strict):
    location: Line
    bug: Line


class Cluster(_Strict):
    name: Line
    applied: list[Applied]
    skipped: list[Skipped]
    bugs: list[Bug]


class RefactorReport(_Strict):
    schema_: Literal["refactor-report/v2"] = Field(alias="schema")
    date: dt.date
    commit: Commit
    clusters: list[Cluster] = Field(min_length=1)


MODEL = RefactorReport


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _cell(text: str) -> str:
    return text.replace("\\|", "&#92;|").replace("|", "\\|")


def _cluster(c: Cluster) -> list[str]:
    out = [f"## {c.name}", "", "**Applied:**", ""]
    if c.applied:
        out += [
            "| Candidate | Before (`git diff --stat`) | After |",
            "| --- | --- | --- |",
            *(
                f"| {_cell(a.candidate)} | {_cell(a.before)} | {_cell(a.after)} |"
                for a in c.applied
            ),
        ]
    else:
        out.append("None")
    out += ["", "**Skipped:**", ""]
    if c.skipped:
        out += [
            "| Candidate | Reason |",
            "| --- | --- |",
            *(
                f"| {_cell(s.candidate)} | {s.reason}: {_cell(s.note)} |"
                for s in c.skipped
            ),
        ]
    else:
        out.append("None")
    bugs = "; ".join(f"`{b.location}`: {b.bug}" for b in c.bugs) or "none"
    return out + ["", f"**Bugs found, not fixed:** {bugs}", ""]


def render(doc: RefactorReport, source: str) -> str:
    """The report in the refactor-report/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        f"date: {doc.date.isoformat()}",
        _key("commit", doc.commit),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        "# Refactor report",
        "",
    ]
    for c in doc.clusters:
        out += _cluster(c)
    out.append("<!-- prettier-ignore-end -->")
    return "\n".join(out) + "\n"
