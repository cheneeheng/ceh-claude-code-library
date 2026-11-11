"""glossary/v2: the glossary's model and its Markdown renderer.

The format in code, per glossary-schema.md beside this file: `artifact.py` validates a
`GLOSSARY.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the `glossary/v1`
layout. Copied word for word into every skill that holds glossary-schema.md.
"""

from __future__ import annotations

import json
import re
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "glossary"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
Block = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


def _fold(text: str) -> str:
    """The comparison key of a term or alias: case and surrounding whitespace ignored."""
    return text.strip().casefold()


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Entry(_Strict):
    term: Line
    definition: Block
    avoid: list[Line]
    not_confused_with: list[Line]

    @model_validator(mode="after")
    def _aliases(self):
        folded = [_fold(a) for a in self.avoid]
        if _fold(self.term) in folded:
            raise ValueError(f"{self.term}: avoid repeats the term itself")
        dupes = sorted({a for a in folded if folded.count(a) > 1})
        if dupes:
            raise ValueError(f"{self.term}: avoid lists an alias twice: {dupes}")
        return self


class OpenTerm(_Strict):
    term: Line
    question: Block


class Glossary(_Strict):
    schema_: Literal["glossary/v2"] = Field(alias="schema")
    entries: list[Entry]
    open: list[OpenTerm]
    notes: Optional[Block] = None

    @model_validator(mode="after")
    def _terms(self):
        if not self.entries and not self.open:
            raise ValueError("entries and open are both empty: a glossary holds a term")
        folded = [_fold(e.term) for e in self.entries]
        dupes = sorted({t for t in folded if folded.count(t) > 1})
        if dupes:
            raise ValueError(f"entries repeat a term, ignoring case: {dupes}")
        return self


MODEL = Glossary


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _label(text: str) -> str:
    """A term or alias as literal text: Markdown delimiters escaped, the stored text unchanged."""
    return re.sub(r"([\\`*_\[\]<>|])", r"\\\1", text)


def render(doc: Glossary, source: str) -> str:
    """The glossary in the glossary/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        "# Glossary",
        "",
    ]
    for e in sorted(doc.entries, key=lambda e: e.term.casefold()):
        out.append(f"**{_label(e.term)}** — {e.definition.strip()}")
        extra = []
        if e.avoid:
            extra.append("_Avoid:_ " + ", ".join(_label(a) for a in e.avoid) + ".")
        if e.not_confused_with:
            near = ", ".join(f"**{_label(n)}**" for n in e.not_confused_with)
            extra.append(f"_Not to be confused with:_ {near}.")
        if extra:
            out.append(" ".join(extra))
        out.append("")
    if doc.open:
        out += ["## Open terms", ""]
        out += [f"- **{_label(o.term)}**: {o.question.strip()}" for o in doc.open]
        out.append("")
    if doc.notes:
        out += ["## Notes", "", doc.notes.strip(), ""]
    out.append("<!-- prettier-ignore-end -->")
    return "\n".join(out) + "\n"
