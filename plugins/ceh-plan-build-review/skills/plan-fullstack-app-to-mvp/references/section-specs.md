# Section Specs

This skill produces the **whole set at once**: one `SKELETON.md` plus the full sequence
of `ITER_NN.md` files that reach the MVP. The section structure below is identical to
the incremental planner's, so artifacts stay compatible — the difference is that the
entire sequence is written in one session and must hold together as a set (see the
cross-iteration audit in SKILL.md step 5).

## File Naming and Version Variants

Base filenames are `SKELETON.md` and `ITER_NN.md` (`NN` = two digits). A new major
version of the app is planned as its own **plan family**, tagged `v2`, `v3`, …. Canonical
emit form is a `_vN` suffix — `SKELETON_v2.md`, `ITER_03_v2.md` — though the
implementation step also reads a `v2_` prefix.

Files sharing a tag form one family; the `NN` counter restarts per family, and each
family has its own `mvp: true` terminator. Untagged files are the **default family**.

## Output Frontmatter

Every output file must open with a YAML frontmatter block.

**SKELETON.md:**

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

The SKELETON frontmatter is **identical to the incremental planner's** — the MVP
boundary is recorded on the terminator iteration, not here (see below).

**ITER_NN.md:**

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

The **terminator** — the final iteration that reaches the MVP — carries two extra fields
that no other artifact has:

```yaml
---
artifact: ITER_04
status: ready
created: YYYY-MM-DD
scope: <one-line description of what this iteration adds or changes>
sections_changed: [02, 04]
sections_unchanged: [01, 03, 05]
depends_on: [SKELETON, ITER_01, ITER_02, ITER_03]
mvp: true # present and true ONLY here — marks the MVP terminator
mvp_target: <one-line description of the MVP this family reaches>
---
```

Every non-terminal iteration **omits** `mvp` entirely (absent means false). Only the
terminator sets `mvp: true`. This keeps non-terminal iterations schema-identical to the
incremental planner's, so a family planned partly with each skill stays consistent.

The SKELETON carries **no** `depends_on` — it is fresh scaffolding, and a versioned
skeleton is assumed to build on the prior family.

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
- `depends_on` — ITER only; the prior artifacts whose content this iteration relies on,
  named by stem. Within a family it is the same-sequence chain (e.g.
  `[SKELETON_v2, ITER_01_v2]`); the first iteration of an iterations-only new version
  points back into the prior family's terminal artifacts — skeleton plus its `mvp: true`
  iteration (e.g. `[SKELETON, ITER_03]`) — whereas a version with its own `SKELETON_vN`
  depends on that instead. Must point only backward — earlier in this family or an earlier
  version, never to a later one. This field is what the cross-iteration audit traces to
  catch forward references.
- `mvp` — terminator iteration only; present and `true` exactly once per family, on the
  iteration that reaches the MVP. Every other artifact **omits** the key, and absence
  means false. Marks where this family's plan stops; nothing is planned past it.
- `mvp_target` — terminator iteration only; one line stating the MVP this family reaches.
  Lives alongside `mvp: true` so the boundary travels with the artifact that closes it.

## Terminator iteration body — Out of MVP scope

The terminator iteration (the one carrying `mvp: true`) must include a short
`## Out of MVP scope` block listing the deferred items from Step 2 — the features and
concerns consciously excluded from this MVP. This is the plan's visible hard edge, and it
lives on the terminator so the full boundary (`mvp: true`, `mvp_target`, and the deferred
list) sits on one artifact and the skeleton stays identical to the incremental planner's.
Keep it to a bulleted list of short phrases; one line each is enough.

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
- New entities, new routes, modified relationships — extending, never contradicting,
  what earlier artifacts established
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
