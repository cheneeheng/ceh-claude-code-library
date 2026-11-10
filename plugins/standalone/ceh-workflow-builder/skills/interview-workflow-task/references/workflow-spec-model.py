"""workflow-spec/v2: the workflow spec's model and its Markdown renderer.

The format in code, per workflow-spec-schema.md beside this file: `artifact.py` validates a
`<name>-workflow-spec.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the
`workflow-spec/v1` layout. Copied word for word into every skill that holds
workflow-spec-schema.md.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal, Optional, Union

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "workflow-spec"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
Slug = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]
StepNo = Annotated[int, Field(ge=1)]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Unanswered(_Strict):
    state: Literal["unanswered"]
    question: Line


class Declined(_Strict):
    state: Literal["declined"]
    words: Line


class DeclinedAssumed(_Strict):
    """Rows 8 and 9 only: the builder's Declined table allows an assumption on no other row."""

    state: Literal["declined"]
    words: Line
    assumption: Optional[Line] = None


class Moment(_Strict):
    state: Literal["answered"]
    answer: Line


class Step(_Strict):
    n: StepNo
    step: Line


class Procedure(_Strict):
    state: Literal["answered"]
    steps: list[Step] = Field(min_length=1)

    @model_validator(mode="after")
    def _numbered(self):
        if [s.n for s in self.steps] != list(range(1, len(self.steps) + 1)):
            raise ValueError("steps are numbered 1, 2, 3 in order")
        return self


class ProofStep(_Strict):
    n: StepNo
    before: Line
    by: Literal["command", "file", "human"]
    check: Line


class Proof(_Strict):
    state: Literal["answered"]
    steps: list[ProofStep]


class Read(_Strict):
    model_config = ConfigDict(populate_by_name=True)
    artifact: Line
    from_: Union[StepNo, Literal["run start"]] = Field(alias="from")


class FlowStep(_Strict):
    n: StepNo
    reads: list[Read]
    leaves: list[Line]


class DataFlow(_Strict):
    state: Literal["answered"]
    starts_from: Line
    steps: list[FlowStep]


class ToolStep(_Strict):
    n: StepNo
    needs: list[Line]


class Tooling(_Strict):
    state: Literal["answered"]
    steps: list[ToolStep]


class Done(_Strict):
    state: Literal["answered"]
    answer: list[Line] = Field(min_length=1)


class Interruption(_Strict):
    state: Literal["answered"]
    answer: Literal["one sitting", "resumable"]


class UnsafeStep(_Strict):
    n: StepNo
    why: Line


class RerunUnsafe(_Strict):
    state: Literal["answered"]
    steps: list[UnsafeStep]
    note: Optional[Line] = None


class EffectStep(_Strict):
    n: StepNo
    effect: Line


class Irreversible(_Strict):
    state: Literal["answered"]
    steps: list[EffectStep]


def _row(answered, declined=Declined):
    return Annotated[
        Union[answered, Unanswered, declined], Field(discriminator="state")
    ]


# The nine rows in question order: (key, heading).
ROWS = [
    ("moment", "Moment"),
    ("procedure", "Manual procedure"),
    ("proof", "Preconditions and proof"),
    ("data_flow", "Data flow"),
    ("tooling", "Tooling"),
    ("done", "Done"),
    ("interruption", "Interruption"),
    ("rerun_unsafe", "Unsafe to re-run"),
    ("irreversible", "Irreversible steps"),
]
STEP_ROWS = ("proof", "data_flow", "tooling", "rerun_unsafe", "irreversible")


class WorkflowSpec(_Strict):
    schema_: Literal["workflow-spec/v2"] = Field(alias="schema")
    name: Slug
    date: dt.date
    moment: _row(Moment)
    procedure: _row(Procedure)
    proof: _row(Proof)
    data_flow: _row(DataFlow)
    tooling: _row(Tooling)
    done: _row(Done)
    interruption: _row(Interruption)
    rerun_unsafe: _row(RerunUnsafe, DeclinedAssumed)
    irreversible: _row(Irreversible, DeclinedAssumed)

    @model_validator(mode="after")
    def _steps_agree(self):
        """Questions 2 to 4 read as one table, so every step number names a procedure step."""
        answered = [k for k in STEP_ROWS if getattr(self, k).state == "answered"]
        if self.procedure.state != "answered":
            if answered:
                raise ValueError(
                    f"{', '.join(answered)} answered while procedure is not"
                )
            return self
        steps = [s.n for s in self.procedure.steps]
        for key in answered:
            got = [s.n for s in getattr(self, key).steps]
            if key in ("proof", "data_flow"):
                if got != steps:
                    raise ValueError(
                        f"{key}: steps {got} do not match procedure steps {steps}"
                    )
            elif not set(got) <= set(steps):
                raise ValueError(f"{key}: steps {got} name no procedure step")
        if self.data_flow.state == "answered":
            for s in self.data_flow.steps:
                for r in s.reads:
                    if r.from_ != "run start" and r.from_ >= s.n:
                        raise ValueError(
                            f"data_flow: step {s.n} reads {r.artifact} from step {r.from_},"
                            " not an earlier step: a later step's output comes from run start"
                        )
        return self


MODEL = WorkflowSpec


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _list(items: list[str]) -> str:
    return ", ".join(items) or "nothing"


def _answered(key: str, row) -> list[str]:
    if key in ("moment", "interruption"):
        return [row.answer]
    if key == "done":
        return [f"- {a}" for a in row.answer]
    if key == "procedure":
        return [f"{s.n}. {s.step}" for s in row.steps]
    if key == "proof":
        return [
            f"{s.n}. Before: {s.before}. Proof ({s.by}): {s.check}" for s in row.steps
        ]
    if key == "data_flow":
        return [
            f"Starts from: {row.starts_from}",
            "",
            *(
                f"{s.n}. Reads: "
                + _list(
                    [
                        f"{r.artifact} (from {'run start' if r.from_ == 'run start' else f'step {r.from_}'})"
                        for r in s.reads
                    ]
                )
                + f". Leaves: {_list(s.leaves)}."
                for s in row.steps
            ),
        ]
    if key == "tooling":
        return [f"{s.n}. Needs: {_list(s.needs)}" for s in row.steps]
    detail = "why" if key == "rerun_unsafe" else "effect"
    out = [f"- Step {s.n}: {getattr(s, detail)}" for s in row.steps] or ["None."]
    if getattr(row, "note", None):
        out += ["", f"Note: {row.note}"]
    return out


def _body(key: str, row) -> list[str]:
    if row.state == "unanswered":
        return [f"Unanswered: {row.question}"]
    if row.state == "declined":
        out = [f"Declined: {row.words}"]
        if getattr(row, "assumption", None):
            out += ["", f"Assumed: {row.assumption}"]
        return out
    return _answered(key, row)


def render(doc: WorkflowSpec, source: str) -> str:
    """The spec in the workflow-spec/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("name", doc.name),
        f"date: {doc.date.isoformat()}",
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# {doc.name} workflow spec",
        "",
    ]
    for n, (key, title) in enumerate(ROWS, 1):
        out += [f"## {n}. {title}", "", *_body(key, getattr(doc, key)), ""]
    out.append("<!-- prettier-ignore-end -->")
    return "\n".join(out) + "\n"
