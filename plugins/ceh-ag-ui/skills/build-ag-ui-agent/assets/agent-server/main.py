"""AG-UI agent server backed by Claude, for a generative-UI canvas.

The canvas sends its catalogue as frontend tools on every run. Claude answers with text and/or a
call to one of them; the server streams both as AG-UI events and ends the run on a frontend call,
because the canvas renders it and sends the result back as a new run.

Claude keeps its own transcript per thread (thinking blocks included) and only the new AG-UI
messages are folded in, so the history stays append-only: the prompt cache stays warm and
thinking blocks stay valid.
"""

import os
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from ag_ui.core import (
    BaseEvent,
    RunAgentInput,
    RunErrorEvent,
    RunFinishedEvent,
    RunStartedEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
    TextMessageStartEvent,
    ToolCallArgsEvent,
    ToolCallEndEvent,
    ToolCallResultEvent,
    ToolCallStartEvent,
)
from ag_ui.encoder import EventEncoder
from anthropic import AsyncAnthropic
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

MODEL = os.environ.get("AGENT_MODEL", "claude-opus-5-5")
SYSTEM = (
    "You answer inside a canvas. When one of the component tools fits the answer, call it with "
    "real content and keep any text to a sentence or two around it. Use plain text only when no "
    "component fits. How components look is fixed by the app; never try to style them."
)

# Tools this server runs itself: name -> (description, JSON Schema, handler). Handlers must
# validate their input: with eager input streaming the API does not.
BackendTool = tuple[str, dict[str, Any], Callable[[dict[str, Any]], Awaitable[str]]]
BACKEND_TOOLS: dict[str, BackendTool] = {}


@dataclass
class Thread:
    transcript: list[Any] = field(
        default_factory=list
    )  # Claude's view, thinking blocks included
    seen: set[str] = field(default_factory=set)  # AG-UI message ids already folded in
    awaiting: set[str] = field(
        default_factory=set
    )  # frontend tool_use ids with no result yet
    held: list[dict[str, Any]] = field(
        default_factory=list
    )  # backend results sent with those


# less-code: in-memory and single-process; lost on restart and not shared between replicas.
# Move to a store keyed by thread_id (Redis, Postgres) before running more than one instance.
THREADS: dict[str, Thread] = {}

client = AsyncAnthropic()
app = FastAPI()


def text_of(content: Any) -> str:
    if isinstance(content, str):
        return content
    return "".join(getattr(part, "text", "") for part in content or [])


def fold_in(thread: Thread, run: RunAgentInput) -> None:
    """Append the user's new text and the canvas's tool results as one user turn."""
    results: dict[str, dict[str, Any]] = {}
    texts: list[str] = []
    for message in run.messages:
        if message.id in thread.seen:
            continue
        thread.seen.add(message.id)
        if message.role == "tool" and message.tool_call_id in thread.awaiting:
            results[message.tool_call_id] = {
                "type": "tool_result",
                "tool_use_id": message.tool_call_id,
                "content": text_of(message.content),
                "is_error": text_of(message.content).startswith("error"),
            }
        elif message.role == "user":
            texts.append(text_of(message.content))
        # Assistant messages are this server's own output; client-sent system/developer
        # messages are ignored so the browser cannot rewrite the system prompt.
    # A call the canvas never answered (the user pressed Stop) still needs a result.
    for call_id in thread.awaiting - results.keys():
        results[call_id] = {
            "type": "tool_result",
            "tool_use_id": call_id,
            "is_error": True,
            "content": "The user interrupted before this was shown.",
        }
    blocks = (
        thread.held
        + list(results.values())
        + [{"type": "text", "text": t} for t in texts if t]
    )
    thread.awaiting, thread.held = set(), []
    if blocks:
        thread.transcript.append({"role": "user", "content": blocks})


def echoable(content: list[Any]) -> list[Any]:
    """After a mid-output fallback, only text from before the last fallback block is echoed."""
    cut = max((i for i, b in enumerate(content) if b.type == "fallback"), default=None)
    if cut is None:
        return content
    return [b for b in content[:cut] if b.type == "text"] + content[cut:]


