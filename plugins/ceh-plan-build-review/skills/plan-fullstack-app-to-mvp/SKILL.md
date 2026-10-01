---
name: plan-fullstack-app-to-mvp
description: >-
  Load this skill when the COMPLETE build plan for an app is wanted in one session, empty repo to
  working MVP: a skeleton plus every iteration needed to reach a first usable version. Best for
  small-to-moderate, well-understood apps with a foreseeable whole build. Trigger on "plan this
  whole app to MVP", "plan everything upfront", "lay out all the iterations", "full build plan".
  All-at-once counterpart to plan-fullstack-app-iteratively: choose THIS skill for a new major
  version only when its ENTIRE version is planned to MVP in one session. A built-in complexity gate
  recommends the iterative fallback when upfront planning is unsafe. Not for planning just the next
  release or a version's next increment, or for a large, novel, or uncertain app (use
  plan-fullstack-app-iteratively), and not for building the plan (use implement-from-plan).
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Plan Fullstack App to MVP

Produce the **complete plan from nothing to a working MVP** in one session: a skeleton plus every
iteration needed to reach a first usable version, all detailed upfront and saved under
`.agents_workspace/planning/`.

The reason this skill exists: for small, well-understood apps, re-planning each iteration on its
own is wasted effort and context-switching. If the developer can already foresee the whole build,
planning it once is faster and gives a coherent arc.

The reason this skill is dangerous if misused: planning everything upfront is only safe when the
build is actually foreseeable. The moment real uncertainty enters (a novel core mechanic, a
decision that depends on seeing the data first, a sprawling surface area) detailed plans for later
iterations become fiction. A developer who builds against fictional plans wastes more time than
re-planning would have cost.

So this skill polices itself. **Step 1 is a gate, not a formality.** If the app is too big or too
uncertain, the right move is to stop and hand off to `plan-fullstack-app-iteratively`. Honest
verdict over a plan you cannot trust.

## Procedure

