"""interface-audit/v2: the interface audit's model and its Markdown renderer.

The format in code, per interface-audit-schema.md beside this file: `artifact.py` validates a
`UX_AUDIT.yaml` whose `schema:` is `interface-audit/v2` with `MODEL` and writes
`render(doc, source)` beside it, in the `interface-audit/v1` layout. Copied word for word into
every skill that holds interface-audit-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "interface-audit"
VERSION = 2

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
# write-evidence-report runs `git log <commit>..HEAD` on it, so a name such as HEAD is refused.
Commit = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{7,40}$")]
Count = Annotated[int, Field(ge=0)]
METHOD = "cold persona-constrained agents — proxy for a user test, not a user test"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Gate(_Strict):
    score: Count
    out_of: Count
    na: Count

    @model_validator(mode="after")
    def _five(self) -> Gate:
        if self.out_of + self.na != 5:
            raise ValueError("out_of + na must be 5")
        if self.score > self.out_of:
            raise ValueError("score must not exceed out_of")
        return self

    def text(self) -> str:
        if self.na == 0:
            return f"{self.score}/5"
        return f"{self.score}/{self.out_of}, {self.na} N/A"


class Goal(_Strict):
    goal: Line
    budget: Count


class Skipped(_Strict):
    persona: Line
    why: Line


class Walkers(_Strict):
    run: list[Line] = Field(min_length=1)
    skipped: list[Skipped]


class Screen(_Strict):
    screen: Line
    where_am_i: Line
    what_for: Line
    primary_action: Line
    what_happened: Line
    way_out: Line


class Finding(_Strict):
    id: Line
    severity: Literal["Blocker", "Detour", "Friction", "Polish"]
    title: Line
    where: Line
    persona: Line
    expected: Text
    got: Text
    fix: Text


class Delegated(_Strict):
    skill: Line
    what: Text


class InterfaceAudit(_Strict):
    schema_: Literal["interface-audit/v2"] = Field(alias="schema")
    target: Line
    surface: Line
    run: Annotated[int, Field(ge=1)]
    date: dt.date
    commit: Commit
    goals: list[Goal] = Field(min_length=1)
    audience: Text
    allowlist: Text
    walkers: Walkers
    gate: Gate
    five_questions: list[Screen]
    findings: list[Finding]
    hypotheses: list[Text]
    delegated: list[Delegated]
    not_covered: list[Text]

    @model_validator(mode="after")
    def _ids(self) -> InterfaceAudit:
        ids = [f.id for f in self.findings]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise ValueError(f"finding ids must be unique: {', '.join(dupes)}")
        return self


MODEL = InterfaceAudit


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


def _walkers(w: Walkers) -> str:
    skipped = "; ".join(f"skipped {s.persona}: {s.why}" for s in w.skipped)
    return ", ".join(w.run) + (f" ({skipped})" if skipped else "")


def render(doc: InterfaceAudit, source: str) -> str:
    """The report in the interface-audit/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    goals = "; ".join(f"{g.goal} ({g.budget} actions)" for g in doc.goals)
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("target", doc.target),
        _key("surface", doc.surface),
        f"run: {doc.run:03d}",
        f"date: {doc.date.isoformat()}",
        _key("commit", doc.commit),
        _key("gate", doc.gate.text()),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Interface Audit — {doc.target} ({doc.surface})",
        "",
        f"**Goal(s) walked:** {goals}",
        f"**Audience baseline:** {doc.audience}",
        f"**Allowlist:** {doc.allowlist}",
        f"**Walkers:** {_walkers(doc.walkers)}",
        f"**Method:** {METHOD}",
        f"**Gate:** {doc.gate.text()}",
        "",
        "## Five questions",
        "",
    ]
    if doc.five_questions:
        out += [
            "| Screen / command | Where am I | What for | Primary action | What happened | Way out |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        out += [
            "| "
            + " | ".join(
                _cell(c)
                for c in (
                    s.screen,
                    s.where_am_i,
                    s.what_for,
                    s.primary_action,
                    s.what_happened,
                    s.way_out,
                )
            )
            + " |"
            for s in doc.five_questions
        ]
    else:
        out.append("None")
    out += ["", "## Findings"]
    for f in doc.findings:
        out += [
            "",
            f"### {f.id} — {f.severity} — {f.title}",
            "",
            _bullet(f"**Where:** {f.where}"),
            _bullet(f"**Persona:** {f.persona}"),
            _bullet(f"**Expected / got:** {f.expected} / {f.got}"),
            _bullet(f"**Fix:** {f.fix}"),
        ]
    if not doc.findings:
        out += ["", "None"]
    out += ["", "## Hypotheses (no walker stalled — unranked)", ""]
    out += [_bullet(h) for h in doc.hypotheses] or ["None"]
    out += ["", "## Delegated", ""]
    out += [_bullet(f"{d.skill}: {d.what}") for d in doc.delegated] or ["None"]
    out += ["", "## Not covered", ""]
    out += [_bullet(n) for n in doc.not_covered] or ["None"]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
