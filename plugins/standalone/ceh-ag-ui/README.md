# ceh-ag-ui

Generative-UI canvases for agents that speak the [AG-UI](https://docs.ag-ui.com) protocol. The
user types, and the agent answers by placing components from a **catalogue fixed at build time**,
styled only by the theme (Meridian by default, from `ceh-ui-design:design-ui`). The agent picks
the component and fills in the content. It can never change how anything looks.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). `ceh-ui-design` arrives with this plugin
as a dependency: `build-ag-ui` and `add-canvas-component` call its `design-ui` skill on every run
for the theme and its token and class contract. The app the skills build also needs:

- **Bun (or Node.js 20+) and network access**: the canvas. `react`, `vite`, `zod` 4 and
  `@ag-ui/client` 1.x arrive as project dependencies.
- **uv and Python 3.11+**: the mock agent and the agent server (`fastapi`, `uvicorn`,
  `ag-ui-protocol` 1.x, `anthropic`).
- **Claude API credentials** (`ANTHROPIC_API_KEY` or an `ant auth login` profile): only for the
  server from `build-ag-ui-agent`. Without them the server starts but every run ends in `RUN_ERROR`.

## Skills

| Skill                  | Say or type                                                                                                                                               | What it does                                                                                                                                                                                                                                                            |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `build-ag-ui`          | "build a UI with AG-UI", "generative UI for my agent", `/ceh-ag-ui:build-ag-ui`                                                                           | Starts a generative-UI canvas for an AG-UI agent: uses your own template or copies the bundled one (React + Vite + `@ag-ui/client`, seven theme-styled catalogue components, a deterministic mock agent), installs the theme, and enforces the three-layer styling lock |
| `add-canvas-component` | "add a component the agent can show", "let the agent render a chart", `/ceh-ag-ui:add-canvas-component`, or loads by itself on an edit under `catalogue/` | Adds or changes a catalogue component: the tool name and agent-facing description, a content-only zod schema (no styling props), the example that doubles as a fixture, a theme-only component, and verification against the mock                                       |
| `build-ag-ui-agent`    | "build the AG-UI server", "connect Claude to my canvas", "replace the mock agent", `/ceh-ag-ui:build-ag-ui-agent`                                         | Builds the agent server behind the canvas: a bundled FastAPI + Claude server that keeps the model's own append-only transcript per thread, ends the run on a frontend tool call, and holds backend results until the canvas answers                                     |
| `add-live-state-panel` | "show the agent's progress live", "shared state", "sync state with the agent", `/ceh-ag-ui:add-live-state-panel`                                          | Adds a live value the agent updates as it works: `STATE_SNAPSHOT` / `STATE_DELTA` (JSON Patch), one writer per key, a fixed validated state panel, UI-to-agent state                                                                                                    |
| `add-human-approval`   | "ask the user before", "human in the loop", "approval step", `/ceh-ag-ui:add-human-approval`                                                              | Gets the user's decision before the agent acts: AG-UI 1.0 interrupts with the interrupt outcome, a fixed approval card, one `resume` covering every open interrupt, cancel-on-type, single-use approvals                                                                |

## Agents

This plugin has no agents.

## Hooks

This plugin has no hooks.

## Settings

This plugin reads no settings. The generated app reads `AGENT_ORIGIN` and `VITE_AGENT_URL`
(canvas) and `AGENT_MODEL` (server), each documented in the skill that writes it.

## How it works

### Build-time only

All five skills are **build-time**: Claude Code loads one while writing your app, and none runs
inside the running app. Worked examples, prompt by prompt:
[examples/README.md](examples/README.md).

### What lands in your project

`build-ag-ui` copies a default canvas (`web/`) and a no-LLM mock agent (`agent/`).
`build-ag-ui-agent` copies the Claude-backed AG-UI server (`main.py`, `pyproject.toml`).

## Not this plugin

- The visual design and theme of a page with no agent: `ceh-ui-design`.
- A SvelteKit or React frontend that is not an AG-UI canvas: `ceh-web-frontend`.
- A FastAPI web service that is not an AG-UI agent server: `ceh-python-service`.

## Where its files live

This plugin saves no files of its own. Its skills write the canvas and the agent server into your
project.
