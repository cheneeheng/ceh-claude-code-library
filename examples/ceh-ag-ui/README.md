# Using `ceh-ag-ui` — worked examples

Every `ceh-ag-ui` skill is a **build-time** skill. You ask Claude Code for a feature, and it loads
the matching skill and writes the code. Once the app is running, no skill is involved. The canvas
and the agent server talk to each other over AG-UI through the code the skills wrote.

```
you, in Claude Code ──► skill loads ──► code lands in your repo ──► you run the app
                                                                      │
                             end user types in the canvas ◄───────────┘
                             the agent places components, updates panels, asks for approval
```

| When you're building…                        | Skill                            | What it adds to your app                        |
| -------------------------------------------- | -------------------------------- | ----------------------------------------------- |
| a new agent canvas                           | `ceh-ag-ui:build-ag-ui`          | `web/` canvas + seven components, `agent/` mock |
| a component the agent should be able to show | `ceh-ag-ui:add-canvas-component` | one file in `web/src/catalogue/`                |
| the real backend                             | `ceh-ag-ui:build-ag-ui-agent`    | a FastAPI + Claude server                       |
| a panel that updates while the agent works   | `ceh-ag-ui:add-live-state-panel` | a fixed panel, and agent code that feeds it     |
| a step where the agent must ask first        | `ceh-ag-ui:add-human-approval`   | an approval card, and agent code that pauses    |

The prompts below are what you type into Claude Code. Any wording that describes the same moment
triggers the skill, and you can always invoke one directly with `/ceh-ag-ui:<skill>`.

Install: `/plugin install ceh-ag-ui@ceh-claude-code-library`. This brings `ceh-web-frontend` with it, for the
theme.

---

## 1. Start a canvas from nothing

> Build me an AG-UI canvas for a sales assistant. Put it in `apps/assistant`.

**Skill:** `build-ag-ui`. It uses Tidewater without asking, unless you name another theme.

**What happens:**

1. The bundled template is copied to `apps/assistant/web` and `apps/assistant/agent`.
2. `ceh-web-frontend:design-ui` is loaded, and Tidewater's `brand.css` is copied to
   `web/src/brand.css`.
3. The seven default components are kept, unless you said which ones the app does not need.

**Run it** (two terminals):

```bash
cd apps/assistant/agent && uv run uvicorn main:app --port 8000
cd apps/assistant/web && bun install && bun run dev      # http://localhost:5173
```

**Try it:** the empty canvas shows four starter buttons. Click **Show a table**, or type
`show a bar chart`. The mock agent has no LLM. It places whichever component you name, using the
example data defined for it.

---

## 2. Start from your own template

> Here's our design-system starter in `../acme-shell`. Turn it into an AG-UI canvas.

**Skill:** `build-ag-ui`, using your template instead of the bundled one.

**What happens:** Claude Code looks for four parts in your template: a component catalogue, the
agent connection, the canvas and the theme. It adds only the parts that are missing, in your
template's own style. Your layout and design system stay. If you already have a token file with
the same token names and classes as `design-ui`, it is kept in place of Tidewater.

---

## 3. Let the agent show something new

> The agent needs to show a timeline of order events — dates and what happened.

**Skill:** `add-canvas-component`.

**What happens:**

- It first checks whether an existing component already covers this. A "sales table" would just
  be `show_table`, not a new component.
- It then writes `web/src/catalogue/timeline.tsx` and adds one line to `catalogue/index.ts`. The
  new component has:
  - the name `show_timeline`
  - a description written for the agent ("use show_table for records without an order")
  - content-only fields: a title and a list of `{date, label}` events
  - example data
  - markup built only from theme classes

**Try it:**

- `show a timeline` places it with its example data.
- `show_timeline {"title":"x"}` is refused, and the chat names the missing field.
- `show_timeline {"title":"x","events":[{"date":"2026-01-01","label":"y"}],"style":{"color":"red"}}`
  renders normally. The `style` key is silently dropped.

**What it refuses to do:**

> Add a `color` prop to the stat card so the agent can highlight important numbers.

The canvas fails at startup: `"color" lets the agent style the component`. Claude Code suggests a
meaning-based option instead, `emphasis: "normal" | "important"`. The component maps that option
to a theme class, so the agent picks the meaning and the theme picks the look.

---

## 4. Change the look

> Switch the canvas to the Meridian theme.

