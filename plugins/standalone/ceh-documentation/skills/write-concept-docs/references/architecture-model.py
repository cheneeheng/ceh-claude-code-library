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
    # Only `true`, on a diagram of what is not built yet. A built diagram leaves the key out.
    planned: Optional[Literal[True]] = None
    walkthrough: Text
    notice: list[Text] = Field(max_length=3)
    mermaid: Optional[Text] = None
    parts: Optional[list[Part]] = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _one_body(self) -> Diagram:
        if (self.mermaid is None) == (self.parts is None):
            raise ValueError("a diagram has exactly one of mermaid and parts")
        return self


PART_MAX_LINES = 30
ATX = re.compile(r"^ {0,3}#{1,6}(\s|$)")
UNDERLINE = re.compile(r"^ {0,3}(=+|-+)\s*$")


def _heading_error(text: str) -> Optional[str]:
    """What breaks the renderer's numbering in a Markdown field: a heading it did not number, or
    a code block left open, which swallows every heading after it."""
    fenced, above = False, ""
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        elif not fenced and (
            ATX.match(line) or (above.strip() and UNDERLINE.match(line))
        ):
            return "holds a heading line"
        above = line
    return "holds an unclosed code block" if fenced else None


class DesignPart(_Strict):
    title: Heading
    body: Text

    @model_validator(mode="after")
    def _small(self) -> DesignPart:
        n = len(self.body.splitlines())
        if n > PART_MAX_LINES:
            raise ValueError(
                f"part '{self.title}' has {n} lines, over {PART_MAX_LINES}: make it its own topic"
            )
        return self


class DesignTopic(_Strict):
    topic: Heading
    # Markdown that states the contract: paragraphs, lists, tables, code blocks, no heading.
    choice: Text
    reason: Text
    parts: Optional[list[DesignPart]] = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _no_headings(self) -> DesignTopic:
        if err := _heading_error(self.choice):
            raise ValueError(f"{self.topic}: choice {err}, use parts")
        if err := _heading_error(self.reason):
            raise ValueError(f"{self.topic}: reason {err}")
        for p in self.parts or []:
            if err := _heading_error(p.body):
                raise ValueError(f"{self.topic}, part '{p.title}': body {err}")
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
    # The current choice per topic, edited in place. A file with no technical design leaves it out.
    technical_design: Optional[list[DesignTopic]] = Field(default=None, min_length=1)
    key_decisions: list[KeyDecision]

    @model_validator(mode="after")
    def _superseded_by_another(self) -> Architecture:
        seen: set[str] = set()
        for t in self.technical_design or []:
            if t.topic.casefold() in seen:
                raise ValueError(f"technical_design: topic '{t.topic}' appears twice")
            seen.add(t.topic.casefold())
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
    # The Contents list: each numbered heading with its depth below `##`.
    toc: list[tuple[int, str]] = [(0, "01. Overview")]
    body: list[str] = ["## 01. Overview", ""]
    body += [f"- {b}" for b in doc.overview.bullets] + [""] + _fence(doc.overview.flow)
    for n, d in enumerate(doc.diagrams, 2):
        head = f"{n:02d}. {d.name}"
        toc.append((0, head))
        body += ["", f"## {head}", ""]
        if d.planned:
            body += ["**Planned:** not built yet.", ""]
        body += _walk(d.walkthrough, d.notice)
        if d.mermaid:
            body += _fence(d.mermaid)
        for i, p in enumerate(d.parts or [], 1):
            sub = f"{n:02d}.{i:02d} {p.title}"
            toc.append((1, sub))
            body += (
                ["", f"### {sub}", ""]
                + _walk(p.walkthrough, p.notice)
                + _fence(p.mermaid)
            )
    n = len(doc.diagrams) + 2
    if doc.technical_design:
        head = f"{n:02d}. Technical Design"
        toc.append((0, head))
        body += ["", f"## {head}"]
        for i, t in enumerate(doc.technical_design, 1):
            sub = f"{n:02d}.{i:02d} {t.topic}"
            toc.append((1, sub))
            body += ["", f"### {sub}", "", t.choice, "", f"**Reason:** {t.reason}"]
            for j, p in enumerate(t.parts or [], 1):
                part = f"{n:02d}.{i:02d}.{j:02d} {p.title}"
                toc.append((2, part))
                body += ["", f"#### {part}", "", p.body]
        n += 1
    kd = f"{n:02d}. Key Decisions"
    toc.append((0, kd))
    body += ["", f"## {kd}"]
    for k in doc.key_decisions:
        body += ["", f"### {k.date.isoformat()} — {k.title}", ""]
        body += [
            f"**Status:** {k.status}",
            f"**Context:** {k.context}",
            f"**Decision:** {k.decision}",
            f"**Consequences:** {k.consequences}",
        ]
    contents = [f"{'  ' * depth}- [{h}](#{anchor(h)})" for depth, h in toc]
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
