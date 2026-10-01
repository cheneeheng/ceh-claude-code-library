---
name: build-agentic-workflow
description: >-
  Load this skill to turn a repetitive multi-step task into something an agent runs instead of
  something a human drives by hand: design it from a workflow spec, decide whether it is one
  skill or a gated multi-step workflow, and emit the artifact into the target repo's
  `.claude/skills/`. Trigger on "turn this into a skill", "turn this into a workflow", "build an
  agentic workflow", "automate this process", "make this repeatable", "I do this by hand every
  time", or "I need a skill that calls other skills". Covers the one-skill-vs-workflow gate, the
  pipeline + gate table, per-step data-contract schemas for handoffs, and leaf-first emission.
  An intake gate delegates to ceh-workflow-builder:interview-workflow-task when the task is not
  yet described, so this stays the entry point even with nothing written down. Not for
  evaluating a skill that already exists, not for adding a
  component to this plugin repo, and not for running a workflow that has already been built.
---

# Build an Agentic Workflow

Turn a specified repetitive task into a runnable artifact. Two possible outputs, and choosing
between them is the main decision this skill makes:

- **One skill** — the default. A single `SKILL.md` the agent loads and follows.
- **A workflow** — a flow skill that owns _ordering and gates only_, plus the step skills, scripts,
  and handoff schemas it delegates to.

Target runtime is **Claude Code**. Other agent runtimes are out of scope; do not water the output
down for portability.

## Assumed capabilities

The emitted artifact may rely on these and nothing else. Do not list them in the artifact — they are
always present in Claude Code, so declaring them is noise. `compatibility` is for the software the
_machine_ may lack, which is a different question.

| Capability                         | Tool                      | Watch out                                                                     |
| ---------------------------------- | ------------------------- | ----------------------------------------------------------------------------- |
| Read, write, edit files            | `Read` / `Write` / `Edit` | —                                                                             |
| Run commands                       | `Bash`                    | Any CLI a step invokes belongs in the artifact's `compatibility`              |
| Search                             | `Glob` / `Grep`           | —                                                                             |
| Call another skill                 | `Skill`                   | Loads into the **caller's** context — it does not get its own                 |
| Give a step its own context window | `Agent`                   | The only way to isolate a step; a subagent cannot see the caller's transcript |
| Ask the user                       | `AskUserQuestion`         | Stripped from every subagent, so only the flow itself can ask                 |

`Skill` and `Agent` are not interchangeable, and the difference decides two things later: whether a
step can be isolated (Phase 3) and whether it can pause for confirmation (Resumption, re-runs and irreversible steps).

## Directories

Two directories, two variables, two lifetimes. Do not conflate them.

|            | Variable                  | Default              | Holds                                                 |
| ---------- | ------------------------- | -------------------- | ----------------------------------------------------- |
| Build time | `$CEH_WORKFLOW_BUILD_DIR` | `.agents_workspace/` | the workflow spec and build notes                     |
| Run time   | `$CEH_WORKFLOW_RUN_DIR`   | `.agents_workspace/` | the generated workflow's step artifacts and run state |

Both default to the same place, so both namespace by name: the workflow spec is
`<build-dir>/<name>-workflow-spec.md` and run-time paths are under `<run-dir>/<name>/`. Use a
provisional slug for the spec until the name is settled, then rename it — otherwise building a second
workflow overwrites the first one's spec.

**One directory per run, not per flow.** Each run writes to `<run-dir>/<name>/<run-id>/`, with
`<run-id>` the start time (`20260913-0930`), and creating it is the flow's first instruction —
unless no step writes a run artifact, in which case the flow has no run directory at all. Below,
`<run>` means that directory. A flow that runs every week into a fixed `<run-dir>/<name>/` finds last
week's artifacts in place: a consumer's exists-check passes on a stale file, and a finished
`run-state.md` makes the new run skip every step. State that must outlive a run, such as a
last-processed watermark, sits one level up in `<run-dir>/<name>/` and is written only after every
step it summarises has succeeded.

The generated flow **names the run-time variable and its default in its own body** — the agent that
runs it is not the agent that built it and has none of this context.

