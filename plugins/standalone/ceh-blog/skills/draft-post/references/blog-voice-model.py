"""blog-voice/v2: the blog voice profile's model and its Markdown renderer.

The format in code, per blog-voice-schema.md beside this file: `artifact.py` validates a
`blog-voice.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the `blog-voice/v1`
layout. Copied word for word into every skill that holds blog-voice-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
)

NAME = "blog-voice"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]


def _not_blank(text: str) -> str:
    # The author's words are kept as written: checked for content, never stripped.
    if not text.strip():
        raise ValueError("is empty or only whitespace")
    return text


Text = Annotated[str, AfterValidator(_not_blank)]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Observation(_Strict):
    point: Text
    quote: Text
    source: Optional[Line]


class BlogVoice(_Strict):
    schema_: Literal["blog-voice/v2"] = Field(alias="schema")
    blog: Line
    posts_read: int = Field(ge=3)
    date: dt.date
    rhythm: list[Observation]
    # `register` is a BaseModel attribute, so the field takes the key through an alias.
    register_: list[Observation] = Field(alias="register")
    recurring_words: list[Observation]
    never_used: list[Text]
    openings_closings: list[Observation]
    notes: Optional[Text] = None


MODEL = BlogVoice

NONE = "None established."


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _item(text: str) -> str:
    """Text as one list item: its own words, each later line indented under the bullet."""
    return text.rstrip("\n").replace("\n", "\n  ")


def _observations(rows: list[Observation]) -> list[str]:
    if not rows:
        return [NONE]
    out = []
    for o in rows:
        line = f'- {_item(o.point)}: "{_item(o.quote)}"'
        out.append(f"{line} ({o.source})" if o.source else line)
    return out


def render(doc: BlogVoice, source: str) -> str:
    """The profile in the blog-voice/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    sections = [
        ("Rhythm", _observations(doc.rhythm)),
        ("Register", _observations(doc.register_)),
        ("Recurring words and phrases", _observations(doc.recurring_words)),
        ("Never used", [f"- {_item(n)}" for n in doc.never_used] or [NONE]),
        ("Openings and closings", _observations(doc.openings_closings)),
    ]
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("blog", doc.blog),
        f"posts_read: {doc.posts_read}",
        f"date: {doc.date.isoformat()}",
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
    ]
    for heading, body in sections:
        out += [f"## {heading}", "", *body, ""]
    if doc.notes:
        out += ["## Notes", "", doc.notes.rstrip("\n"), ""]
    out.append("<!-- prettier-ignore-end -->")
    return "\n".join(out) + "\n"
