"""session-retro/v3: the session diagnosis's model and its Markdown renderer.

The format in code, per session-retro-schema.md beside this file: `artifact.py` validates a
`<YYYYMMDD-HHMMSS>-<session-id>-session-<diagnosed-id>.yaml` with `MODEL` and writes
`render(doc, source)` beside it, in the `session-retro/v2` layout.
"""

from __future__ import annotations

import datetime as dt
import json
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NAME = "session-retro"
VERSION = 3

Line = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[^\n]*$")
]
# <transcript>:<line>, the quote-or-suppress anchor every claim carries.
Citation = Annotated[str, StringConstraints(pattern=r"^\S+:\d+$")]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class FirstWrongTurn(_Strict):
    citation: Citation
    quote: Line


class RootCause(_Strict):
    kind: Literal["Request", "Guidance", "Environment", "Model", "Claude Code"]
    cause: Line
    first_wrong_turn: FirstWrongTurn
    # From the first wrong turn through each step to the visible failure.
    chain: list[Line] = Field(min_length=2)
    route: Line
    status: Literal["handed off", "open", "dropped"]
    # The artifact handed off to, the user decision it waits on, or why it was dropped.
    status_detail: Line


class Finding(_Strict):
    lens: Line
    finding: Line
    citation: Citation


class Hypothesis(_Strict):
    cause: Line
    confirm: Line


class SessionRetro(_Strict):
    schema_: Literal["session-retro/v3"] = Field(alias="schema")
    session: Line
    date: dt.date
    transcript: Line
    subagent_transcripts: int = Field(ge=0)
    symptom: Line
    root_causes: list[RootCause]
    other_findings: list[Finding]
    hypotheses: list[Hypothesis]


MODEL = SessionRetro


def _key(key: str, value: object) -> str:
    line = yaml.safe_dump(
        {key: value}, sort_keys=False, allow_unicode=True, width=10**6
    ).strip()
    if line.startswith(f"{key}: '"):
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
    return line


def render(doc: SessionRetro, source: str) -> str:
    """The report in the session-retro/v2 layout. The same YAML always renders to the same text."""
    note = f"Do not edit. artifact.py renders this file from {source}: edit the YAML, then run artifact.py render."
    day = doc.date.isoformat()
    out = [
        "---",
        _key("schema", doc.schema_),
        _key("generated_from", source),
        _key("generated_note", note),
        _key("session", doc.session),
        f"date: {day}",
        "---",
        "",
        "<!-- prettier-ignore-start -->",
        "",
        f"# Session diagnosis: {doc.session}, {day}",
        "",
        f"**Transcript:** {doc.transcript} (+ {doc.subagent_transcripts} subagent transcripts)",
        f"**Symptom:** {doc.symptom}",
        "",
        "## Root causes",
        "",
    ]
    for n, r in enumerate(doc.root_causes, 1):
        out += [
            f"### {n}. {r.kind}: {r.cause}",
            "",
            f'- **First wrong turn:** `{r.first_wrong_turn.citation}` "{r.first_wrong_turn.quote}"',
            f"- **Chain:** {' → '.join(r.chain)}",
            f"- **Route:** {r.route}",
            f"- **Status:** {r.status}: {r.status_detail}",
            "",
        ]
    if not doc.root_causes:
        out += ["None", ""]
    out += ["## Other findings", ""]
    out += [f"- {f.lens}: {f.finding} `{f.citation}`" for f in doc.other_findings] or [
        "None"
    ]
    out += ["", "## Hypotheses", ""]
    out += [f"- {h.cause}: {h.confirm}" for h in doc.hypotheses] or ["None"]
    out += ["", "<!-- prettier-ignore-end -->"]
    return "\n".join(out) + "\n"
