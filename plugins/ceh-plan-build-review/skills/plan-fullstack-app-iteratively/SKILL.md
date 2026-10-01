---
name: plan-fullstack-app-iteratively
description: >-
  Load this skill when planning a software project one release at a time: each session produces a
  single artifact scoped to the next build (a SKELETON.md or the next ITER_NN.md), never the
  finished product. Handles vague or early-stage descriptions, greenfield skeletons, and iterative
  feature planning for existing apps. Trigger on "plan the next feature", "plan this iteration",
  "create a skeleton plan", "plan the next release", or a description of one piece of work to
  plan. The incremental counterpart to plan-fullstack-app-to-mvp: choose THIS skill to plan one
  release at a time. Not for planning the entire build from skeleton to a finished MVP in a single
  session (use plan-fullstack-app-to-mvp), building the plan (use implement-from-plan), or a small
  non-feature change to a built version (use patch-built-version).
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Plan Fullstack App Iteratively

Produce a **minimal, scoped plan** for the current development intent, no more, no less. The goal
is to unblock the next build, not to specify the finished product. Plans are iterative: each
planning session produces one artifact scoped to one release, saved under
`.agents_workspace/planning/`.

## Procedure

### 1. Assess intent

Before writing anything, determine:

1. **What is the app?** Capture the core concept in one sentence. If unclear, ask, but only one
   question at a time.
2. **Greenfield or continuing?** Is this a new project, or adding to or changing something that
   already exists?
