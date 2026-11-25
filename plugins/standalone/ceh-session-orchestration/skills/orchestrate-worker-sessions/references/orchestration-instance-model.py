"""orchestration-instance/v1: the orchestration instance's model and its Markdown renderer.

The format in code, per orchestration-instance-schema.md beside this file: `artifact.py`
validates a `.agents_workspace/orchestration/<YYYYMMDD-HHMMSS>-<name>.yaml` with `MODEL` and
writes `render(doc, source)` beside it.
"""

from __future__ import annotations

import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "orchestration-instance"
VERSION = 1

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
Slug = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")]
Time = Annotated[str, StringConstraints(pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")]
TaskId = Annotated[str, StringConstraints(pattern=r"^t[1-9]\d*$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Orchestrator(_Strict):
    session_id: Line
    session_name: Line


class Check(_Strict):
    command: Line
    result: Line


class Report(_Strict):
    received: Time
    status: Literal["done", "blocked", "failed"]
    summary: Line
    files: list[Line]
    checks: list[Check]
    needs_user: Line


class Task(_Strict):
    id: TaskId
    goal: Line
    scope: Line
    inputs: list[Line]
    done_when: Line
    commit: bool
    sent: Time
    status: Literal["sent", "reported", "accepted", "rejected"]
    report: Optional[Report] = None


class Worker(_Strict):
    name: Slug
    # Absent until the start command has printed the worker's id.
    session_id: Optional[Line] = None
    worktree: Line
    branch: Line
    status: Literal["starting", "busy", "idle", "closed", "lost"]
    started: Time
    last_active: Time
    tasks: list[Task]


class Instance(_Strict):
    schema_: Literal["orchestration-instance/v1"] = Field(alias="schema")
    name: Slug
    status: Literal["open", "closed"]
    created: Time
    updated: Time
    orchestrator: Orchestrator
    worker_model: Line
    workers: list[Worker]

    @model_validator(mode="after")
    def _agree(self):
        # The four cross-key rules of orchestration-instance-schema.md, and the only ones.
        tasks = [t for w in self.workers for t in w.tasks]
        for t in tasks:
            if t.status == "sent" and t.report is not None:
                raise ValueError(f"{t.id} has a report while sent")
            if t.status != "sent" and t.report is None:
                raise ValueError(f"{t.id} is {t.status} with no report")
        for kind, names in (
            ("task id", [t.id for t in tasks]),
            ("worker name", [w.name for w in self.workers]),
        ):
            dupes = sorted({n for n in names if names.count(n) > 1})
            if dupes:
                raise ValueError(f"{kind} {', '.join(dupes)} is used twice")
        if self.status == "closed":
            for w in self.workers:
                if w.status in ("starting", "busy", "idle"):
                    raise ValueError(f"closed while {w.name} is {w.status}")
        return self


MODEL = Instance


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def render(doc: Instance, source: str) -> str:
    """The instance header and one row per worker. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    rows = []
    for w in doc.workers:
        task = w.tasks[-1] if w.tasks else None
        rows.append(
            f"| {w.name} | {w.status} | {_cell(w.branch)} | "
            + (
                f"{task.id}: {_cell(task.goal)} | {task.status} |"
                if task
                else "none | - |"
            )
        )
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Orchestration instance: {doc.name}",
        "",
        f"**Status:** {doc.status}",
        f"**Created / updated:** {doc.created} / {doc.updated}",
        f"**Orchestrator:** {doc.orchestrator.session_name} ({doc.orchestrator.session_id})",
        f"**Worker model:** {doc.worker_model}",
        "",
        "## Workers",
        "",
    ]
    if rows:
        out += [
            "| Worker | Status | Branch | Newest task | Task status |",
            "| --- | --- | --- | --- | --- |",
            *rows,
        ]
    else:
        out.append("No workers yet.")
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
