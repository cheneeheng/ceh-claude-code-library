"""handoff/v2: the session handoff's model and its Markdown renderer.

The format in code, per handoff-schema.md beside this file: `artifact.py` validates a
`<YYYYMMDD-HHMMSS>-<session-id>-handoff.yaml`, or a caller's `--file` YAML, with `MODEL` and
writes `render(doc, source)` beside it, in the `handoff/v1` layout. Copied word for word into
every skill that holds handoff-schema.md.
"""

from __future__ import annotations

import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NAME = "handoff"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
Saved = Annotated[str, StringConstraints(pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")]
Session = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{8}$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class CallerField(_Strict):
    name: Line
    value: Line


class Done(_Strict):
    item: Line
    files: Line
    validated: bool


class Handoff(_Strict):
    schema_: Literal["handoff/v2"] = Field(alias="schema")
    saved: Saved
    session: Session
    header: list[Line]
    repo: Line
    branch: Line
    fields: list[CallerField]
    goal: list[Line] = Field(min_length=1)
    done: list[Done]
    in_flight: list[Line]
    # A handoff with nothing open has nothing to resume: finished work names its confirming check.
    open: list[Line] = Field(min_length=1)
    decisions_pending: list[Line]
    forks_go_to: Optional[Line] = None
    resume_with: Line


MODEL = Handoff


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _bullets(items: list[str]) -> list[str]:
    return [f"- {i}" for i in items] or ["- none"]


def render(doc: Handoff, source: str) -> str:
    """The handoff in the handoff/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    pending = "; ".join(doc.decisions_pending) or "none"
    if doc.forks_go_to:
        pending += f", forks go to {doc.forks_go_to}"
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("saved", doc.saved),
        _key("session", doc.session),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Handoff — {doc.saved}",
        "",
    ]
    if doc.header:
        out += [*doc.header, ""]
    out += [
        f"**Repo / branch:** {doc.repo} / {doc.branch}",
        f"**Session:** {doc.session}",
        *(f"**{f.name}:** {f.value}" for f in doc.fields),
        "",
        "**Goal:**",
        "",
        *_bullets(doc.goal),
        "",
        "**Done:**",
        "",
        *_bullets(
            [
                f"{d.item}: {d.files}, {'validated' if d.validated else 'not validated'}"
                for d in doc.done
            ]
        ),
        "",
        "**In flight:**",
        "",
        *_bullets(doc.in_flight),
        "",
        "**Open:**",
        "",
        *(f"{n}. {o}" for n, o in enumerate(doc.open, 1)),
        "",
        f"**Decisions pending:** {pending}",
        "",
        f"**Resume with:** {doc.resume_with}",
        "",
        "<!-- prettier-ignore-end -->",
    ]
    return "\n".join(out) + "\n"
