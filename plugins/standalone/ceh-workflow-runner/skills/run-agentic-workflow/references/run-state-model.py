"""run-state/v2: the run state's model and its Markdown renderer.

The format in code, per run-state-schema.md beside this file: `artifact.py` validates a
`{run}/run-state.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the
`run-state/v1` layout. Copied word for word into every skill that holds run-state-schema.md.
"""

from __future__ import annotations

import json
import re
from typing import Annotated, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "run-state"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
Slug = Annotated[str, StringConstraints(pattern=rf"^{SLUG}$")]
RunId = Annotated[str, StringConstraints(pattern=r"^\d{8}-\d{4}(-\d+)?$")]
Time = Annotated[
    str,
    StringConstraints(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:\d{2})?$"
    ),
]
Source = Annotated[
    str, StringConstraints(pattern=rf"^(interactive|resume-prompt|approve={SLUG})$")
]
STATUS = re.compile(rf"^(done|awaiting-approval ({SLUG})|failed ({SLUG}|-) \S.*)$")


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Input(_Strict):
    name: Slug
    value: Line


class Stage(_Strict):
    id: Slug
    state: Literal["pending", "done", "awaiting-approval", "failed"]
    artifacts: list[Line]
    note: Optional[Line] = None


class Approval(_Strict):
    stage: Slug
    decision: Literal["approved", "rejected"]
    source: Source
    at: Time


class RunState(_Strict):
    schema_: Literal["run-state/v2"] = Field(alias="schema")
    flow: Slug
    run_id: RunId
    config: Line
    mode: Literal["interactive", "headless"]
    inputs: list[Input]
    stages: list[Stage] = Field(min_length=1)
    approvals: list[Approval]
    status: Optional[Line] = None

    @model_validator(mode="after")
    def _agree(self):
        ids = [s.id for s in self.stages]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise ValueError(f"stages: duplicate id {', '.join(dupes)}")
        state = {s.id: s.state for s in self.stages}
        waiting = [i for i in ids if state[i] == "awaiting-approval"]
        if len(waiting) > 1:
            raise ValueError(
                f"stages: {', '.join(waiting)} are awaiting-approval, at most one may be"
            )
        for a in self.approvals:
            if a.stage not in state:
                raise ValueError(f"approvals: {a.stage} names no stage")
            if a.source.startswith("approve=") and a.source != f"approve={a.stage}":
                raise ValueError(f"approvals: {a.stage} has source {a.source}")
        if self.status is None:
            return self
        m = STATUS.match(self.status)
        if not m:
            raise ValueError(
                f"status: {self.status!r} is not done, awaiting-approval <stage-id>"
                " or failed <stage-id or -> <reason>"
            )
        if self.status == "done":
            if any(state[i] != "done" for i in ids):
                raise ValueError("status: done while a stage is not done")
        elif m.group(2):
            if state.get(m.group(2)) != "awaiting-approval":
                raise ValueError(
                    f"status: {m.group(2)} is not an awaiting-approval stage"
                )
        elif m.group(3) != "-" and m.group(3) not in state:
            raise ValueError(f"status: failed {m.group(3)} names no stage")
        return self


MODEL = RunState


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def render(doc: RunState, source: str) -> str:
    """The run state in the run-state/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        "---",
        "",
        # No blank line after the start marker or before FLOW STATUS: without the two markers, the
        # body is the v1 layout line for line, and the status stays the file's last line.
        "<!-- prettier-ignore-start -->",
        f"# Run state: {doc.flow}/{doc.run_id}",
        "",
        f"flow: {doc.flow}",
        f"config: {doc.config}",
        f"mode: {doc.mode}",
        "inputs: " + (", ".join(f"{i.name}={i.value}" for i in doc.inputs) or "-"),
        "",
        "## Stages",
        "",
        *(
            f"- {s.id}: {s.state} | {', '.join(s.artifacts) or '-'} | {s.note or '-'}"
            for s in doc.stages
        ),
        "",
        "## Approvals",
        "",
        *(
            [f"- {a.stage}: {a.decision} | {a.source} | {a.at}" for a in doc.approvals]
            or ["- none"]
        ),
        "",
        "<!-- prettier-ignore-end -->",
    ]
    if doc.status is not None:
        out.append(f"FLOW STATUS: {doc.status}")
    return "\n".join(out) + "\n"