Run artifacts are never committed. When the flow has a run directory, before finishing check the target repo actually ignores the run
directory and append it to `.gitignore` if it does not; stating the requirement in prose is not the
same as meeting it.

## Phase 1 — Intake

This skill designs from a spec; it does not conduct the interview. Before anything else, establish
that the nine answers exist — in `<build-dir>/<name>-workflow-spec.md`, or given directly in this
conversation, in which case write them to that file now so the rest of the phases have one source.

| #   | Must be answered                                        | Not satisfied by                                                                              |
| --- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| 1   | Moment                                                  | a topic or domain noun. A schedule ("every Friday") passes — recast it as the moment it fires |
| 2   | Manual procedure, step by step                          | "the usual release process"                                                                   |
| 3   | Preconditions and proof per step                        | a proof no command or file check can settle, unless it is a declared human go/no-go gate      |
| 4   | Data flow per step, naming the _producing_ step         | an artifact named with no producer                                                            |
| 5   | Tooling: CLIs, credentials, services, network           | —                                                                                             |
| 6   | Done: what is true at the end that was not at the start | —                                                                                             |
| 7   | Interruption: one sitting, or resumable                 | —                                                                                             |
| 8   | Which steps damage something if they run twice          | silence                                                                                       |
| 9   | Which steps are irreversible outside this machine       | silence                                                                                       |

**A gap is not a "none".** Invoke the Skill tool with
`skill="ceh-workflow-builder:interview-workflow-task"` to fill any row above, then re-check this
table against what it wrote. Never infer a missing answer and continue.

**Check this row by row, all nine.** It bites hardest on the rows you can nearly answer. An
assumed-empty 8 emits a workflow with no re-run guard and an assumed-empty 9 emits one that
publishes without pausing, so those two fail loudly, and they are the rows a user volunteering
their task unprompted almost never covers. Rows 1-7 fail quietly, because the procedure under 2
makes them look already answered: deriving row 4's data flow from what each step appears to read
and leave behind is the same violation, and it is the one that gets through, because the chain you
derived reads plausibly. Plausible is not answered. Only the user knows whether step 3 pulls its
input from somewhere no step names.

An obvious answer is still your answer, not theirs. A gap never takes the declined-row fallback
below: writing the conservative reading under an unanswered heading and calling it an assumption is
the same failure wearing a label, because the user never chose it. Marking a row `Partial` and then
supplying the missing half yourself is that same move at half scale. Naming a row as unanswered and
then answering it in the next sentence does not clear the gate either. When a row cannot be filled,
the build is blocked — name every row that blocked it and stop. Reporting a finished artifact while
a row is open is the failure this gate exists to prevent.

**A declined row is different, and it ends the loop.** When the spec records `Declined` under a
heading, do not invoke the interview again — that is how these two skills bounce off each other
forever. Take the conservative reading instead, write it into the spec as an assumption, and tell
the user what it costs them:

| Declined      | Assume                                            | Costs                                        |
| ------------- | ------------------------------------------------- | -------------------------------------------- |
| 8             | every step is unsafe to run twice                 | each step opens by checking the world        |
| 9             | every step with an outside effect is irreversible | the flow pauses for confirmation before each |
| any other row | nothing — these cannot be assumed safely          | stop and say which row blocked the build     |

Whatever you write into the spec goes under the heading it belongs to. Do not add a heading: the
consumer gates on the nine by name, and a tenth section holding your own build notes is not part of
that contract. Build notes belong in the reply.

Do not start designing until every row passes or carries a recorded assumption.

## Phase 2 — One skill or a workflow

**Default to one skill.** Emit a workflow only if at least one of these holds:

1. A step has a gate that can fail and must block the next step.
2. Steps need different tools or permissions.
3. Several steps are big enough to deserve their own context windows. One such step does not qualify:
   a single skill can dispatch one subagent itself, and that is the smaller artifact.
4. The run must survive interruption and resume.
5. A step is already owned by an existing skill worth delegating to.
6. One step's output is another step's input — the handoff needs a declared contract.

