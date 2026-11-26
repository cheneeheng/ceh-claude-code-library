"""orchestration-instance/v2: the orchestration file's model and its Markdown renderer.

The format in code, per orchestration-instance-schema.md beside this file: `artifact.py`
validates a `.agents_workspace/orchestration/<machine>.yaml` with `MODEL` and writes
`render(doc, source)` beside it.
"""

from __future__ import annotations

import json
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "orchestration-instance"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
WorkerName = Annotated[
    str, StringConstraints(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*-w[1-9]\d*$")
]
Time = Annotated[str, StringConstraints(pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")]
TaskId = Annotated[str, StringConstraints(pattern=r"^t[1-9]\d*$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


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
    name: WorkerName
    # Absent until the start command has printed the worker's id.
    session_id: Optional[Line] = None
    reports_to: Line
    model: Line
    worktree: Line
    branch: Line
    status: Literal["starting", "busy", "idle", "closed", "lost"]
    started: Time
    last_active: Time
    tasks: list[Task]


class Instance(_Strict):
    schema_: Literal["orchestration-instance/v2"] = Field(alias="schema")
    workers_started: int = Field(ge=0)
    workers: list[Worker]

    @model_validator(mode="after")
    def _agree(self):
        # The four cross-key rules of orchestration-instance-schema.md, and the only ones.
        for w in self.workers:
            for t in w.tasks:
                if t.status == "sent" and t.report is not None:
                    raise ValueError(f"{t.id} has a report while sent")
                if t.status != "sent" and t.report is None:
                    raise ValueError(f"{t.id} is {t.status} with no report")
            ids = [t.id for t in w.tasks]
            dupes = sorted({i for i in ids if ids.count(i) > 1})
            if dupes:
                raise ValueError(f"{w.name} uses task id {', '.join(dupes)} twice")
            if int(w.name.rsplit("-w", 1)[1]) > self.workers_started:
                raise ValueError(
                    f"{w.name} is numbered above workers_started {self.workers_started}"
                )
        names = [w.name for w in self.workers]
        dupes = sorted({n for n in names if names.count(n) > 1})
        if dupes:
            raise ValueError(f"worker name {', '.join(dupes)} is used twice")
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
    """The file header and one row per worker. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    rows = []
    for w in doc.workers:
        task = w.tasks[-1] if w.tasks else None
        rows.append(
            f"| {w.name} | {w.status} | {_cell(w.reports_to)} | {_cell(w.model)} | {_cell(w.branch)} | "
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
        f"# Orchestration: {source.rsplit('.', 1)[0]}",
        "",
        f"**Workers started:** {doc.workers_started}",
        "",
        "## Workers",
        "",
    ]
    if rows:
        out += [
            "| Worker | Status | Reports to | Model | Branch | Newest task | Task status |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            *rows,
        ]
    else:
        out.append("No workers.")
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
