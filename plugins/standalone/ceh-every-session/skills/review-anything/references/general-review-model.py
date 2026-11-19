"""general-review/v1: the general review's model and its Markdown renderer.

The format in code, per general-review-schema.md beside this file: `artifact.py` validates a
`<YYYYMMDD-HHMMSS>-<target>.yaml` with `MODEL` and writes `render(doc, source)` beside it. One file
per target holds every review round and every finding with its status.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "general-review"
VERSION = 1

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
# A path, optionally followed by :<line>.
Location = Annotated[str, StringConstraints(pattern=r"^\S+?(:\d+)?$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Round(_Strict):
    date: dt.date
    verdict: Literal["Done", "Not yet", "Cannot judge"]
    verdict_detail: Line
    summary: Text
    not_covered: list[Line]


class Finding(_Strict):
    round: int = Field(ge=1)
    location: Location
    label: Literal["blocking", "advisory", "question"]
    comment: Line
    status: Literal["open", "fixed", "won't fix"]
    # The fixing edit or commit, or why it will not be fixed.
    resolution: Optional[Line] = None

    @model_validator(mode="after")
    def _resolution(self) -> Finding:
        if (self.status == "open") != (self.resolution is None):
            raise ValueError(
                "resolution is required when status is not open, and only then"
            )
        return self


class GeneralReview(_Strict):
    schema_: Literal["general-review/v1"] = Field(alias="schema")
    target: Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")]
    subject: list[Line] = Field(min_length=1)
    criteria: list[Line] = Field(min_length=1)
    rounds: list[Round] = Field(min_length=1)
    findings: list[Finding]

    @model_validator(mode="after")
    def _rounds(self) -> GeneralReview:
        for f in self.findings:
            if f.round > len(self.rounds):
                raise ValueError(f"findings: round {f.round} does not exist")
        for n, r in enumerate(self.rounds, 1):
            blocking = sum(
                f.round == n and f.label == "blocking" for f in self.findings
            )
            if r.verdict == "Done" and blocking:
                raise ValueError(
                    f"rounds.{n - 1}: verdict Done allows no blocking finding"
                )
            if r.verdict == "Not yet" and not blocking:
                raise ValueError(
                    f"rounds.{n - 1}: verdict Not yet needs a blocking finding"
                )
        return self


MODEL = GeneralReview


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def render(doc: GeneralReview, source: str) -> str:
    """The review: the latest verdict, what was reviewed against what, every finding with its
    status, then each round. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    last = doc.rounds[-1]
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("target", doc.target),
        f"date: {last.date.isoformat()}",
        _key("verdict", last.verdict),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Review: {doc.target}",
        "",
        f"**Verdict:** {last.verdict} (round {len(doc.rounds)}) — {last.verdict_detail}",
        "",
        "## Subject",
        "",
        *(f"- `{s}`" for s in doc.subject),
        "",
        "## Criteria",
        "",
        *(f"- {c}" for c in doc.criteria),
        "",
        "## Findings",
        "",
    ]
    for f in doc.findings:
        status = f"{f.status}: {f.resolution}" if f.resolution else f.status
        out.append(
            f"- `{f.location}` [{f.label}] {f.comment} (round {f.round}, {status})"
        )
    if not doc.findings:
        out.append("None")
    for n, r in enumerate(doc.rounds, 1):
        out += ["", f"## Round {n}: {r.date.isoformat()}, {r.verdict}", ""]
        out += [f"**Verdict:** {r.verdict} — {r.verdict_detail}", "", r.summary, ""]
        if r.not_covered:
            out += ["**Not covered:**", "", *(f"- {x}" for x in r.not_covered)]
        else:
            out.append("**Not covered:** None")
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