"It has several paragraphs" is not a reason. If none hold, write one skill from the single-skill
template below: skip phases 3 and 4, and from Phase 5 keep only the destination and the
confirm-before-writing step. A single skill has no schemas, no scripts to order, and no run
directory to ignore. Three rules from the skipped sections still apply, because they guard the
world rather than a handoff: never write a secret to disk, only a reference to where it lives; a step
from spec question 8 opens by checking the world; and the skill pauses for user confirmation
immediately before a step from question 9. It runs in the main context, so it can ask.

**Naming.** Derive `<name>` from the moment as a short kebab verb phrase the user would recognise
(`prepublish`, `onboard-tenant`, `rotate-keys`), never from the domain noun. Confirm it with the user
before emitting, because every filename depends on it.

## Phase 3 — What each step becomes

Decide per step, in this order — stop at the first that fits:

| Becomes                  | When                                                                                                                                                                                                                                                                                                                                                                                            |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| An existing skill        | Something already owns this step. Check it is installed in this session and model-invocable _before_ choosing this row; if it is not, drop to the next row rather than emitting a call that fails silently. A skill from a plugin rather than the target repo's `.claude/skills/` may be absent where the flow later runs, so its row names a fallback: `<skill> if installed, else <next row>` |
| A script                 | The step is mechanical and deterministic                                                                                                                                                                                                                                                                                                                                                        |
| Its own step skill       | The step is independently triggerable outside the flow, or the flow will dispatch it in a subagent                                                                                                                                                                                                                                                                                              |
| Inline prose in the flow | Nothing above fits — the default                                                                                                                                                                                                                                                                                                                                                                |

**Isolation comes from `Agent`, not from being a skill.** A step skill invoked with the `Skill` tool
runs in the flow's own context and saves it nothing. A step that needs its own context window — it
reads a lot, or its working notes would crowd the rest of the run — is dispatched with `Agent`,
either carrying its instructions inline or told to load the step skill. Choose that only when the
step's output outlives the subagent — a file, or state the flow can check with a command, such as a
commit, an open PR, or a tag — because the subagent's context dies with it. The dispatch prompt
carries `<run>`, every input path, and the path of every schema the step reads or writes, since the
subagent sees nothing else.

**A step earns its own skill only on the third row.** A step that only ever runs inside one flow,
and fits in the flow's own context, is inline prose or a script. Three skills beat six: every skill
added to `.claude/skills/` competes for auto-triggering in the target repo, and `.claude/skills/` is
flat, so a generated set is grouped only by naming — flow `<name>-flow`, steps `<name>-<step>`.

**Nesting is capped at one level.** A workflow's steps may be skills; a step skill may not itself be
a workflow.

**A step skill cannot be hidden.** `disable-model-invocation: true` would block the flow's own call
to it. Instead, its `description` must name the owning flow and route away from direct use.

## Phase 4 — Data contracts

The failure this prevents: a later step gets no declared shape, infers one from whatever artifact it
finds, infers it wrong, and the run keeps producing garbage past a green gate.

**When a schema is required.** Whenever a step's output is read by _any_ later step — N+m, not just
N+1 — and one artifact may have several consumers. A step that produces nothing, or a terminal
artifact nobody downstream reads, gets no schema.

- **Handoff is always a file.** Never conversation state: a step dispatched with `Agent` cannot see
  the caller's transcript, and compaction drops anything held only in context — including a
  `Skill`-invoked step's output, which does start out in the flow's own context.
- **A fan-out writes one file per worker.** When a step runs N subagents over N items, each writes
  its own `<run>/<artifact>/<item>.md` and a following inline step merges them. Two concurrent
  workers appending to one artifact interleave and lose lines, and nothing downstream can tell that
  it happened. The merge step's gate counts files against the item list, because a worker that died
  leaves no file rather than a failing one, and a resumed run dispatches only the items with no file.
- **A repo file is its own handoff.** When a step writes a committed project file in a format that
  already has an owner — `CHANGELOG.md` per the changelog skill, a manifest — the consumer reads it in
  place and the Schema column names that owner. Copying it into the run directory, or restating its
  format in a schema, makes a second version that can drift.