3. **Which plan family?** Is this work part of the current plan set, or the start of a **new major
   version** (v2, v3, …)? See [Plan families and versions](#plan-families-and-versions). When in
   doubt, ask.
4. **What is the scope of this session?** Skeleton, a specific feature, a rework?

Use the answers to select the output mode:

| Situation                                                   | Output                                                                                             |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| New project, nothing built yet                              | [Skeleton plan](#skeleton-plan), default (untagged) family                                         |
| Existing project, same version, adding / changing something | [Iteration plan](#iteration-plan), current family                                                  |
| New major version that reshapes the scaffolding             | [Skeleton plan](#skeleton-plan), new `vN` family                                                   |
| New major version that builds directly on the prior one     | [Iteration plan](#iteration-plan), new `vN` family — first iteration `depends_on` the prior family |

Do not proceed to planning until intent is clear. Do not ask more than one clarifying question per
exchange.

### 2. Apply the anti-overplan check

Before writing any section, apply this filter:

> _Is this decision required to build what the developer described right now?_

If no, leave it out. Mark it as deferred in the relevant section with a one-line note.

Do not spec behaviour that has not been decided. Do not add features "while we're at it". Do not
describe the finished app: describe the next release.

Overplanning is a blocking risk: a developer who reads ahead into unresolved detail will pause to
resolve it before building. Keep the plan narrow.

### 3. Write the artifact

Write the [Skeleton plan](#skeleton-plan) or the [Iteration plan](#iteration-plan) selected in step

1. Read `${CLAUDE_SKILL_DIR}/references/section-specs.md` for the required frontmatter and the
   expected contents of each section (§01–§06) at skeleton and iteration level. Apply the
   [Implementation gotchas](#implementation-gotchas) when writing §04, §05, or §06.

### 4. Audit and deliver

1. Run the anti-overplan check over the draft: remove anything that is not required for the
   current release.
2. Run the [Pre-delivery audit checklist](#pre-delivery-audit-checklist) over the artifact.
3. Save the file to `.agents_workspace/planning/`.
4. Present the file to the user.
5. Close with the summary under Output.

## Plan families and versions

A **plan family** is one skeleton/iteration sequence for the app, identified by an optional version
tag.

- The first version of the app is the **default family**: untagged filenames `SKELETON.md`,
  `ITER_01.md`, `ITER_02.md`, …
- A **new major version** is a fresh family with a version tag (`v2`, `v3`, …). Each major version
  is a new start: the `NN` iteration counter **restarts at 01** within the family, and the version
  tag goes in the filename, `SKELETON_v2.md`, `ITER_01_v2.md`, … (canonical emit form: `_vN`
  suffix; the implementation step also accepts a `v2_` prefix on read).

Families are **linked, not isolated**, but how a new version inherits depends on whether it has its
own skeleton, and a skeleton is always a resolution _terminus_ (the implementation step never
traces past one):

- **New version with its own skeleton** (`SKELETON_vN`, when the scaffold is reshaped): the
  skeleton is **self-contained**. It re-states every section the version needs, because a pointer
  cannot resolve past it into the prior family. Its iterations `depends_on` `SKELETON_vN` and
  earlier `vN` iterations only. Lineage to the prior version is conceptual, not a resolution link.
- **New version without a skeleton** (iterations-only, when the prior scaffold is reused):
  `ITER_01_vN` `depends_on` the prior family's terminal artifacts, skeleton plus its final
  iteration, e.g. `depends_on: [SKELETON, ITER_03]`, and inheritance resolves _across_ that link.
  This is the case where cross-version `depends_on` does real work.

In both cases `depends_on` names artifacts by **stem** (filename without `.md`, which carries the
version tag), and only ever points **backward**: earlier in this family or into an earlier version,
never forward. Within a family it is simply the same-sequence chain, e.g.
`[SKELETON_v2, ITER_01_v2]`. Skeletons themselves carry **no** `depends_on`.

## Skeleton plan

**When:** new project, nothing built yet, **or** the start of a new major version that reshapes the
scaffolding.

**Goal:** produce just enough to build a working skeleton: screens render, routes respond, but
functionality is stubbed. The developer should be able to run the app and get a first impression of
whether the concept is right.

**File:** a single file `.agents_workspace/planning/SKELETON.md` for the default family, or
`.agents_workspace/planning/SKELETON_vN.md` for a version family (e.g. `SKELETON_v2.md`). Skeletons
carry no `depends_on` (see [Plan families and versions](#plan-families-and-versions)).

Include all applicable sections inline. Keep each section brief: stubs and shapes, not full
implementation detail. Skip sections that do not apply (e.g. no backend → skip §04, no LLM → skip
§06).

```text
§01 · Concept
§02 · Architecture
§03 · Tech Stack
§04 · Backend
§05 · Frontend
§06 · LLM / Prompts
```

Skeleton rules:

- Every route/endpoint exists but may return hardcoded or empty data.
- Every screen exists but may render with placeholder content.
- No auth, no error handling, no edge cases, unless the concept cannot be understood without them.
- Dependencies listed but not fully justified. Rationale comes in iteration plans.
- No deployment, no CI/CD, no production config.

## Iteration plan

**When:** adding to or changing an existing project, within an existing or new version family.

**File:** a single file `.agents_workspace/planning/ITER_NN.md` (default family) or
`.agents_workspace/planning/ITER_NN_vN.md` (version family), where `NN` is the next available
two-digit number **within that family**. The counter restarts per family: `ITER_01_v2.md` is the
first iteration of the `v2` family, independent of `ITER_01.md`.

Use the same section numbers as the skeleton. For each section:

- **If the section is affected by this iteration:** write the full scoped content for what changes.
- **If the section is untouched:** include a one-line pointer only.

**Pointer format.** Reference the artifact by stem (the filename without `.md`, including any
version tag):

```markdown
## §03 · Tech Stack

> Unchanged — see SKELETON_v2 § 03
```

or

```markdown
## §04 · Backend

> Unchanged — see ITER_02_v2 § 04
```

Always point to the last artifact where that section was substantively written, not to the skeleton
by default. A pointer may cross a version boundary, e.g. a `v2` iteration whose §03 was last
written in the `v1` skeleton points to `SKELETON § 03`.

**`depends_on` frontmatter.** Every iteration lists the artifacts it builds on, by stem, so the
implementation step can resolve pointers by walking the chain backward:

- Within a family, this is the same-sequence chain up to here, e.g.
  `depends_on: [SKELETON_v2, ITER_01_v2]`.
- The **first iteration of a new version** depends on `SKELETON_vN` if this version has its own
  skeleton. If it is an iterations-only version reusing the prior scaffold, it points back into the
  prior family's terminal artifacts instead, e.g. `depends_on: [SKELETON, ITER_03]`. See
  [Plan families and versions](#plan-families-and-versions).
- Every artifact named in a pointer must appear in (or be reachable through) `depends_on`.
  `depends_on` only points backward, never to a later iteration or version.

Iteration rules:

- Scope strictly to what this iteration adds or changes.
- Do not restate unchanged decisions: use pointers.
- `depends_on` must list every artifact a pointer relies on, and must point only backward.
- Do not plan the iteration after this one.
- Deferred decisions stay deferred until they become relevant.

## Pre-delivery audit checklist

Run this before delivering any plan artifact (SKELETON.md or ITER_NN.md). The goal is to catch
decisions that will block a developer mid-build.

For each gap: if it is your call, resolve it and add the resolution inline. If it needs user input,
collect all such items and present them together before finalising.

**Scope**

- [ ] Does the plan cover only the current release? Remove anything that belongs to a future
      iteration.
- [ ] Are deferred decisions explicitly marked as deferred (not left ambiguous)?
- [ ] Does every section pointer reference the correct artifact (by stem, including version tag)
      and section?
- [ ] (ITER) Does `depends_on` name every artifact the pointers rely on, and does it point only
      backward, never to a later iteration or version?
- [ ] (Version family) Does the filename carry the right version tag, and does the `NN` counter
      restart correctly within the family?

**Architecture (§02)**

- [ ] Is the component diagram in Mermaid, not ASCII art? (ITER) Does it visualize what changed
      this iteration, not just the current state?
- [ ] Is the data model complete enough to start building? (Entity names, key fields,
      relationships: not full schema, but no mystery fields)
- [ ] Is the API surface defined with methods, paths, and expected response shapes?
- [ ] Are cross-origin concerns addressed? (Which origins are allowed, cookie policy)
- [ ] Is auth handled or explicitly deferred? (Not silently assumed)

**Tech Stack (§03)**

- [ ] Is every dependency in the plan actually needed for this iteration?
- [ ] Are there conflicting dependencies? (e.g. two state management libraries)
- [ ] Is the local dev setup runnable from the plan alone? (Runtime versions, how to start)

**Backend (§04)**

- [ ] Does every planned endpoint have a defined request and response shape?
- [ ] Is ownership/access control addressed for every resource endpoint?
- [ ] Are list endpoints paginated, or is pagination explicitly deferred?
- [ ] Are environment variables named (not necessarily valued)?
- [ ] Is the database migration strategy clear for this iteration?

**Frontend (§05)**

- [ ] Does every screen in the plan have a defined route?
- [ ] Are loading and error states mentioned, or explicitly deferred?
- [ ] Is the API client setup addressed? (Base URL, auth header/cookie strategy)
- [ ] Are there empty states for any list views?

**LLM (§06, if applicable)**

- [ ] Is the model and provider specified?
- [ ] Is the context window strategy defined, or explicitly deferred?
- [ ] Are role constraints for the target API addressed in the message-building logic?

**Completeness scan (run last).** Scan the artifact for:

- Placeholder code (`pass`, `TODO`, `...`, `// implement this`)
- Prose like "adjust as needed" without specifying what
- References to files, endpoints, or types that are not defined anywhere in the plan
- Fields named in one section but missing from the corresponding schema in another

## Implementation gotchas

Common technical traps in fullstack projects. Apply them when writing §04 (Backend), §05
(Frontend), or §06 (LLM): address applicable gotchas proactively in the plan, do not wait for the
developer to discover them. Each entry names the trap, why it happens, and the fix. Examples use
Python/TypeScript but the principle applies across stacks.

**Backend**

- **Middleware order is counterintuitive.** Most frameworks apply middleware in reverse
  registration order (last registered = outermost), so CORS and auth middleware registered in the
  wrong order fail preflight or auth checks silently. Always document the intended middleware stack
  order in the plan with a comment explaining why.
- **ORM async + migration tool mismatch.** With an async ORM driver (asyncpg, aiomysql, motor),
  migration tools (Alembic, Flyway) default to synchronous connections and fail or silently skip
  tables. Bridge the async engine explicitly for migrations. Migration tools also only discover
  models that have been imported: a missing import in the model registry makes the table invisible
  to autogenerate.
- **Cached config breaks tests.** Singletons or cached config objects (e.g. `@lru_cache` on a
  settings loader) capture environment variables at first call. Tests that set env vars after
  import silently use the wrong config, including connecting to the wrong database. Mutate the
  cached instance in a test fixture before any test runs, or clear the cache between tests.
- **Sequential ID / index assignment under concurrency.** `SELECT MAX(n) + 1` without a row lock
  lets two concurrent transactions compute the same next value. Use a database sequence, an
  auto-increment column, or `SELECT FOR UPDATE` inside a transaction whenever assigning ordered
  identifiers.
- **Resource ownership: 403 not 404.** Returning 404 when a resource exists but belongs to another
  user leaks its existence. Always return 403 (or consistently 404 for both cases), never 404
  specifically for "exists but not yours".
- **Implicit resource creation race.** Creating a resource on the first dependent action (e.g.
  creating a session when the first message is sent) leaves a window where a second concurrent
  action arrives before the resource exists. Create resources as an explicit user action and
  trigger dependent operations after creation confirms.

**Frontend**

- **Stable references for framework config objects.** Frameworks that accept component registries
  or config objects (graph libraries, data grid libraries, rich text editors) compare them by
  reference. Defined inside a component, a new object is created on every render and the framework
  tears down and remounts all children. Define them at module level, outside any component.
- **httpOnly cookie cross-origin.** Cookies set by the API are not sent by the browser on
  cross-origin requests unless `withCredentials: true` (or equivalent) is set on the HTTP client.
  Missing this makes auth fail silently on every request.
- **SSE: native EventSource limitations.** The browser's `EventSource` API only supports GET
  requests and cannot send custom headers. Endpoints that require a POST body or auth header must
  use `fetch()` with `ReadableStream` parsing instead.
- **React StrictMode double-invocation.** In development, React 18 StrictMode intentionally mounts
  components twice, so any `useEffect` that triggers a one-time action (auto-send, session init,
  analytics event) fires twice. Guard with a `useRef(false)` flag that is set on first invocation.
- **Volume mounts shadow installed packages.** Mounting a source directory into a container
  overwrites the container's package directory with the host's (which has none). Add an anonymous
  volume for `node_modules` (and `.venv` for Python) to shield them from the host mount.

**Auth and sessions**

- **Token refresh race condition.** Multiple concurrent requests that each receive a 401 each
  attempt a token refresh independently. The second refresh call typically fails (token already
  rotated) and logs the user out. Queue concurrent 401s and resolve them all with the result of a
  single refresh call.
- **Refresh cookie parameter mismatch.** A refresh cookie set with different parameters in register
  vs login (different `path`, `samesite`, or `secure` values) results in two separate cookies, one
  of which is never sent. Set cookie parameters identically across all endpoints that issue it.

**LLM integration**

- **API role constraints.** Most LLM APIs only accept specific role values in the messages array
  (e.g. `user` and `assistant` only, no `system` role in the array). Messages stored with other
  roles in the database must be transformed before sending to the API. Plan this transformation in
  the build-messages function.
- **Context window overflow.** Long-running sessions eventually exceed the model's context limit.
  Plan a truncation or summarisation strategy upfront: sliding window, summarise-and-replace, or
  drop oldest. Deciding this after the fact requires retrofitting the message model.
- **SSE heartbeat composition.** Composing a keep-alive heartbeat with a streaming LLM response is
  error-prone if done via task cancellation/restart. Use a shared async queue: one producer task
  writes LLM tokens, a second writes periodic pings, a single consumer reads from the queue and
  yields to the client.

## Rules

- One artifact per session, scoped to one release. Do not produce multiple files unless the user
  asks.
- Do not produce a `CLAUDE.md` unless the user asks.
- Ask at most one clarifying question per exchange.
- Do not plan the iteration after this one.

## Output

One file under `.agents_workspace/planning/` (`SKELETON.md`, `ITER_NN.md`, or their `_vN` forms),
opening with the frontmatter from `${CLAUDE_SKILL_DIR}/references/section-specs.md`. Close the
reply with a brief summary:

- What this plan covers
- What is explicitly deferred
- Suggested scope for the next iteration (one sentence only, do not plan it)

## Stop conditions

- Intent is unclear (the app, greenfield vs continuing, the plan family, or the session scope) →
  ask one question and wait instead of planning on a guess.
- The audit finds gaps that need user input → collect them and present them together before
  finalising.
