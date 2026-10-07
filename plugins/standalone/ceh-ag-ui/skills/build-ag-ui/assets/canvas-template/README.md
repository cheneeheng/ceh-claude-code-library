# AG-UI canvas template

A generative-UI canvas for an [AG-UI](https://docs.ag-ui.com) agent: a component area, a chat panel,
and a catalogue of components the agent can place. Each catalogue entry in `web/src/catalogue/` is
sent to the agent as a frontend tool; when the agent calls one, the canvas validates the arguments
against the entry's zod schema and renders it. Styling comes only from the theme, never the agent.

```bash
# once — install the theme (Tidewater by default; Meridian swaps in with no markup changes)
cp <ceh-ui-design design-ui>/references/tidewater/brand.css web/src/brand.css

# terminal 1 — mock agent on :8000 (swap for your real AG-UI endpoint)
cd agent && uv run uvicorn main:app --port 8000

# terminal 2 — canvas on :5173, proxies /agent to :8000 (override with AGENT_ORIGIN)
cd web && bun install && bun run dev
```

The mock agent needs no LLM: "show a bar chart" places that component with its example arguments,
and `<tool-name> <json-args>` sends exact arguments, so every component can be tested.
