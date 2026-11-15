"""repurposed-post/v2: the repurposed post's model and its Markdown renderer.

The format in code, per repurposed-post-schema.md beside this file: `artifact.py` validates a
`<slug>-<format>.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the
`repurposed-post/v1` layout.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints

NAME = "repurposed-post"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]


def _not_blank(text: str) -> str:
    # The adapted text is kept as written, for pasting: checked, never stripped.
    if not text.strip():
        raise ValueError("is empty or only whitespace")
    return text


Body = Annotated[str, AfterValidator(_not_blank)]


class RepurposedPost(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    schema_: Literal["repurposed-post/v2"] = Field(alias="schema")
    source: Line
    format: Literal["thread", "linkedin", "tldr", "newsletter"]
    date: dt.date
    text: Body


MODEL = RepurposedPost


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def render(doc: RepurposedPost, source: str) -> str:
    """The text in the repurposed-post/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("source", doc.source),
        _key("format", doc.format),
        f"date: {doc.date.isoformat()}",
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        doc.text.strip("\n"),
        "",
        "<!-- prettier-ignore-end -->",
    ]
    return "\n".join(out) + "\n"