async def run_claude(thread: Thread, run: RunAgentInput) -> AsyncIterator[BaseEvent]:
    frontend = {tool.name for tool in run.tools or []}
    tools = [
        {
            "name": t.name,
            "description": t.description,
            "eager_input_streaming": True,
            "input_schema": t.parameters or {"type": "object"},
        }
        for t in run.tools or []
    ] + [
        {
            "name": name,
            "description": desc,
            "input_schema": schema,
            "eager_input_streaming": True,
        }
        for name, (desc, schema, _) in BACKEND_TOOLS.items()
    ]
    while True:
        async with client.beta.messages.stream(
            model=MODEL,
            max_tokens=64000,
            system=SYSTEM,
            tools=tools,
            messages=thread.transcript,
            output_config={"effort": "medium"},
            fallbacks="default",
            betas=["server-side-fallback-2026-07-01"],
        ) as stream:
            open_blocks: dict[
                int, tuple[str, str]
            ] = {}  # block index -> (kind, AG-UI id)
            async for event in stream:
                if event.type == "content_block_start":
                    block = event.content_block
                    if block.type == "text":
                        open_blocks[event.index] = ("text", str(uuid.uuid4()))
                        yield TextMessageStartEvent(
                            message_id=open_blocks[event.index][1], role="assistant"
                        )
                    elif block.type == "tool_use":
                        open_blocks[event.index] = ("tool", block.id)
                        yield ToolCallStartEvent(
                            tool_call_id=block.id, tool_call_name=block.name
                        )
                elif event.type == "content_block_delta" and event.index in open_blocks:
                    block_id = open_blocks[event.index][1]
                    if event.delta.type == "text_delta":
                        yield TextMessageContentEvent(
                            message_id=block_id, delta=event.delta.text
                        )
                    elif event.delta.type == "input_json_delta":
                        yield ToolCallArgsEvent(
                            tool_call_id=block_id, delta=event.delta.partial_json
                        )
                elif event.type == "content_block_stop" and event.index in open_blocks:
                    kind, block_id = open_blocks.pop(event.index)
                    if kind == "tool":
                        yield ToolCallEndEvent(tool_call_id=block_id)
                    else:
                        yield TextMessageEndEvent(message_id=block_id)
            final = await stream.get_final_message()

        thread.transcript.append(
            {"role": "assistant", "content": echoable(final.content)}
        )
        calls = [b for b in final.content if b.type == "tool_use"]
        if final.stop_reason == "refusal":
            yield RunErrorEvent(
                message="The model declined this request.", code="refusal"
            )
            return
        if final.stop_reason == "max_tokens" and calls:
            yield RunErrorEvent(
                message="A tool call was cut off by max_tokens.", code="max_tokens"
            )
            return
        if final.stop_reason == "pause_turn":
            continue
        if final.stop_reason != "tool_use":
            return

        results: list[dict[str, Any]] = []
        for call in (c for c in calls if c.name not in frontend):
            if call.name in BACKEND_TOOLS:
                output = await BACKEND_TOOLS[call.name][2](call.input)
                results.append(
                    {"type": "tool_result", "tool_use_id": call.id, "content": output}
                )
            else:
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": call.id,
                        "is_error": True,
                        "content": f"Unknown tool {call.name}.",
                    }
                )
            yield ToolCallResultEvent(
                message_id=str(uuid.uuid4()),
                tool_call_id=call.id,
                content=results[-1]["content"],
            )
        thread.awaiting = {c.id for c in calls if c.name in frontend}
        if thread.awaiting:
            thread.held = (
                results  # sent together with the canvas's results, in one user turn
            )
            return
        thread.transcript.append({"role": "user", "content": results})


@app.post("/agent")
async def agent(run: RunAgentInput, request: Request) -> StreamingResponse:
    encoder = EventEncoder(accept=request.headers.get("accept"))
    thread = THREADS.setdefault(run.thread_id, Thread())
    fold_in(thread, run)

    async def stream() -> AsyncIterator[str]:
        yield encoder.encode(
            RunStartedEvent(thread_id=run.thread_id, run_id=run.run_id)
        )
        try:
            async for event in run_claude(thread, run):
                yield encoder.encode(event)
                if isinstance(event, RunErrorEvent):
                    return
        except Exception as exc:  # noqa: BLE001 — every failure must end the run with RUN_ERROR
            yield encoder.encode(
                RunErrorEvent(message=str(exc), code=type(exc).__name__)
            )
            return
        yield encoder.encode(
            RunFinishedEvent(thread_id=run.thread_id, run_id=run.run_id)
        )

    return StreamingResponse(stream(), media_type=encoder.get_content_type())
