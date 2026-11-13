"""competitor-report/v2: the competitor report's model and its Markdown renderer.

The format in code, per competitor-report-schema.md beside this file: `artifact.py` validates a
`<slug>.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the
`competitor-report/v1` layout. Copied word for word into every skill that holds
competitor-report-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "competitor-report"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
Block = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Rating = Literal["Covered", "Partial", "Gap", "N/A"]
# A Covered or Partial row names a component of ours: a ceh-<plugin>[:<name>] or a path.
OURS = re.compile(r"ceh-[a-z0-9]|\S/\S")


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Fields(_Strict):
    read: Literal["shallow clone", "web pages", "local checkout", "pasted material"]
    author: Line
    version: Line
    version_from: Line
    license: Line
    size: Line
    size_command: Line
    missing: Optional[Line] = None


class Adopt(_Strict):
    idea: Line
    lands_in: Line
    why: Line
    covers: list[Line]


class Build(_Strict):
    idea: Line
    lands_in: Line
    effort: Literal["M", "L"]
    why: Line
    covers: list[Line]


class Skip(_Strict):
    idea: Line
    why_not: Line
    covers: list[Line]


class Take(_Strict):
    adopt_now: list[Adopt]
    build: list[Build]
    skip: list[Skip]
    notes: Optional[Block] = None


class OhWow(_Strict):
    what: Line
    one_line: Line
    how: Line
    evidence: Line


class Group(_Strict):
    group: Line
    count: int = Field(ge=0)
    items: Line

    @model_validator(mode="after")
    def _empty(self):
        if self.count == 0 and self.items != "—":
            raise ValueError("a group with count 0 has items: —")
        return self


class Inventory(_Strict):
    groups: list[Group] = Field(min_length=1)
    notes: Optional[Block] = None

    @model_validator(mode="after")
    def _sorted(self):
        counts = [g.count for g in self.groups]
        if counts != sorted(counts, reverse=True):
            raise ValueError(f"groups are sorted by count, largest first, got {counts}")
        return self


class Extra(_Strict):
    after: int = Field(ge=1, le=5)
    heading: Line
    body: Block


class Row(_Strict):
    component: Line
    evidence: Line
    what: Line
    rating: Rating
    ours: Optional[Line] = None

    @model_validator(mode="after")
    def _ours(self):
        if self.rating in ("Covered", "Partial"):
            if not self.ours:
                raise ValueError(
                    f"{self.component}: a {self.rating} row needs ours, else it is a Gap"
                )
            if not OURS.search(self.ours):
                raise ValueError(
                    f"{self.component}: ours names no ceh-<plugin>:<name>, ceh-<plugin> or path"
                )
        elif self.ours is not None:
            raise ValueError(
                f"{self.component}: a {self.rating} row takes no ours, put its note in what"
            )
        return self


class CoverageGroup(_Strict):
    group: Line
    rows: list[Row] = Field(min_length=1)


class CompetitorReport(_Strict):
    schema_: Literal["competitor-report/v2"] = Field(alias="schema")
    competitor: Line
    source: Line
    analysed: dt.date
    summary: Line
    verdict: Line
    fields: Fields
    take: Take
    how_it_works: list[Line] = Field(min_length=3, max_length=5)
    oh_wow: list[OhWow]
    inventory: Inventory
    coverage_notes: Optional[Block] = None
    extra_sections: Optional[list[Extra]] = None
    coverage: list[CoverageGroup] = Field(min_length=1)

    @model_validator(mode="after")
    def _complete(self):
        """Every Partial or Gap component is taken, built or skipped, and nothing else is."""
        names = [r.component for g in self.coverage for r in g.rows]
        dupes = sorted({n for n in names if names.count(n) > 1})
        if dupes:
            raise ValueError(f"component names repeat across coverage: {dupes}")
        open_ = {
            r.component
            for g in self.coverage
            for r in g.rows
            if r.rating in ("Partial", "Gap")
        }
        rows = [*self.take.adopt_now, *self.take.build, *self.take.skip]
        covered = {c for r in rows for c in r.covers}
        if wrong := sorted(covered - open_):
            raise ValueError(f"take covers names no Partial or Gap component: {wrong}")
        if left := sorted(open_ - covered):
            raise ValueError(f"Partial or Gap components no take row covers: {left}")
        return self


MODEL = CompetitorReport

LEGEND = (
    "**Covered**: one of our components does the same job. **Partial**: ours does part of it. "
    "**Gap**: we ship nothing for it. **N/A**: plumbing for the competitor's own product, host "
    "or vendor. Coverage is inferred from our skill names and descriptions, not tested."
)


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _cell(text: str) -> str:
    """A table cell: a bare `|` would split the row, so every `|` is escaped, and a backslash
    written before one is kept as `&#92;`."""
    return text.replace("\\|", "&#92;|").replace("|", "\\|")


def _table(head: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(" --- " for _ in head) + "|"]
    return out + ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows]


def _code(name: str) -> str:
    """A name as a code span, with a longer fence when the name holds a backtick."""
    return f"`` {name} ``" if "`" in name else f"`{name}`"


def _covers(text: str, covers: list[str]) -> str:
    if not covers:
        return text
    names = [_code(c) for c in covers]
    joined = (
        names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    )
    return f"{text} Covers {joined}."


def _block(text: Optional[str]) -> list[str]:
    return [text.strip(), ""] if text else []


def render(doc: CompetitorReport, source: str) -> str:
    """The report in the competitor-report/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    f, t = doc.fields, doc.take
    read = f"{f.read}, analysed {doc.analysed.isoformat()}"
    if f.missing:
        read += f"; missing: {f.missing}"
    rows = [r for g in doc.coverage for r in g.rows]
    tally = {
        k: sum(r.rating == k for r in rows)
        for k in ("Covered", "Partial", "Gap", "N/A")
    }

    def extras(n: int) -> list[str]:
        out = []
        for e in doc.extra_sections or []:
            if e.after == n:
                out += [f"## {e.heading}", "", e.body.strip(), ""]
        return out

    def none(table: list[str], empty: str) -> list[str]:
        return table if len(table) > 2 else [empty]

    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("competitor", doc.competitor),
        _key("source", doc.source),
        f"analysed: {doc.analysed.isoformat()}",
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Competitor analysis: {doc.competitor}",
        "",
        doc.summary,
        "",
        f"**Verdict:** {doc.verdict}",
        "",
        *_table(
            ["Field", "Value"],
            [
                ["Source", f"{doc.source} ({read})"],
                ["Author", f.author],
                ["Version", f"{f.version} ({f.version_from})"],
                ["License", f.license],
                ["Size", f"{f.size} ({_code(f.size_command)})"],
            ],
        ),
        "",
        "## 1. What we take",
        "",
        *_block(t.notes),
        "### Adopt now",
        "",
        *none(
            _table(
                ["Idea", "Lands in", "Why"],
                [[r.idea, r.lands_in, _covers(r.why, r.covers)] for r in t.adopt_now],
            ),
            "None.",
        ),
        "",
        "### Build",
        "",
        *none(
            _table(
                ["Idea", "Lands in", "Effort", "Why"],
                [
                    [r.idea, r.lands_in, r.effort, _covers(r.why, r.covers)]
                    for r in t.build
                ],
            ),
            "None.",
        ),
        "",
        "### Skip",
        "",
        *none(
            _table(
                ["Idea", "Why not"],
                [[r.idea, _covers(r.why_not, r.covers)] for r in t.skip],
            ),
            "None.",
        ),
        "",
        *extras(1),
        "## 2. How it works",
        "",
        *(f"{n}. {s}" for n, s in enumerate(doc.how_it_works, 1)),
        "",
        *extras(2),
        '## 3. "Oh wow" moments',
        "",
        *none(
            _table(
                ["#", "What", "One line", "How it works", "Evidence"],
                [
                    [str(n), o.what, o.one_line, o.how, o.evidence]
                    for n, o in enumerate(doc.oh_wow, 1)
                ],
            ),
            "None found.",
        ),
        "",
        *extras(3),
        "## 4. Inventory",
        "",
        *_table(
            ["Group", "Count", "Items"],
            [[g.group, str(g.count), g.items] for g in doc.inventory.groups],
        ),
        "",
        *_block(doc.inventory.notes),
        *extras(4),
        "## 5. Coverage in our work",
        "",
        LEGEND,
        "",
        *_block(doc.coverage_notes),
        f"**Tally ({len(rows)} components):** {tally['Covered']} covered, "
        f"{tally['Partial']} partial, {tally['Gap']} gaps, {tally['N/A']} N/A.",
        "",
    ]
    for g in doc.coverage:
        out += [
            f"### {g.group}",
            "",
            *_table(
                [
                    f"{doc.competitor} component",
                    "What it does",
                    "Ours",
                    "Our component",
                ],
                [
                    [f"{r.component} ({r.evidence})", r.what, r.rating, r.ours or "—"]
                    for r in g.rows
                ],
            ),
            "",
        ]
    out += extras(5)
    out.append("<!-- prettier-ignore-end -->")
    return "\n".join(out) + "\n"
