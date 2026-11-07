"""plan/v2: the build plan's model and its Markdown renderer.

The format in code, per plan-schema.md beside this file: `artifact.py` validates a plan YAML with
`MODEL` and writes `render(plan, source)` beside it. Copied word for word into every plugin that
holds plan-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "plan"
VERSION = 2

# Free text: anything but empty. A Line holds no line break.
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]


class _Strict(BaseModel):
    # strict: a value YAML retyped (`yes` read as a bool) is an error, never coerced.
    model_config = ConfigDict(extra="forbid", strict=True)


class OutItem(_Strict):
    item: Text
    reason: Text


class Scope(_Strict):
    # `in` is a Python keyword, so the field takes the YAML key through its alias.
    in_: list[Text] = Field(alias="in", min_length=1)
    out: list[OutItem]


class Decision(_Strict):
    topic: Line
    decision: Text


class Phase(_Strict):
    name: Line
    builds: Text
    check: Text
    status: Literal["todo", "unplanned", "done"]
    evidence: Optional[Text] = None
    note: Optional[Text] = None

    @model_validator(mode="after")
    def _evidence_when_done(self) -> Phase:
        if (self.status == "done") != (self.evidence is not None):
            raise ValueError("evidence is required when status is done, and only then")
        return self


class OpenItem(_Strict):
    question: Text
    assumption: Text


Event = Literal[
    "Planned", "Reviewed", "Built Phase", "Design changed", "Checked", "Evidence", "PR"
]


class Entry(_Strict):
    date: dt.date
    event: Event
    phase: Optional[int] = Field(default=None, ge=1)
    details: Text

    @model_validator(mode="after")
    def _phase_when_built(self) -> Entry:
        if (self.event == "Built Phase") != (self.phase is not None):
            raise ValueError(
                "phase is required when event is Built Phase, and only then"
            )
        return self


class Plan(_Strict):
    # `schema` would shadow a BaseModel attribute, so the field takes the key through its alias.
    schema_: Literal["plan/v2"] = Field(alias="schema")
    title: Line
    status: Literal["draft", "ready", "building", "built"]
    created: dt.date
    business_plan: Optional[Line] = None
    goal: Text
    scope: Scope
    design: list[Decision] = Field(min_length=1)
    phases: list[Phase] = Field(min_length=1)
    open: list[OpenItem]
    record: list[Entry] = Field(min_length=1)

    @model_validator(mode="after")
    def _status_matches_phases(self) -> Plan:
        done = sum(p.status == "done" for p in self.phases)
        if self.status == "built" and done < len(self.phases):
            raise ValueError("status built needs every phase done")
        if self.status == "building" and done == 0:
            raise ValueError("status building needs at least one phase done")
        if self.status in ("draft", "ready") and done:
            raise ValueError(f"status {self.status} allows no phase done, set building")
        return self


MODEL = Plan


def _bullet(text: str) -> str:
    """One Markdown bullet: continuation lines indented two spaces, blank lines kept blank."""
    lines = text.split("\n")
    return "- " + "\n".join([lines[0]] + [f"  {ln}" if ln else "" for ln in lines[1:]])


def _key(key: str, value: object) -> str:
    # safe_dump quotes a value only when YAML needs it, such as a title holding ": ".
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    # It quotes with ' and prettier rewrites that to ", so quote as a JSON string, valid YAML.
    # less-code: a value holding a " may still be requoted by prettier; escape it if one ever does.
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _status(p: Phase) -> str:
    if p.evidence:
        s = f"done, {p.evidence}"
        return f"{s} {p.note}" if p.note else s
    return f"{p.status}. {p.note}" if p.note else p.status


def render(plan: Plan, source: str) -> str:
    """The plan as plan/v1-layout Markdown. The same plan always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    front = [
        _key("schema", plan.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("title", plan.title),
    ]
    front += [_key("status", plan.status), _key("created", plan.created)]
    if plan.business_plan:
        front.append(_key("business_plan", plan.business_plan))
    # The ignore range keeps a formatter from rewriting the body, which would leave it stale.
    out = [
        "---",
        *front,
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        "## Goal",
        "",
        plan.goal,
        "",
        "## Scope",
        "",
        "**In:**",
        "",
    ]
    out += [_bullet(i) for i in plan.scope.in_]
    out += ["", "**Out:**", ""] + [
        _bullet(f"{o.item}: {o.reason}") for o in plan.scope.out
    ]
    out += ["", "## Design", ""]
    for d in plan.design:
        # A decision that opens with a list, table or code block starts on the line below its topic.
        sep = "\n" if d.decision.startswith(("- ", "| ", "```")) else " "
        out.append(_bullet(f"**{d.topic}**{sep}{d.decision}"))
    out += ["", "## Phases", ""]
    for n, p in enumerate(plan.phases, 1):
        out += [f"### Phase {n}: {p.name}", ""]
        out += [_bullet(f"**Builds:** {p.builds}"), _bullet(f"**Check:** {p.check}")]
        out += [_bullet(f"**Status:** {_status(p)}"), ""]
    out += ["## Open", ""]
    out += [_bullet(f"{o.question}: {o.assumption}") for o in plan.open] or ["None"]
    out += ["", "## Record", ""]
    for e in plan.record:
        event = f"{e.event} {e.phase}" if e.phase else e.event
        out.append(_bullet(f"{e.date.isoformat()} {event}: {e.details}"))
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
