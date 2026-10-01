# Section Specs

## File Naming and Version Variants

Base filenames are `SKELETON.md` and `ITER_NN.md` (`NN` = two digits). When the app has more than one major version planned in the same location, files carry a **version tag** (`v2`, `v3`, …). Canonical emit form is a `_vN` suffix — `SKELETON_v2.md`, `ITER_03_v2.md` — though the implementation step also reads a `v2_` prefix.

Files sharing a tag form one **plan family**; the `NN` counter restarts per family. Untagged files belong to the **default family**.

## Output Frontmatter

Every output file (SKELETON or ITER_NN) must open with a YAML frontmatter block.

**SKELETON:**

```yaml
---
artifact: SKELETON
status: ready
created: YYYY-MM-DD
app: <one-line app name>
stack: <comma-separated key technologies>
sections: [01, 02, 03, 04, 05] # list only sections present in this file
---
```

Skeletons carry **no** `depends_on` — a skeleton is fresh scaffolding, and a versioned skeleton is assumed to build on the prior family.

**ITER_NN:**

```yaml
---
artifact: ITER_01 # increment NN per family; stem includes any version tag
status: ready
created: YYYY-MM-DD
scope: <one-line description of what this iteration adds or changes>
sections_changed: [02, 05] # sections with substantive content in this file
sections_unchanged: [01, 03, 04] # sections with pointers only
depends_on: [SKELETON] # prior artifacts this iteration builds on, by stem
---
```

**Fields:**

- `artifact` — filename without extension (the stem; carries the version tag for versioned files)
- `status` — always `ready` on delivery
- `created` — ISO date
- `app` — SKELETON only; short human-readable name
- `stack` — SKELETON only; key technologies (e.g. `Python, FastAPI, React, PostgreSQL`)
- `sections` — SKELETON only; the section numbers present in this file
- `scope` — ITER only; what this iteration covers
- `sections_changed` — ITER only; sections with content in this file
- `sections_unchanged` — ITER only; sections that use pointers
- `depends_on` — ITER only; prior artifacts this iteration relies on, named by stem. Within a family it is the same-sequence chain (e.g. `[SKELETON_v2, ITER_01_v2]`); the first iteration of an iterations-only new version points back into the prior family (e.g. `[SKELETON, ITER_03]`), whereas a version with its own `SKELETON_vN` depends on that instead. Points only backward — never to a later iteration or version.

---

Expected contents for each section, at both skeleton and iteration level.

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
