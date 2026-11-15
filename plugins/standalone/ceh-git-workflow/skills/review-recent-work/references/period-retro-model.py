"""period-retro/v3: the period retro's model and its Markdown renderer.

The format in code, per period-retro-schema.md beside this file: `artifact.py` validates a
`<YYYYMMDD-HHMMSS>-<session-id>-period.yaml` with `MODEL` and writes `render(doc, source)` beside
it, in the `period-retro/v2` layout.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "period-retro"
VERSION = 3

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Shipped(_Strict):
    group: Line
    change: Line
    refs: list[Line] = Field(min_length=1)


class Measure(_Strict):
    value: Line
    source: Line


class Flow(_Strict):
    prs_merged: Measure
    median_time_to_merge: Measure
    reverts: Measure


class Hotspot(_Strict):
    path: Line
    commits: int = Field(ge=1)


class Issue(_Strict):
    kind: Literal["Bug", "Design", "Project rule", "Agent mistake"]
    issue: Line
    evidence: Line
    route: Line
    status: Literal["handed off", "open"]
    # The artifact handed off to, or why it is open.
    status_detail: Line


class PeriodRetro(_Strict):
    schema_: Literal["period-retro/v3"] = Field(alias="schema")
    since: dt.date
    until: dt.date
    shipped: list[Shipped]
    flow: Flow
    hotspots: list[Hotspot]
    issues: list[Issue] = Field(max_length=3)
    questions: list[Line]

    @model_validator(mode="after")
    def _period(self):
        if self.since > self.until:
            raise ValueError(f"since {self.since} is after until {self.until}")
        return self


MODEL = PeriodRetro


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _cell(text: str) -> str:
    return text.replace("\\|", "&#92;|").replace("|", "\\|")


def render(doc: PeriodRetro, source: str) -> str:
    """The retro in the period-retro/v2 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    since, until = doc.since.isoformat(), doc.until.isoformat()
    f = doc.flow
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        f"since: {since}",
        f"until: {until}",
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Retro {since} to {until}",
        "",
        "## Shipped",
        "",
        *(
            [f"- {s.group}: {s.change} — {', '.join(s.refs)}" for s in doc.shipped]
            or ["None"]
        ),
        "",
        "## Flow",
        "",
        "| Measure | Value | From |",
        "| --- | --- | --- |",
        *(
            f"| {name} | {_cell(m.value)} | {_cell(m.source)} |"
            for name, m in (
                ("PRs merged", f.prs_merged),
                ("Median time to merge", f.median_time_to_merge),
                ("Reverts", f.reverts),
            )
        ),
        "",
        "Churn hotspots: "
        + (
            ", ".join(f"`{h.path}` ({h.commits} commits)" for h in doc.hotspots)
            or "none"
        ),
        "",
        "## Issues",
        "",
    ]
    for n, i in enumerate(doc.issues, 1):
        out += [
            f"### {n}. {i.kind}: {i.issue}",
            "",
            f"- **Evidence:** {i.evidence}",
            f"- **Route:** {i.route}",
            f"- **Status:** {i.status}: {i.status_detail}",
            "",
        ]
    if not doc.issues:
        out += ["None", ""]
    out += ["## Questions the history cannot answer", ""]
    out += [f"- {q}" for q in doc.questions] or ["None"]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