- **Artifacts live for the whole run.** Nothing is cleaned up at a step boundary; the consumer may be
  four steps away.
- **One writer, many readers.** The schema belongs to the producing step. Every consumer points at
  the one schema file rather than restating its fields, or the contract drifts between them. When a
  later step must amend the artifact — adding ticket links to a drafted document — the schema names
  that step and the part it owns. An undeclared second writer is the bug this rule exists to catch.
- **Preconditions are checked twice.** The producer's gate proves the artifact was valid when
  written; each consumer re-asserts it exists before reading, since intervening steps can fail.
- **Never a secret.** A run artifact is plaintext on disk, git-ignored or not. A step that produces a
  credential writes a _reference_ to where it lives — a secret-manager key, an env var name — and the
  schema says so. The consuming step resolves the reference itself.

**Where it lives.** `.claude/skills/<name>-flow/references/<artifact>-schema.md`. Form is a Markdown
doc: required fields, optional fields, one complete worked example, and the list of consuming steps.
Name each required field as a literal heading or key, so a gate can check it with `Grep` rather than
by judgement.
Reach for JSON Schema and a validator only when the artifact is genuinely JSON and that step already
runs a script — never add a dependency for this.

**Schemas make gates falsifiable.** Replace "the plan is complete" with "`<run>/plan.md`
exists and carries every required field in `plan-schema.md`". Phrase gates that way wherever a schema
exists.

## What a gate does when it fails

"Do not proceed past a red gate" is a prohibition, not a behaviour, and a generated flow that stops
there leaves the agent inventing one at the worst possible moment. Every gate resolves into exactly
one of two shapes, and the flow says which:

- **Stop.** The default. Report the failing step and why to the user and end the run, recording both
  in `run-state.md` if the flow emits one. Never continue in degraded mode, and never skip a step to
  reach a later one — the pipeline's ordering is the only reason the later step's inputs are valid.
- **Retry.** Only where re-running the step can plausibly change the outcome: a fix-then-re-run loop
  such as upgrade → test → fix → test. Then the flow must state **what changes between attempts**,
  **the bound** (a specific attempt count, usually 2 or 3), and **what happens when the bound is
  spent** — which is the Stop shape above. A retry loop with no bound is how a run burns a whole
  session on a failure that was never going to clear.

Mark a retrying gate in the pipeline table as `<condition> — retry up to N, then stop`, so the bound
is visible where the gate is rather than buried in prose.

## Resumption, re-runs and irreversible steps

Emit a run-state file only when spec question 7 said the run can stop partway — otherwise skip this,
since a flow that finishes in one sitting does not need one. Emit it even when most steps leave a
trace in git: work the user never committed leaves none, so git alone cannot show where a run stopped.

`<run>/run-state.md`: one line per step recording `pending` / `done` plus the artifact path it
wrote. The flow's first instruction becomes "find the newest run under `<run-dir>/<name>/`; if its
`run-state.md` has a step that is not `done`, ask whether to resume that run or start a new one, and
on resume skip to that step". A flow without a run-state file always starts a new run.

A step whose own work is long — a fact-check loop over twenty claims — must also be resumable
_inside_ itself. Say so explicitly in that step skill: append each unit of work to its output file as
it completes, rather than holding results in context and writing once at the end. Context that dies
mid-step takes unwritten results with it.

**Re-running is not the same as resuming.** `run-state.md` tells you where a run stopped only if it
survived the failure, so a step named in spec question 8 cannot rely on it. Such a step opens by
checking the world, not the ledger: does this schema already exist, has this row already been
inserted? Write that check into the step itself and make it the step's first instruction.

**Irreversible steps** from spec question 9 get two rules. They go as late in the pipeline as the data flow
allows, so a failure upstream costs nothing outside the machine. And the flow pauses for explicit user
confirmation immediately before each one — never on a re-run path where it could fire twice unnoticed.
A batch, such as one comment on each of thirty issues, gets one confirmation that shows the whole
batch, not thirty prompts. A declined confirmation is the Stop shape with the step left `pending`, so
a resumed run asks again instead of firing. Irreversible steps that follow each other with only a
mechanical gate between them — merge, then tag — share one confirmation placed before the first.