Everything below operates within the family being planned. Read
[Plan families and versions](#plan-families-and-versions) first when the request is a new major
version or continues plans already on disk.

### 1. Run the complexity gate

Before planning anything, decide whether this app is simple and certain enough to plan end-to-end.
Gather what you need by inferring from the user's description first, then ask only for what is
genuinely missing, one question at a time.

You are judging foreseeability: can the whole build be planned now without guessing at decisions
that can only be made by building first?

**Signs it IS suitable (plan to MVP):**

- The MVP is a bounded, well-understood set of features: you can name them all now.
- Conventional domain and patterns: CRUD, standard auth, one or two well-known integrations.
  Nothing research-grade or performance-critical-unknown.
- A manageable data model, on the order of a dozen entities or fewer.
- The stack is conventional and either decided or obvious from the problem.
- The developer can state what "done with the MVP" means in a sentence or two.
- Few hard external unknowns: no "it depends what the third-party API actually returns" or "we'll
  know after we see real usage."

**Signs it is NOT suitable (fall back to iterative):**

- The developer cannot pin down the MVP, or it keeps growing as you discuss it.
- A core mechanic is novel or unproven and needs a prototype to validate (ML feasibility, a hard
  algorithm, tight performance budgets, unproven integration).
- Very large surface area (many subsystems, many roles): a soft signal, not a stop on its own, but
  a reason to look harder for hidden uncertainty underneath it.
- Decisions that genuinely depend on building-and-seeing, where any plan you write for iteration 3
  is a guess you would likely throw away.
- The app already has substantial code and the user only wants the next feature (that is squarely
  the iterative skill's job).

**The threshold (adjust to taste).** Default to PROCEED: plan to MVP unless there is a real reason
not to. Size alone rarely earns a fallback: a larger app that is _conventional and well-understood_
is still foreseeable, so plan it. As a rough guide, ~8 core features and ~12 entities are both
comfortably plannable upfront, and even more is fine when the domain is familiar.

What actually earns a fallback is **uncertainty**, not size. Stop and recommend the iterative skill
if any one of these is strongly true:

- A core mechanic is novel or unproven and needs a prototype to validate.
- A real decision cannot be made without building-and-seeing first.
- The developer cannot pin down what the MVP is, or it keeps growing as you discuss it.

Treat very large surface area (many subsystems, many roles) as a soft signal: a reason to look
harder for hidden uncertainty, not an automatic stop on its own.

**Verdict. Be explicit, do not hedge:**

- **PROCEED** → state in one line why the app clears the gate, then continue to step 2.
- **STOP** → state plainly that this app is better planned incrementally, give the specific reason
  (which signal tripped), and recommend `plan-fullstack-app-iteratively` for a skeleton plus the
  first iteration. Do not produce a partial full-MVP plan as a consolation: that is the exact
  fiction this gate exists to prevent. If the user insists after a clear recommendation, proceed
  but flag the later iterations as low-confidence and likely to change.

### 2. Define the MVP boundary

The MVP is the terminator for the whole plan. Without a hard edge, "plan everything" has no
stopping point and silently becomes overplanning. So pin it down before sequencing anything.

Write two short lists and confirm them with the user if there is any doubt:

- **In the MVP:** the minimal set of capabilities that makes the app genuinely usable for its core
  purpose. If a feature can be removed and the app still delivers its core value, it is not in the
  MVP.
- **Deferred (post-MVP):** everything the user mentioned or will obviously want that is _not_
  required for first usefulness. This list is the plan's hard edge: nothing past it gets planned in
  this session.

Everything planned from here drives toward the "In the MVP" list and stops there.

Record both lists on the **terminator iteration** (the final iteration, which carries `mvp: true`)
so the boundary is durable, not just something you reasoned about and discarded: `mvp_target` in
its frontmatter, and a short `## Out of MVP scope` block in its body holding the deferred items.
Keeping the whole boundary on the terminator leaves the SKELETON frontmatter identical to the
incremental planner's, which is what lets a family planned partly with each skill stay consistent.
The deferred list is the plan's visible hard edge: a reader should be able to see what was
consciously left out, not just what is in.

### 3. Sequence the iterations

Decompose the path from skeleton to MVP into an ordered series of iterations. Do this in two passes
so you can sanity-check the arc before committing to detail.

**Pass A, the arc (one line each).** List the skeleton and each iteration with a one-line scope, in
build order. Stop when the cumulative state equals the MVP from step 2. Read this list back: does
each step move the app measurably closer? Is anything out of order? Is any step doing too much
(split it) or too little (merge it)?

**Pass B, confirm ordering.** Each iteration must be buildable using **only** what the skeleton and
earlier iterations established. This is the rule that makes upfront planning safe:

- Foundational concerns first: data model and auth (if the MVP needs it) before the features that
  depend on them.
- No forward references: ITER_N may rely only on content defined in SKELETON or
  ITER_01…ITER\_(N−1), never on something a later iteration introduces.
- Prefer thin vertical slices (one feature end-to-end) over horizontal layers, so each iteration
  leaves the app runnable and demonstrable, but do not force it. The first iteration is often a
  foundational layer (auth, core data model) that is not independently demoable, and that is
  expected: when the two pull against each other, foundational-first wins.

A good decomposition for a small app is usually 2–5 iterations after the skeleton. If you are
producing more than that, re-check the gate: you may be past the point where upfront planning is
wise.

### 4. Write all artifacts

Produce the full set for this family in one session. For the default family:

- `.agents_workspace/planning/SKELETON.md`
- `.agents_workspace/planning/ITER_01.md` … `ITER_NN.md` (the sequence from step 3)

For a new major version, tag every filename in the family with `_vN` and restart the counter at 01:

- `.agents_workspace/planning/SKELETON_v2.md` (omit if this version reuses the prior scaffold)
- `.agents_workspace/planning/ITER_01_v2.md` … `ITER_NN_v2.md`

The final iteration of the family is the **terminator**: it carries `mvp: true` plus `mvp_target`
and the `## Out of MVP scope` block. Every other iteration **omits** the `mvp` key entirely
(absence means false), which keeps non-terminal iterations schema-identical to the incremental
planner's. If the version has its own `SKELETON_vN`, that skeleton is self-contained and iterations
depend only on it and earlier `vN` iterations. If it is iterations-only, `ITER_01_vN` sets
`depends_on` to the prior family's terminal artifacts (skeleton plus its `mvp: true` iteration) so
it inherits across the boundary. See [Plan families and versions](#plan-families-and-versions).

Each artifact uses the same §01–§06 section structure. Read
`${CLAUDE_SKILL_DIR}/references/section-specs.md` for the expected contents of each section and the
required frontmatter, including the `depends_on` field that records each iteration's prerequisites
and the `mvp: true` marker on the final iteration.

Detail level:

- **Skeleton:** stubs and shapes: screens render, routes respond, functionality is stubbed. Enough
  to run the app and feel the concept. Because you have planned the whole arc, the skeleton's §02
  may state the _full_ target data model and API surface up front. That is expected and useful
  here, unlike in incremental planning where you would not know them yet. Just keep the
  implementations behind them stubbed.
- **Each iteration:** full scoped detail for what _that_ iteration adds or changes. For sections an
  iteration does not touch, use a pointer to the last artifact where the section was substantively
  written, referenced by stem (e.g. `> Unchanged — see ITER_01 § 04`, or across a version boundary
  `> Unchanged — see SKELETON § 03`) rather than restating it. You have the whole set in view, so
  make pointers precise, and ensure every artifact a pointer names is reachable through
  `depends_on`.

When a feature's UI would naturally appear before the iteration that builds its backend (e.g. a
"Send" button planned before the send endpoint exists), pick one explicit convention and state it
(omit the control until its iteration, or render it disabled with a clear note) rather than leaving
an either/or. Unresolved waffle is exactly what the audit's completeness scan flags.

Apply the [Implementation gotchas](#implementation-gotchas) before writing any §04 / §05 / §06
content, and address applicable traps proactively.

### 5. Audit and deliver

Run two audits before delivering.

**Per-artifact audit.** Run the [Pre-delivery audit checklist](#pre-delivery-audit-checklist) over
the skeleton and over each iteration.

**Cross-iteration audit** (unique to upfront planning: this is where the set holds together or
falls apart):

- **No forward references.** Every entity, route, type, or dependency an iteration uses is
  established in the skeleton or an earlier iteration, or, for a new version's first iteration, in
  the prior family it `depends_on`. Trace each `depends_on`: it must point only backward, never to
  a later iteration or version.
- **The data model only grows.** Later iterations extend earlier entities. They never silently
  redefine or contradict a field already specified, including across a version boundary, where a
  new version extends what the prior family established.
- **Terminates exactly at the MVP.** The cumulative state after this family's `mvp: true` iteration
  equals the "In the MVP" list from step 2: no less, and nothing planned past it. Exactly one
  iteration in the family carries `mvp: true`. Every other artifact omits the `mvp` key. The
  terminator also carries `mvp_target` and the `## Out of MVP scope` block, and no other artifact
  does.
- **Version tagging is consistent.** Every file in the family carries the same `_vN` tag (or none,
  for the default family), and the `NN` counter restarts within the family.
- **Pre-existing artifacts are untouched.** If this was a continuation, no skeleton or earlier
  iteration written in a prior session was rewritten. New iterations only chain off them via
  `depends_on`.
- **Decomposition is sound.** No empty or trivial iteration, no mega-iteration that should be
  split.

Then deliver:

1. Save all files to `.agents_workspace/planning/`.
2. Present them to the user.
3. Close with the summary under Output.

## Plan families and versions

A **plan family** is one complete skeleton-to-MVP sequence, identified by an optional version tag.
This skill plans one whole family per session.

- The first version of the app is the **default family**: untagged filenames `SKELETON.md`,
  `ITER_01.md`, …, with `mvp: true` on the final iteration.
- A **new major version** (v2, v3, …) is planned as a fresh family with a version tag. Each major
  version is a new start: the `NN` counter **restarts at 01** within the family, the version tag
  goes in the filename (`SKELETON_v2.md`, `ITER_01_v2.md`, …; canonical emit form is a `_vN`
  suffix, though the implementation step also reads a `v2_` prefix), and the family gets its
  **own** `mvp: true` terminator and `mvp_target`.

When the user asks to plan a new major version, the whole of this skill applies _to that version's
scope_: gate it, define its MVP boundary, sequence its iterations, write its family.

Families are **linked, not isolated**, but how a new version inherits depends on whether the family
has its own skeleton, and a skeleton is always a resolution _terminus_ (the implementation step
never traces past one):

- **Version with its own skeleton** (`SKELETON_vN`, when the scaffold is reshaped): the skeleton is
  **self-contained**. It re-states every section the version needs, since a pointer cannot resolve
  past it into the prior family. Iterations `depends_on` `SKELETON_vN` and earlier `vN` iterations
  only. Lineage to the prior version is conceptual.
- **Iterations-only version** (no skeleton, reusing the prior scaffold): `ITER_01_vN` `depends_on`
  the prior family's terminal artifacts, skeleton plus its `mvp: true` iteration, e.g.
  `depends_on: [SKELETON, ITER_03]`, and inheritance resolves _across_ that link. This is where
  cross-version `depends_on` does real work.

`depends_on` names artifacts by **stem** (filename without `.md`, including the version tag) and
only ever points **backward**: earlier in this family, or into an earlier version. Never forward.
Skeletons carry no `depends_on`.

### Continuing an existing family

The family may already be partly planned on disk, typically a skeleton and a few iterations
produced earlier with `plan-fullstack-app-iteratively`. This is a **continuation**, not a fresh
family, and the same-family rules apply (no version tag, no new skeleton):

- Read every existing `.agents_workspace/planning/` artifact first to establish current state. **Do
  not rewrite the skeleton or any existing iteration**: they are delivered artifacts.
- Run step 1's gate and step 2's boundary against the **remaining** path to MVP, not the whole app.
  What is already built is given. You are sequencing only what is left.
- Number new iterations from the next available `NN` in that family (existing `ITER_01`, `ITER_02`
  → start at `ITER_03`).
- The first new iteration's `depends_on` chains back through the existing artifacts it relies on
  (e.g. `[SKELETON, ITER_01, ITER_02]`). Later new iterations chain normally.
- The new terminator carries `mvp: true` + `mvp_target` + the `## Out of MVP scope` block, exactly
  as a from-scratch terminator would. Because the boundary lives on the terminator, the
  pre-existing skeleton needs no edit and stays valid as written.

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
- [ ] (Version family) Does every file carry the right `_vN` tag, does the `NN` counter restart
      within the family, and does exactly one iteration carry `mvp: true`?

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

- Plan one whole family per session, and nothing past its `mvp: true` terminator.
- Never rewrite a skeleton or iteration delivered in a prior session.
- Do not produce a `CLAUDE.md` or any file beyond the planning set unless the user asks.
- Ask at most one clarifying question at a time.

## Output

The full planning set for the family under `.agents_workspace/planning/`, each file opening with
the frontmatter from `${CLAUDE_SKILL_DIR}/references/section-specs.md`. Close the reply with a
brief summary:

- The MVP definition (the "In the MVP" list).
- The iteration sequence, one line each, in build order.
- What is deferred to post-MVP.

## Stop conditions

- The complexity gate returns STOP → state the reason, recommend `plan-fullstack-app-iteratively`,
  and produce no partial full-MVP plan. Proceed only if the user insists, flagging later iterations
  as low-confidence.
- The audit finds gaps that need user input → collect them and present them together before
  finalising.
