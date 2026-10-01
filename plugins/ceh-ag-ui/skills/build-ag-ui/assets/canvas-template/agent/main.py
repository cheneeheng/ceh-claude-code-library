"""Mock AG-UI agent: no LLM, deterministic, so the canvas can be exercised end to end.

- Text naming a catalogue component ("show a bar chart") -> calls that frontend tool with the
  example arguments the canvas sent in the tool's metadata.
- `<tool-name> <json-args>` -> calls that tool with exactly those arguments (malformed or
  schema-breaking arguments included, to test the canvas rejects them).
- A tool result as the last message -> reports whether the canvas rendered it.
- Anything else -> echoes the text and lists what it can show.

Replace this file with a real agent; the canvas only depends on the AG-UI event stream.
"""

import json
import uuid
from collections.abc import AsyncIterator

from ag_ui.core import (
    BaseEvent,
    RunAgentInput,
    RunFinishedEvent,
    RunStartedEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
    TextMessageStartEvent,
    Tool,
    ToolCallArgsEvent,
    ToolCallEndEvent,
    ToolCallStartEvent,
)
from ag_ui.encoder import EventEncoder
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()


def say(text: str) -> list[BaseEvent]:
    message_id = str(uuid.uuid4())
    return [
        TextMessageStartEvent(message_id=message_id, role="assistant"),
        TextMessageContentEvent(message_id=message_id, delta=text),
        TextMessageEndEvent(message_id=message_id),
    ]


def call_tool(name: str, args: str) -> list[BaseEvent]:
    call_id = str(uuid.uuid4())
    return [
        ToolCallStartEvent(tool_call_id=call_id, tool_call_name=name),
        ToolCallArgsEvent(tool_call_id=call_id, delta=args),
        ToolCallEndEvent(tool_call_id=call_id),
    ]


def phrase(tool: Tool) -> str:
    return tool.name.removeprefix("show_").replace("_", " ")


def respond(run: RunAgentInput) -> list[BaseEvent]:
    tools = run.tools or []
    last = run.messages[-1] if run.messages else None
    if last is None:
        return say("Say something.")
    if last.role == "tool":
        content = last.content if isinstance(last.content, str) else ""
        return say(
            "Rendered on the canvas."
            if content == "rendered"
            else f"The canvas refused it: {content}"
        )
    text = last.content if isinstance(last.content, str) else ""
    name, _, args = text.strip().partition(" ")
    if name in {tool.name for tool in tools}:
        return call_tool(name, args or "{}")
    for tool in tools:
        example = (tool.metadata or {}).get("example")
        if example is not None and phrase(tool) in text.lower():
            return call_tool(tool.name, json.dumps(example))
    options = ", ".join(phrase(tool) for tool in tools) or "nothing yet"
    return say(f"You said: {text}\nI can show: {options}.")


@app.post("/agent")
async def agent(run: RunAgentInput, request: Request) -> StreamingResponse:
    encoder = EventEncoder(accept=request.headers.get("accept"))

    async def stream() -> AsyncIterator[str]:
        yield encoder.encode(
            RunStartedEvent(thread_id=run.thread_id, run_id=run.run_id)
        )
        events = respond(run)
        for event in events:
            yield encoder.encode(event)
        # A handler may end the run itself (e.g. with an interrupt outcome).
        if not (events and isinstance(events[-1], RunFinishedEvent)):
            yield encoder.encode(
                RunFinishedEvent(thread_id=run.thread_id, run_id=run.run_id)
            )

    return StreamingResponse(stream(), media_type=encoder.get_content_type())
