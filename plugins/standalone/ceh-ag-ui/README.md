# ceh-ag-ui

Generative-UI canvases for agents that speak the [AG-UI](https://docs.ag-ui.com) protocol. The
user types, and the agent answers by placing components from a **catalogue fixed at build time**,
styled only by the theme (Tidewater by default, from `ceh-ui-design:design-ui`). The agent picks
the component and fills in the content. It can never change how anything looks.

All five skills are **build-time**: Claude Code loads one while writing your app, and none runs
inside the running app. Worked examples, prompt by prompt:
[examples/ceh-ag-ui](https://github.com/cheneeheng/ceh-claude-code-library/tree/main/examples/ceh-ag-ui).

## Skills

| Skill                  | Invoke                            | Triggers when                                                                                                                                                                                                                                                                       |
| ---------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `build-ag-ui`          | `/ceh-ag-ui:build-ag-ui`          | Starting a generative-UI canvas for an AG-UI agent: uses the user's own template or copies the bundled one (React + Vite + `@ag-ui/client`, seven Tidewater-styled catalogue components, a deterministic mock agent), installs the theme, and enforces the three-layer styling lock |
| `add-canvas-component` | `/ceh-ag-ui:add-canvas-component` | Adding or changing a catalogue component: the tool name and agent-facing description, a content-only zod schema (no styling props), the example that doubles as a fixture, a theme-only component, and verification against the mock                                                |
| `build-ag-ui-agent`    | `/ceh-ag-ui:build-ag-ui-agent`    | Building the agent server behind the canvas: a bundled FastAPI + Claude server that keeps the model's own append-only transcript per thread, ends the run on a frontend tool call, and holds backend results until the canvas answers                                               |
| `add-live-state-panel` | `/ceh-ag-ui:add-live-state-panel` | The canvas needs a live value the agent updates as it works: `STATE_SNAPSHOT` / `STATE_DELTA` (JSON Patch), one writer per key, a fixed validated state panel, UI-to-agent state                                                                                                    |
| `add-human-approval`   | `/ceh-ag-ui:add-human-approval`   | The agent must get the user's decision before acting: AG-UI 1.0 interrupts with the interrupt outcome, a fixed approval card, one `resume` covering every open interrupt, cancel-on-type, single-use approvals                                                                      |

## Prerequisites

- **`ceh-ui-design`**: installed automatically as a dependency. `build-ag-ui` and
  `add-canvas-component` call its `design-ui` skill on every run for the theme and its token and
  class contract.
- **Bun (or Node.js 20+) and network access**: the canvas. `react`, `vite`, `zod` 4 and
  `@ag-ui/client` 1.x arrive as project dependencies.
- **uv and Python 3.11+**: the mock agent and the agent server (`fastapi`, `uvicorn`,
  `ag-ui-protocol` 1.x, `anthropic`).
- **Claude API credentials** (`ANTHROPIC_API_KEY` or an `ant auth login` profile): only for the
  server from `build-ag-ui-agent`. Without them the server starts but every run ends in `RUN_ERROR`.

The plugin itself reads no environment variables. The generated app reads `AGENT_ORIGIN` and
`VITE_AGENT_URL` (canvas) and `AGENT_MODEL` (server), each documented in the skill that writes it.

## Bundled assets

| Path                                            | What it is                                                       |
| ----------------------------------------------- | ---------------------------------------------------------------- |
| `skills/build-ag-ui/assets/canvas-template/`    | The default canvas (`web/`) and the no-LLM mock agent (`agent/`) |
| `skills/build-ag-ui-agent/assets/agent-server/` | The Claude-backed AG-UI server (`main.py`, `pyproject.toml`)     |
