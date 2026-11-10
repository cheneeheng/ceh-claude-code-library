"""qa-report/v2: the QA report's model and its Markdown renderer.

The format in code, per qa-report-schema.md beside this file: `artifact.py` validates a
`QA_REPORT.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the `qa-report/v1`
layout. Copied word for word into every skill that holds qa-report-schema.md.
"""

from __future__ import annotations

import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "qa-report"
VERSION = 2

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
# write-evidence-report runs `git log <commit>..HEAD` on it, so a name such as HEAD is refused.
Commit = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{7,40}$")]
Stamp = Annotated[str, StringConstraints(pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")]
STATUS = {"confirmed": "confirmed (reproduced twice)", "unconfirmed": "unconfirmed"}


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Launch(_Strict):
    command: Line
    entry: Line


class Charter(_Strict):
    charter: Line
    actions_used: int = Field(ge=0, le=20)
    bugs: list[Line]


class Fix(_Strict):
    commit: Commit
    rerun: Text


class Bug(_Strict):
    id: Line
    severity: Literal["Critical", "Major", "Minor", "Cosmetic"]
    title: Line
    status: Literal["confirmed", "unconfirmed"]
    steps: list[Line] = Field(min_length=1)
    expected: Text
    actual: Text
    evidence: Text
    fix: Optional[Fix] = None


class NotExplored(_Strict):
    what: Line
    why: Text


class QaReport(_Strict):
    schema_: Literal["qa-report/v2"] = Field(alias="schema")
    app: Line
    commit: Commit
    mode: Literal["report", "fix"]
    date: Stamp
    launched_with: Launch
    charters: list[Charter]
    bugs: list[Bug]
    usability_notes: list[Text]
    not_explored: list[NotExplored]

    @model_validator(mode="after")
    def _ids(self) -> QaReport:
        ids = [b.id for b in self.bugs]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise ValueError(f"bug ids must be unique: {', '.join(dupes)}")
        for n, c in enumerate(self.charters):
            missing = [i for i in c.bugs if i not in ids]
            if missing:
                raise ValueError(
                    f"charters.{n}.bugs names {', '.join(missing)}, not a bug in this file"
                )
        if self.mode == "report":
            fixed = [n for n, b in enumerate(self.bugs) if b.fix is not None]
            if fixed:
                raise ValueError(
                    f"bugs.{fixed[0]}.fix is allowed only when mode is fix"
                )
        return self


MODEL = QaReport


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _bullet(text: str) -> str:
    lines = text.split("\n")
    return "- " + "\n".join([lines[0]] + [f"  {ln}" if ln else "" for ln in lines[1:]])


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def render(doc: QaReport, source: str) -> str:
    """The report in the qa-report/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("app", doc.app),
        _key("commit", doc.commit),
        _key("mode", doc.mode),
        _key("date", doc.date),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# QA report: {doc.app} at {doc.commit}",
        "",
        f"**Launched with:** `{doc.launched_with.command}` → {doc.launched_with.entry}",
        f"**Mode:** {doc.mode}",
        "",
        "## Charters",
        "",
    ]
    if doc.charters:
        out += ["| Charter | Actions used | Bugs |", "| --- | --- | --- |"]
        out += [
            f"| {_cell(c.charter)} | {c.actions_used}/20 | {_cell(', '.join(c.bugs))} |"
            for c in doc.charters
        ]
    else:
        out.append("None")
    out += ["", "## Bugs"]
    for b in doc.bugs:
        steps = " ".join(f"{n}. {s}" for n, s in enumerate(b.steps, 1))
        out += [
            "",
            f"### {b.id}: {b.severity}: {b.title}",
            "",
            _bullet(f"**Status:** {STATUS[b.status]}"),
            _bullet(f"**Steps:** {steps}"),
            _bullet(f"**Expected / actual:** {b.expected} / {b.actual}"),
            _bullet(f"**Evidence:** {b.evidence}"),
        ]
        if b.fix:
            out.append(_bullet(f"**Fix:** {b.fix.commit}, {b.fix.rerun}"))
    if not doc.bugs:
        out += ["", "None"]
    out += ["", "## Usability notes (not bugs)", ""]
    out += [_bullet(n) for n in doc.usability_notes] or ["None"]
    out += ["", "## Not explored", ""]
    out += [_bullet(f"{n.what}: {n.why}") for n in doc.not_explored] or ["None"]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
