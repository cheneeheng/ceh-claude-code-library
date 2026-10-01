# Section Specs

Expected contents for each section, at both skeleton and iteration level. File naming and
frontmatter live in `plan-schema.md`.

---

## §01 · Concept

**Skeleton:** One paragraph. What the app does, who it's for, what problem it solves. The single most important user flow. Nothing else.

**Iteration:** What this iteration adds or changes to the concept. If the concept is unchanged, use a pointer.

---

## §02 · Architecture

**Skeleton:**

- A component diagram in Mermaid (e.g. `flowchart` or `graph TD`) showing what exists and how the pieces connect — prefer Mermaid over ASCII art so it renders in any Markdown viewer
- Data model: entity names and their key fields only — no full schema
- API surface: list of routes with method, path, and one-line description. Return types can be stubs.
- No auth, no caching, no queues unless the concept breaks without them

**Iteration:**

- Only the parts of the architecture that change
- An updated Mermaid component diagram that visualizes what changed this iteration — mark new/modified pieces (e.g. a distinct Mermaid `style`/`class` or a `%% changed` comment) so the diff is visible at a glance
- New entities, new routes, modified relationships — extending, never contradicting, what earlier artifacts established
- Pointer for anything untouched

---

## §03 · Tech Stack

**Skeleton:**

- Language and runtime versions
- Framework choices (one per layer)
- Database (type + name)
- Key libraries (only those needed for the skeleton to run)
- No version pinning required at skeleton stage — add in an iteration when a version decision matters

**Iteration:**

- New dependencies added by this iteration, with rationale
- Version pins if a specific version was chosen and why
- Pointer for anything untouched

---

## §04 · Backend

**Skeleton:**

- File/module structure (directory tree, 2–3 levels)
- One representative stub implementation per route group — enough to show the pattern
- How to run locally (single command)
- Environment variables needed (names only, no values)

**Iteration:**

- New modules or files added
- Implementation detail for the endpoints/services introduced in this iteration
- Apply `${CLAUDE_PLUGIN_ROOT}/references/implementation-gotchas.md` before writing this section

---

## §05 · Frontend

**Skeleton:**

- Page/screen list with routes
- Component tree (top-level only)
- How to run locally (single command)
- Placeholder data strategy — how stubs are handled in the UI

**Iteration:**

- New screens or components introduced
- State changes, new API calls wired up
- Apply `${CLAUDE_PLUGIN_ROOT}/references/implementation-gotchas.md` before writing this section

---

## §06 · LLM / Prompts

_Skip if the app has no LLM integration._

**Skeleton:**

- What the LLM is used for (one sentence)
- Which model and provider
- Stub system prompt (can be a placeholder string)
- Input/output shape

**Iteration:**

- Revised or new prompts
- Context strategy changes
- Evaluation approach if this iteration makes the LLM behaviour testable
