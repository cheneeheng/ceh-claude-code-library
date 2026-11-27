"""orchestration-instance/v2: the orchestration file's model and its Markdown renderer.

The format in code, per orchestration-instance-schema.md beside this file: `artifact.py`
validates a `.agents_workspace/orchestration/<machine>.yaml` with `MODEL` and writes
`render(doc, source)` beside it.
"""

from __future__ import annotations

import json
from typing import Annotated, Literal, Optional, Union

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
# "." or /-joined segments inside the hub: no leading /, drive letter, backslash, or segment
# starting with "." (so no "..", and no .claude/worktrees).
RepoPath = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        pattern=r"^(\.|[^/\\:.\n][^/\\:\n]*(/[^/\\:.\n][^/\\:\n]*)*)$",
    ),
]


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
    status: Literal["sent", "reported", "accepted", "rejected", "answered"]
    report: Optional[Report] = None


class Worker(_Strict):
    name: WorkerName
    # Absent until the start command has printed the worker's id.
    session_id: Optional[Line] = None
    reports_to: Line
    model: Line
    # The worker's repository, relative to the hub. Absent reads as ".".
    repo: Optional[RepoPath] = None
    worktree: Line
    branch: Line
    status: Literal["starting", "busy", "idle", "closed", "lost"]
    started: Time
    last_active: Time
    tasks: list[Task]


class Held(_Strict):
    goal: Line
    scope: Line
    inputs: list[Line]
    done_when: Line
    commit: bool
    held: Time
    model: Optional[Line] = None
    # Queued for this worker: a land, or the next task of its chain.
    worker: Optional[WorkerName] = None
    # Goes to the same worker as the entry before it.
    follows: Optional[Literal[True]] = None
    # A fresh or waiting entry's repository, relative to the hub. Absent reads as ".".
    repo: Optional[RepoPath] = None
    # Waits for this worker to land, or with true for the worker the nearest fresh entry before
    # it will start.
    after: Optional[Union[WorkerName, Literal[True]]] = None


class Instance(_Strict):
    schema_: Literal["orchestration-instance/v2"] = Field(alias="schema")
    workers_started: int = Field(ge=0)
    workers: list[Worker]
    held: list[Held] = []

    @model_validator(mode="after")
    def _agree(self):
        # The six cross-key rules of orchestration-instance-schema.md, and the only ones.
        for w in self.workers:
            if (w.repo or ".") != "." and w.worktree == "none":
                raise ValueError(f"{w.name} has repo {w.repo} with worktree none")
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
        for i, h in enumerate(self.held):
            if h.worker and h.follows:
                raise ValueError(f"held.{i} has both worker and follows")
            if h.follows and i == 0:
                raise ValueError(f"held.{i} has follows with no entry before it")
            if h.worker and h.worker not in names:
                raise ValueError(
                    f"held.{i} names worker {h.worker}, which is not in the file"
                )
            if h.repo and (h.worker or h.follows):
                raise ValueError(f"held.{i} has repo with worker or follows")
            if h.after is None:
                continue
            if h.worker or h.follows:
                raise ValueError(f"held.{i} has after with worker or follows")
            if h.after is True:
                # The nearest entry before it that is no follows entry must be fresh.
                j = i - 1
                while j >= 0 and self.held[j].follows:
                    j -= 1
                if j < 0 or self.held[j].worker or self.held[j].after is not None:
                    raise ValueError(
                        f"held.{i} has after true with no fresh entry before it"
                    )
            elif h.after not in names:
                raise ValueError(
                    f"held.{i} waits for worker {h.after}, which is not in the file"
                )
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


def _waits(h: Held) -> str:
    """The held table's Worker cell: whom the entry goes to, or waits for."""
    if h.after is not None:
        return f"after {'previous' if h.after is True else h.after}"
    return h.worker or ("follows" if h.follows else "fresh")


def render(doc: Instance, source: str) -> str:
    """The file header and one row per worker. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    rows = []
    for w in doc.workers:
        task = w.tasks[-1] if w.tasks else None
        rows.append(
            f"| {w.name} | {_cell(w.repo or '.')} | {w.status} | {_cell(w.reports_to)} | {_cell(w.model)} | {_cell(w.branch)} | "
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
            "| Worker | Repo | Status | Reports to | Model | Branch | Newest task | Task status |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
            *rows,
        ]
    else:
        out.append("No workers.")
    if doc.held:
        out += [
            "",
            "## Held tasks",
            "",
            "| Held | Goal | Model | Worker | Repo |",
            "| --- | --- | --- | --- | --- |",
            *(
                f"| {h.held} | {_cell(h.goal)} | {_cell(h.model or 'by task')} | {_waits(h)} | "
                f"{'-' if h.worker or h.follows else _cell(h.repo or '.')} |"
                for h in doc.held
            ),
        ]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
