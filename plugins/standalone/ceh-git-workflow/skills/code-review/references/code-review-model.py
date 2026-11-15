"""code-review/v2: the code review's model and its Markdown renderer.

The format in code, per code-review-schema.md beside this file: `artifact.py` validates a
`<YYYYMMDD-HHMMSS>-<session-id>-<branch>.yaml` with `MODEL` and writes `render(doc, source)`
beside it, in the `code-review/v1` layout.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "code-review"
VERSION = 2

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Comment(_Strict):
    location: Annotated[str, StringConstraints(pattern=r"^\S+:\d+$")]
    label: Literal["blocking", "advisory", "question"]
    comment: Line


class CodeReview(_Strict):
    schema_: Literal["code-review/v2"] = Field(alias="schema")
    branch: Line
    date: dt.date
    verdict: Literal["Approve", "Request changes", "Comment", "Cannot verify"]
    verdict_detail: Line
    summary: Text
    comments: list[Comment]

    @model_validator(mode="after")
    def _verdict(self):
        blocking = sum(c.label == "blocking" for c in self.comments)
        if self.verdict == "Approve" and blocking:
            raise ValueError("verdict Approve allows no blocking comment")
        if self.verdict == "Request changes" and not blocking:
            raise ValueError("verdict Request changes needs a blocking comment")
        if blocking > 5:
            raise ValueError(f"{blocking} blocking comments, at most 5")
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
    """The review in the code-review/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("branch", doc.branch),
        f"date: {doc.date.isoformat()}",
        _key("verdict", doc.verdict),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Code review: {doc.branch}",
        "",
        f"**Verdict:** {doc.verdict} — {doc.verdict_detail}",
        "",
        "## Summary",
        "",
        doc.summary,
        "",
        "## Line comments",
        "",
        *(
            [f"- `{c.location}` [{c.label}] {c.comment}" for c in doc.comments]
            or ["None"]
        ),
        "",
        "<!-- prettier-ignore-end -->",
    ]
    return "\n".join(out) + "\n"