**Skill:** `ceh-web-frontend:design-ui` (the theme layer). This works because every `ceh-ag-ui`
component uses only theme tokens.

**What happens:** `web/src/brand.css` is replaced with Meridian's. No component file changes. Both
themes use the same token names and class names.

---

## 5. Connect a real model

> Replace the mock with a real agent using Claude.

**Skill:** `build-ag-ui-agent`.

**What happens:** `server/main.py` and `server/pyproject.toml` are written next to `agent/`.
`agent/` stays, because it is still the fastest way to test a new component. The new server:

- sends the canvas's components to Claude as tools on every run
- streams Claude's text and tool calls back as AG-UI events
- stops as soon as Claude picks a component, so the canvas can draw it and send the result back
- keeps Claude's own conversation history for each thread and only ever appends to it

**Run it:**

```bash
export ANTHROPIC_API_KEY=...          # or `ant auth login`
cd apps/assistant/server && uv run uvicorn main:app --port 8000
```

**Try it:**

- "Show me Q3 revenue by region as a chart" should place `show_bar_chart` with real numbers.
- Follow up with "now as a table". The table should use the same numbers, which shows the
  conversation history carried over.
- Press **Stop** while a component is being drawn, then send another message. The next reply
  should still work.

**Next:** "the agent should be able to look up real orders" adds a server-side tool. The skill
covers this under _Adding a backend tool_.

---

## 6. Show progress while the agent works

> Report generation takes a while. Show a progress tracker the agent updates as it goes.

**Skill:** `add-live-state-panel`.

**What happens:**

- **Canvas:** a fixed `ProgressPanel` in `web/src/state/progress.tsx`, pinned above the placed
  components. It checks the agent's data against a schema before rendering, just like catalogue
  components.
- **Agent:** code that sends the whole state once (`STATE_SNAPSHOT`), then small updates
  (`STATE_DELTA`) as each step finishes. For a real model, this is an `update_progress`
  server-side tool, so the model never writes those updates itself.

**Try it with the mock:** type `show progress`. The panel appears and ticks through its steps, and
the chat says "Report ready."

**When it's the wrong skill:** if the value never changes after it's shown, it's a catalogue
component (example 3), not a live panel.

---

## 7. Make the agent ask before acting

> The agent can delete archived records. It must ask me before it does.

**Skill:** `add-human-approval`.

**What happens:**

- **Agent:** the delete action no longer runs straight away. The agent ends the run with an AG-UI
  interrupt ("Allow the agent to delete 3 archived records?"), and remembers which action that
  interrupt stands for.
- **Canvas:** a fixed approval card with **Approve** and **Reject** buttons appears in the chat
  panel. Its look comes from the theme. The agent supplies only the question text.
- **Next run:** it carries the user's decision. The action runs only on Approve, and each approval
  can be used only once.

**Try it with the mock:**

| You do                              | You see                                                                                     |
| ----------------------------------- | ------------------------------------------------------------------------------------------- |
| type `delete old records`           | the approval card; nothing is deleted                                                       |
| click **Approve**                   | "Done: delete 3 archived records."                                                          |
| ask again, click **Reject**         | "Not done: …"                                                                               |
| ask again, then type something else | the pending request is cancelled ("Not done: …"), then your new message gets a normal reply |

---

## 8. All together: a sales assistant, start to finish

A realistic order of prompts in one Claude Code session:

1. **"Build an AG-UI canvas for a sales assistant."** Uses `build-ag-ui`. Run it and click the
   starter buttons.
2. **"We never need key-values or callouts; drop them."** Uses `build-ag-ui` (step 3, shaping the
   catalogue).
3. **"The agent should show a sales pipeline: stages with deal counts and totals."** Uses
   `add-canvas-component`. It becomes `show_pipeline`, and you test it with `show a pipeline`.
4. **"Connect Claude, and give it a tool to query our deals table."** Uses `build-ag-ui-agent`,
   including a server-side tool.
5. **"Forecasts take a minute; show progress while it runs."** Uses `add-live-state-panel`.
6. **"Before the agent emails a customer, it must ask me."** Uses `add-human-approval`.

The end user never sees any of this. They type "what's our pipeline looking like?" and the canvas
shows a pipeline, a chart and a short summary, all in your theme. When they ask the assistant to
email a customer, it waits for their approval.