**The confirmation belongs to the flow, not to the step.** `AskUserQuestion` is stripped from every
subagent, so a step dispatched with `Agent` cannot ask and would proceed straight through the pause.
Put the prompt in the flow, immediately before the dispatch, and never inside a step that might run
isolated.

## Phase 5 — Emit

Leaf-first, so every reference resolves the moment it is written:

1. Schema docs → `references/`
2. Scripts → `.claude/skills/<name>-flow/scripts/`
3. Step skills → `.claude/skills/<name>-<step>/SKILL.md`
4. The flow skill → `.claude/skills/<name>-flow/SKILL.md`

Reference a script through `${CLAUDE_SKILL_DIR}`, which Claude Code substitutes with the calling
skill's own directory: the flow reaches `scripts/<x>.sh` beneath it, a step skill goes up one level to
`<name>-flow/scripts/<x>.sh`. A bare `scripts/<x>.sh` resolves against the repo root, where `Bash`
runs, and finds a different file or none.

Then run these checks:

- **Resolution.** A generated step skill must have a directory that now exists under
  `.claude/skills/`. A pre-existing skill delegated to is a different check: it must be installed in
  the session and model-invocable, since a call to a skill with `disable-model-invocation: true`
  fails silently.
- **Dependency.** Every `Reads` entry names an artifact some _earlier_ step `Writes`. This is the
  likeliest generation bug once handoffs stop being adjacent.
- **Schema coverage.** Every `Reads` entry that names another step has a schema, and that schema file
  exists. A `—` in the Schema column is only legal when the artifact came from outside the flow, and
  a repo file with an established format names its owner instead.

Show the user the file list and the step/gate table before writing, and write only after they agree.
Emission creates several files in their repo; a wrong `<name>` means cleaning all of them up.

Default destination is `.claude/skills/` in the target repo — no install step, picked up immediately.
Offer plugin packaging only when the user says the workflow is shared across repos.

## The single-skill template

The Phase 2 default, and the path most tasks end on.

```markdown
---
name: <name>
description: >-
  <The moment, as a verb.> Trigger on "<phrase>", "<phrase>". Not for <nearest neighbour>, use
  <that> instead.
compatibility: >-
  <Only if it needs a CLI, service, credential, or network.>
---

# <Name>

<One paragraph: what this does and the one thing it gets right that doing it ad hoc does not.>

## Procedure

1. <step>
2. <step> — <how to tell it worked, only where that is not self-evident>
3. <irreversible step> — <confirm with the user first, showing exactly what will be sent or changed>

## Done when

<The falsifiable end condition from spec question 6.>
```

No pipeline table, no run directory, no schemas: a single skill runs in one context and hands nothing
off. Adding those is the over-engineering Phase 2 exists to prevent.

## The flow skill template

```markdown
---
name: <name>-flow
description: >-
  <The moment, as a verb.> Trigger on "<phrase>", "<phrase>". This skill owns only the ordering and
  the gates; each step is delegated to the skill or script that owns it. Not for <nearest
  neighbour>, use <that> instead.
compatibility: >-
  <Only if a step needs a CLI, service, credential, or network. Name the tool, its minimum version,
  and what fails without it.>
argument-hint: "<Only if a run starts from an argument, e.g. [repo]>"
---

# <Name> Flow

<One paragraph: the pipeline as an arrow chain, and what this adds over running the steps ad hoc.>

Each run writes its state and step artifacts to `$CEH_WORKFLOW_RUN_DIR/<name>/<run-id>/`, defaulting
to `.agents_workspace/<name>/<run-id>/`, with `<run-id>` the start time. Create it first and pass its
path to every step. The directory is git-ignored. <Omit this paragraph when no step writes a run
artifact.>

## Pipeline

Run top to bottom. A red gate stops the run unless its row states a retry bound: report which gate
failed and why, never continue in degraded mode or skip ahead.

| #   | Step           | Delegate to                                                                                                                                                                                                          | Gate before next step                                                |
| --- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 1   | <what happens> | the Skill tool with `skill="<step-skill>"` (plus `if installed, else <fallback>` for a plugin skill), or the Agent tool with `subagent_type="<agent>"`, or `scripts/<x>.sh` via `${CLAUDE_SKILL_DIR}`, or "— inline" | <falsifiable condition>, or `<condition> — retry up to N, then stop` |

## Data contracts

| Step | Reads (from step)  | Writes      | Schema                            |
| ---- | ------------------ | ----------- | --------------------------------- |
| 2    | `plan.md` (step 1) | `report.md` | `references/<artifact>-schema.md` |

<Omit this section entirely when no step reads another step's output.>
```

