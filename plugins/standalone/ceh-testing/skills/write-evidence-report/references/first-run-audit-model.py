"""first-run-audit/v2: the first-run audit's model and its Markdown renderer.

The format in code, per first-run-audit-schema.md beside this file: `artifact.py` validates a
`UX_AUDIT.yaml` whose `schema:` is `first-run-audit/v2` with `MODEL` and writes
`render(doc, source)` beside it, in the `first-run-audit/v1` layout. Copied word for word into
every skill that holds first-run-audit-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "first-run-audit"
VERSION = 2

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
# write-evidence-report runs `git log <commit>..HEAD` on it, so a name such as HEAD is refused.
Commit = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{7,40}$")]
Count = Annotated[int, Field(ge=0)]
METHOD = "cold persona-constrained subagents — proxy for a user test, not a user test"


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


class Milestone(_Strict):
    name: Line
    budget: Count


class Skipped(_Strict):
    persona: Line
    why: Line


class Walkers(_Strict):
    run: list[Line] = Field(min_length=1)
    skipped: list[Skipped]
    mode: Literal["in parallel", "serially", "in isolated copies"]


class Result(_Strict):
    persona: Line
    furthest: Line
    stop_reason: Line
    actions: Count
    budget: Count
    lookups: Count
    wait_s: Count
    first_stall: Optional[Line] = None


class Finding(_Strict):
    id: Line
    severity: Literal["Blocker", "Detour", "Friction", "Polish"]
    title: Line
    where: Line
    persona: Line
    expected: Text
    got: Text
    missing_knowledge: Text
    fix: Text


class FirstRunAudit(_Strict):
    schema_: Literal["first-run-audit/v2"] = Field(alias="schema")
    target: Line
    run: Annotated[int, Field(ge=1)]
    date: dt.date
    commit: Commit
    goal: Line
    milestones: list[Milestone] = Field(min_length=1)
    audience: Text
    frozen_set: Text
    walkers: Walkers
    gate: Gate
    results: list[Result]
    minutes: Count
    findings: list[Finding]
    hypotheses: list[Text]
    not_covered: list[Text]

    @model_validator(mode="after")
    def _ids(self) -> FirstRunAudit:
        ids = [f.id for f in self.findings]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise ValueError(f"finding ids must be unique: {', '.join(dupes)}")
        for n, r in enumerate(self.results):
            if r.first_stall is not None and r.first_stall not in ids:
                raise ValueError(
                    f"results.{n}.first_stall names {r.first_stall}, not a finding in this file"
                )
        return self


MODEL = FirstRunAudit


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


def render(doc: FirstRunAudit, source: str) -> str:
    """The report in the first-run-audit/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    budgets = "; ".join(
        f"{m.name} ≤ {m.budget}" + (" actions" if n == 0 else "")
        for n, m in enumerate(doc.milestones)
    )
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("target", doc.target),
        f"run: {doc.run:03d}",
        f"date: {doc.date.isoformat()}",
        _key("commit", doc.commit),
        _key("gate", doc.gate.text()),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# First-Run Walkthrough — {doc.target}",
        "",
        f"**Goal:** {doc.goal}",
        f"**Milestones & budget:** {budgets}",
        f"**Audience baseline:** {doc.audience}",
        f"**Frozen set:** {doc.frozen_set}",
        f"**Walkers:** {_walkers(doc.walkers)} — run {doc.walkers.mode}",
        f"**Method:** {METHOD}",
        f"**Gate:** {doc.gate.text()}",
        "",
        "## Results",
        "",
    ]
    if doc.results:
        out += [
            "| Persona | Furthest milestone | Stop reason | Actions vs budget | External lookups | Machine wait | First stall |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        out += [
            f"| {_cell(r.persona)} | {_cell(r.furthest)} | {_cell(r.stop_reason)} | {r.actions}/{r.budget}"
            f" | {r.lookups} | {r.wait_s}s | {_cell(r.first_stall or '—')} |"
            for r in doc.results
        ]
    else:
        out.append("None")
    wait = sum(r.wait_s for r in doc.results)
    out += [
        "",
        f"**Estimated newcomer time to goal:** ~{doc.minutes} min (cost model, not measured) + {wait}s machine wait",
        "",
        "## Findings",
    ]
    for f in doc.findings:
        out += [
            "",
            f"### {f.id} — {f.severity} — {f.title}",
            "",
            _bullet(f"**Where:** {f.where}"),
            _bullet(f"**Persona:** {f.persona}"),
            _bullet(f"**Expected / got:** {f.expected} / {f.got}"),
            _bullet(f"**Missing knowledge:** {f.missing_knowledge}"),
            _bullet(f"**Fix:** {f.fix}"),
        ]
    if not doc.findings:
        out += ["", "None"]
    out += ["", "## Hypotheses (no walker stalled — unranked)", ""]
    out += [_bullet(h) for h in doc.hypotheses] or ["None"]
    out += ["", "## Not covered", ""]
    out += [_bullet(n) for n in doc.not_covered] or ["None"]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
