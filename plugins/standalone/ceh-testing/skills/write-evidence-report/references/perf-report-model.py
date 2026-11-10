"""perf-report/v2: the performance file's model and its Markdown renderer.

The format in code, per perf-report-schema.md beside this file: `artifact.py` validates a
`<metric>.yaml` with `MODEL` and writes `render(doc, source)` beside it, in the `perf-report/v1`
layout. Copied word for word into every skill that holds perf-report-schema.md.
"""

from __future__ import annotations

import json
from typing import Annotated, Literal, Optional, Union

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NAME = "perf-report"
VERSION = 2

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
# write-evidence-report runs `git log <commit>..HEAD` on it, so a name such as HEAD is refused.
Commit = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{7,40}$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Attempt(_Strict):
    attempt: Union[Literal["baseline"], Annotated[int, Field(ge=1)]]
    change: Line
    median: float
    low: float
    high: float
    within_noise: bool
    kept: bool
    kept_commit: Optional[Commit] = None

    @model_validator(mode="after")
    def _consistent(self) -> Attempt:
        if not self.low <= self.median <= self.high:
            raise ValueError("low <= median <= high must hold")
        if self.kept != (self.kept_commit is not None):
            raise ValueError("kept_commit is required exactly when kept is true")
        return self


class PerfReport(_Strict):
    schema_: Literal["perf-report/v2"] = Field(alias="schema")
    metric: Line
    commit: Commit
    command: Line
    machine: Line
    input: Line
    unit: Line
    spread: Literal["range", "iqr"]
    attempts: list[Attempt] = Field(min_length=1)

    @model_validator(mode="after")
    def _baseline_first(self) -> PerfReport:
        first, rest = self.attempts[0], self.attempts[1:]
        if first.attempt != "baseline":
            raise ValueError("attempts.0 must be the baseline")
        later = [n for n, a in enumerate(rest, 1) if a.attempt == "baseline"]
        if later:
            raise ValueError(f"attempts.{later[0]} is a second baseline")
        if first.within_noise:
            raise ValueError("within_noise must be false on the baseline")
        if first.kept:
            raise ValueError("kept must be false on the baseline")
        # less-code: a zero baseline has no percent change, so it is refused, not special-cased.
        if first.median <= 0:
            raise ValueError("the baseline median must be above 0")
        return self


MODEL = PerfReport


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def _num(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else str(x)


def render(doc: PerfReport, source: str) -> str:
    """The file in the perf-report/v1 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("metric", doc.metric),
        _key("commit", doc.commit),
        _key("command", doc.command),
        _key("machine", doc.machine),
        _key("input", doc.input),
        _key("unit", doc.unit),
        _key("spread", doc.spread),
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Performance: {doc.metric}",
        "",
        "| Attempt | Change | Median (spread) | vs baseline | Kept |",
        "| --- | --- | --- | --- | --- |",
    ]
    base = doc.attempts[0].median
    for a in doc.attempts:
        median = f"{_num(a.median)} {doc.unit} ({_num(a.low)}-{_num(a.high)})"
        if a.attempt == "baseline":
            vs, kept = "—", "—"
        else:
            pct = (a.median - base) / base * 100
            vs = "no measurable change" if a.within_noise else f"{pct:+.1f}%"
            kept = f"yes, {a.kept_commit}" if a.kept else "no"
        out.append(
            f"| {a.attempt} | {_cell(a.change)} | {_cell(median)} | {vs} | {kept} |"
        )
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