In the emitted flow, spell the delegation out as a literal instruction to invoke the Skill tool with
that skill name, and give the schema its real filename. The template above keeps the call in
backticks and the schema path as an angle-bracket placeholder on purpose: _this_ repo's
`validate.py` resolves every literal skill invocation and every literal `references/…` path it
finds, so a concrete example here would fail the repo's own gate. Do not "fix" either one.

## The step skill template

```markdown
---
name: <name>-<step>
description: >-
  <The moment.> Called by `<name>-flow` as step N; not for direct use outside that flow.
compatibility: >-
  <Only if this step needs a CLI, service, credential, or network. A step is the usual place such a
  need appears, so check before omitting.>
---

# <Name>: <Step>

Reads `<artifact>` at `<run>/<file>` per `<schema>`, where `<run>` is the run directory the flow
passes in; writes `<artifact>` to `<run>/<file>`. <Omit whichever half does not apply.>

<The step's actual instructions.>

## Done when

<The falsifiable condition the flow's gate checks.>
```

## Frontmatter rules for everything emitted

`description` is always a folded block scalar (`>-`), with a uniform 2-space indent and no blank
lines — it is the only style with no escaping burden for colons, quotes, or backslashes. The
description carries the trigger moment _and_ negative routing to the nearest neighbour. Any other key
containing `: ` gets single quotes.

If `skill-creator` is installed in the session, use it for the mechanical `SKILL.md` authoring. It is
optional and this skill does not depend on it.

## Final checklist

- [ ] All nine intake rows answered — by the spec or by the interview skill, never by silent
      assumption; a declined row carries its conservative reading written into the spec.
- [ ] Trigger is a moment, not a topic.
- [ ] Workflow emitted only because a Phase 2 condition holds — otherwise one skill.
- [ ] Every step's gate is falsifiable, stated against a schema where one exists.
- [ ] Every gate either stops the run or retries with a stated bound and a stop at the end of it.
- [ ] Every cross-step handoff is a file under the run directory, with a schema.
- [ ] Every `Reads` has an earlier `Writes`, and every cross-step `Reads` has an existing schema.
- [ ] Run-state file emitted if and only if the run can stop partway; long steps resume internally.
- [ ] Every step that is unsafe to run twice opens by checking the world, not `run-state.md`.
- [ ] No run artifact holds a secret — only a reference to where one lives.
- [ ] Irreversible steps sit as late as the data flow allows, and the flow — not the step — asks,
      once per batch, and a "no" stops with the step still `pending`.
- [ ] Any fan-out gives each worker its own output file, merged by a later step that counts them.
- [ ] Each run writes to its own `<run-id>` directory; only cross-run state sits beside them.
- [ ] Every script is referenced through `${CLAUDE_SKILL_DIR}`, never a bare `scripts/` path.
- [ ] Every delegated skill exists and is model-invocable, and a plugin skill's row names a fallback.
- [ ] A committed repo file is read in place, and every second writer is declared in the schema.
- [ ] No step skill survives that is neither triggerable on its own nor dispatched in a subagent.
- [ ] `compatibility` present if and only if a step needs software the machine may lack, and each
      tool it names carries a minimum version and what fails without it. "Runnable through `uv run`"
      is neither.
- [ ] Run directory, if any, declared, defaulted, and actually present in the target repo's `.gitignore`.
