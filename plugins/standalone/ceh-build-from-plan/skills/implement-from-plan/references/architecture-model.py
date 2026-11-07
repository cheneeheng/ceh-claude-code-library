"""architecture/v3: the architecture document's model and its Markdown renderer.

The format in code, per architecture-schema.md beside this file: `artifact.py` validates an
`ARCHITECTURE.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the
`architecture/v2` layout, with section numbers, the Contents list and anchors generated. Copied word
for word into every skill that holds architecture-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "architecture"
VERSION = 3

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
# A heading the renderer numbers: no em dash, which leaves a double hyphen in the anchor.
Heading = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n—]*$")
]
SUPERSEDED = re.compile(r"^Superseded by (\d{4}-\d{2}-\d{2}) (.+)$")


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Overview(_Strict):
    bullets: list[Text] = Field(min_length=1)
    flow: Text


class Part(_Strict):
    title: Heading
    walkthrough: Text
    notice: list[Text] = Field(max_length=3)
    mermaid: Text


class Diagram(_Strict):
    name: Literal[
        "System context", "Components", "Key flows", "Data model", "State machines"
    ]
    walkthrough: Text
    notice: list[Text] = Field(max_length=3)
    mermaid: Optional[Text] = None
    parts: Optional[list[Part]] = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _one_body(self) -> Diagram:
        if (self.mermaid is None) == (self.parts is None):
            raise ValueError("a diagram has exactly one of mermaid and parts")
        return self


class KeyDecision(_Strict):
    date: dt.date
    title: Heading
    status: Line
    context: Text
    decision: Text
    consequences: Text

    @model_validator(mode="after")
    def _status_shape(self) -> KeyDecision:
        if self.status != "Accepted" and not SUPERSEDED.match(self.status):
            raise ValueError("status is Accepted or 'Superseded by YYYY-MM-DD <title>'")
        return self


class Architecture(_Strict):
    schema_: Literal["architecture/v3"] = Field(alias="schema")
    overview: Overview
    diagrams: list[Diagram]
    key_decisions: list[KeyDecision]

    @model_validator(mode="after")
    def _superseded_by_another(self) -> Architecture:
        entries = {(e.date.isoformat(), e.title) for e in self.key_decisions}
        for k in self.key_decisions:
            m = SUPERSEDED.match(k.status)
            named = m and (m.group(1), m.group(2))
            if named and (
                named not in entries or named == (k.date.isoformat(), k.title)
            ):
                raise ValueError(f"{k.title}: '{k.status}' names no other entry")
        return self


MODEL = Architecture


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def anchor(heading: str) -> str:
    """GitHub's heading anchor: lowercase, keep letters, digits, spaces, - and _, spaces to -."""
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


def _fence(body: str) -> list[str]:
    return ["```mermaid", body, "```"]


def _walk(walkthrough: str, notice: list[str]) -> list[str]:
    out = [walkthrough, ""]
    if notice:
        out += [f"- {n}" for n in notice] + [""]
    return out


def render(doc: Architecture, source: str) -> str:
    """The document in the architecture/v2 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    sections: list[tuple[str, list[str]]] = [("01. Overview", [])]
    body: list[str] = ["## 01. Overview", ""]
    body += [f"- {b}" for b in doc.overview.bullets] + [""] + _fence(doc.overview.flow)
    for n, d in enumerate(doc.diagrams, 2):
        head = f"{n:02d}. {d.name}"
        subs = []
        body += ["", f"## {head}", ""] + _walk(d.walkthrough, d.notice)
        if d.mermaid:
            body += _fence(d.mermaid)
        for i, p in enumerate(d.parts or [], 1):
            sub = f"{n:02d}.{i:02d} {p.title}"
            subs.append(sub)
            body += (
                ["", f"### {sub}", ""]
                + _walk(p.walkthrough, p.notice)
                + _fence(p.mermaid)
            )
        sections.append((head, subs))
    kd = f"{len(doc.diagrams) + 2:02d}. Key Decisions"
    sections.append((kd, []))
    body += ["", f"## {kd}"]
    for k in doc.key_decisions:
        body += ["", f"### {k.date.isoformat()} — {k.title}", ""]
        body += [
            f"**Status:** {k.status}",
            f"**Context:** {k.context}",
            f"**Decision:** {k.decision}",
            f"**Consequences:** {k.consequences}",
        ]
    contents = []
    for head, subs in sections:
        contents.append(f"- [{head}](#{anchor(head)})")
        contents += [f"  - [{s}](#{anchor(s)})" for s in subs]
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        "# Architecture",
        "",
        "## Contents",
        "",
        *contents,
        "",
        *body,
        "",
        "<!-- prettier-ignore-end -->",
    ]
    return "\n".join(out) + "\n"
