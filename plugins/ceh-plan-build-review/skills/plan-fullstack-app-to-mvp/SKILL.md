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
`${CLAUDE_PLUGIN_ROOT}/references/section-specs.md` for the expected contents of each section, and
`${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md` for the file naming and the required frontmatter,
including the `depends_on` field that records each iteration's prerequisites, the `mvp: true` marker
on the final iteration, and its `## Out of MVP scope` block.

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

Read and apply `${CLAUDE_PLUGIN_ROOT}/references/implementation-gotchas.md` before writing any §04 / §05 / §06
content, and address applicable traps proactively.

### 5. Audit and deliver

Run two audits before delivering.

**Per-artifact audit.** Run the pre-delivery audit checklist in
`${CLAUDE_PLUGIN_ROOT}/references/audit-checklist.md` over the skeleton and over each iteration.

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

## Rules

- Plan one whole family per session, and nothing past its `mvp: true` terminator.
- Never rewrite a skeleton or iteration delivered in a prior session.
- Do not produce a `CLAUDE.md` or any file beyond the planning set unless the user asks.
- Ask at most one clarifying question at a time.

## Output

The full planning set for the family under `.agents_workspace/planning/`, each file opening with
the frontmatter from `${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md`. Close the reply with a
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
