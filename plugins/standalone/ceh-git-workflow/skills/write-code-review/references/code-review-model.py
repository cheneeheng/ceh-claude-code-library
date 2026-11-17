"""code-review/v3: the code review's model and its Markdown renderer.

The format in code, per code-review-schema.md beside this file: `artifact.py` validates a
`<YYYYMMDD-HHMMSS>-<branch>.yaml` with `MODEL` and writes `render(doc, source)` beside it. One file
per branch holds every review round and every finding with its status.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "code-review"
VERSION = 3

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Round(_Strict):
    date: dt.date
    verdict: Literal["Approve", "Request changes", "Comment", "Cannot verify"]
    verdict_detail: Line
    summary: Text


class Finding(_Strict):
    round: int = Field(ge=1)
    location: Annotated[str, StringConstraints(pattern=r"^\S+:\d+$")]
    label: Literal["blocking", "advisory", "question"]
    comment: Line
    status: Literal["open", "fixed", "won't fix"]
    # The fixing commit, or the reply that declines it.
    resolution: Optional[Line] = None

    @model_validator(mode="after")
    def _resolution(self) -> Finding:
        if (self.status == "open") != (self.resolution is None):
            raise ValueError(
                "resolution is required when status is not open, and only then"
            )
        return self


class CodeReview(_Strict):
    schema_: Literal["code-review/v3"] = Field(alias="schema")
    branch: Line
    rounds: list[Round] = Field(min_length=1)
    findings: list[Finding]

    @model_validator(mode="after")
    def _rounds(self) -> CodeReview:
        for f in self.findings:
            if f.round > len(self.rounds):
                raise ValueError(f"findings: round {f.round} does not exist")
        for n, r in enumerate(self.rounds, 1):
            blocking = sum(
                f.round == n and f.label == "blocking" for f in self.findings
            )
            if r.verdict == "Approve" and blocking:
                raise ValueError(
                    f"rounds.{n - 1}: verdict Approve allows no blocking comment"
                )
            if r.verdict == "Request changes" and not blocking:
                raise ValueError(
                    f"rounds.{n - 1}: verdict Request changes needs a blocking comment"
                )
            if blocking > 5:
                raise ValueError(
                    f"rounds.{n - 1}: {blocking} blocking comments, at most 5"
                )
        return self


MODEL = CodeReview


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def render(doc: CodeReview, source: str) -> str:
    """The review: the latest verdict, every finding with its status, then each round. The same
    YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    last = doc.rounds[-1]
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("branch", doc.branch),
        f"date: {last.date.isoformat()}",
        _key("verdict", last.verdict),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Code review: {doc.branch}",
        "",
        f"**Verdict:** {last.verdict} (round {len(doc.rounds)}) — {last.verdict_detail}",
        "",
        "## Line comments",
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
        out += [f"**Verdict:** {r.verdict} — {r.verdict_detail}", "", r.summary]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
