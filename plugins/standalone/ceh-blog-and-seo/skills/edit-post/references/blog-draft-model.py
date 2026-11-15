"""blog-draft/v2: the blog draft's model and its Markdown renderer.

The format in code, per blog-draft-schema.md beside this file: `artifact.py` validates a draft's
`.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the `blog-draft/v1` layout.
Copied word for word into every skill that holds blog-draft-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints

NAME = "blog-draft"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]


def _not_blank(text: str) -> str:
    # The body is kept as written, for pasting: checked, never stripped.
    if not text.strip():
        raise ValueError("is empty or only whitespace")
    return text


Body = Annotated[str, AfterValidator(_not_blank)]
PostType = Literal[
    "Lessons Learned",
    "How-To",
    "Opinion",
    "Project / Launch",
    "Thought Leadership",
    "Personal Story",
]


class BlogDraft(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    schema_: Literal["blog-draft/v2"] = Field(alias="schema")
    title: Line
    description: Line
    type: PostType
    status: Literal["draft", "published"]
    date: dt.date
    body: Body


MODEL = BlogDraft


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def render(doc: BlogDraft, source: str) -> str:
    """The draft in the blog-draft/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("title", doc.title),
        _key("description", doc.description),
        _key("type", doc.type),
        _key("status", doc.status),
        f"date: {doc.date.isoformat()}",
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        doc.body.strip("\n"),
        "",
        "<!-- prettier-ignore-end -->",
    ]
    return "\n".join(out) + "\n"
