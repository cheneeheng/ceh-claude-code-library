---
name: build-agentic-workflow
description: >-
  Load this skill when turning a repetitive multi-step task into something an agent runs instead
  of something a human drives by hand: design it from a workflow spec, decide whether it is one
  skill or a gated multi-step workflow, and emit the artifact into the target repo's
  `.claude/skills/`. Trigger on "turn this into a skill", "turn this into a workflow", "build an
  agentic workflow", "automate this process", "make this repeatable", "I do this by hand every
  time", or "I need a skill that calls other skills". Covers the one-skill-vs-workflow gate, the
  `flow.yaml` config with its stages and gates, per-step data-contract schemas, and leaf-first
  emission. Building is interactive only; the result runs interactive or headless. An
  intake gate delegates to ceh-workflow-builder:interview-workflow-task when the task is not yet
  described. Not for evaluating a skill that already exists, not for adding a component to this
  plugin repo, and not for running a built workflow (use
  ceh-workflow-runner:run-agentic-workflow).
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Build an agentic workflow

Turn a specified repetitive task into a runnable artifact. Two possible outputs, and choosing
between them is the main decision this skill makes:

- **One skill** — the default. A single `SKILL.md` the agent loads and follows.
- **A workflow** — a `flow.yaml` config that owns _ordering and gates only_, a thin trigger skill
  that hands it to the generic runner (`ceh-workflow-runner:run-agentic-workflow`), and the step
  skills, scripts, saved workflows and handoff schemas the stages delegate to. The config format is
  `${CLAUDE_PLUGIN_ROOT}/references/flow-config-schema.md`; read it before Phase 3.

Target runtime is **Claude Code**. Other agent runtimes are out of scope; do not water the output
down for portability.

**Building is interactive only.** The intake never infers an answer and nothing is written until the
user agrees to the file list, so a headless build (`claude -p`) is out of scope: say so and stop. The
workflow this skill emits runs in both modes.

## Procedure

Assumed capabilities and Directories under Rules apply from step 1.

1. **Intake.** Confirm all nine spec answers exist, filling any gap through the interview skill
   (Phase 1).
2. **One skill or a workflow.** Default to one skill, and name it from the moment (Phase 2).
3. **What each step becomes.** Workflow only: pick an existing skill, a script, a step skill, a saved
   workflow, or inline prose per step (Phase 3).
4. **Data contracts.** Workflow only: give every cross-step handoff a file and a schema (Phase 4).
5. **Emit.** Write leaf-first, check resolution, dependency and schema coverage, and write only after
   the user agrees to the file list (Phase 5).

### Phase 1 — Intake

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

### Phase 2 — One skill or a workflow

**Default to one skill.** Emit a workflow only if at least one of these holds:

1. A step has a gate that can fail and must block the next step.
2. Steps need different tools or permissions.
3. Several steps are big enough to deserve their own context windows, or one step spans many items,
   cross-checks its own results, or loops until a check passes. A few large steps become `Agent`
   stages; many items, cross-checking or loop-until-pass make a step a candidate for a saved
   workflow stage (Phase 3). One large step alone does not qualify: a single skill can dispatch one
   subagent itself, and that is the smaller artifact.
4. The run must survive interruption and resume.
5. A step is already owned by an existing skill worth delegating to.
6. One step's output is another step's input — the handoff needs a declared contract.

"It has several paragraphs" is not a reason. If none hold, write one skill from the single-skill
template (see Templates under Output): skip phases 3 and 4, and from Phase 5 keep only the destination and the
confirm-before-writing step. A single skill has no schemas, no scripts to order, and no run
directory to ignore. Three rules from the skipped sections still apply, because they guard the
world rather than a handoff: never write a secret to disk, only a reference to where it lives; a step
from spec question 8 opens by checking the world; and the skill pauses for user confirmation
immediately before a step from question 9. It runs in the main context, so it can ask.

**Naming.** Derive `<name>` from the moment as a short kebab verb phrase the user would recognise
(`prepublish`, `onboard-tenant`, `rotate-keys`), never from the domain noun. Confirm it with the user
before emitting, because every filename depends on it.

### Phase 3 — What each step becomes

Decide per step, in this order — stop at the first that fits:

| Becomes                  | When                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| An existing skill        | Something already owns this step. Check it is installed in this session and model-invocable _before_ choosing this row; if it is not, drop to the next row rather than emitting a call that fails silently. A skill from a plugin rather than the target repo's `.claude/skills/` may be absent where the flow later runs, so its stage declares a `fallback` (`inline` or `agent`, with the `instructions` that replace it) |
| A saved workflow         | The step fans out over many items, cross-verifies, or loops until a check passes, and needs no human input mid-step. A saved workflow cannot ask the user, so a step that must ask is never this row. Always declare a `fallback`: the Workflow tool is off by default and must be switched on, so it is never assumed to exist. A step one agent can do is an `Agent` stage, not this row                                   |
| A script                 | The step is mechanical and deterministic                                                                                                                                                                                                                                                                                                                                                                                     |
| Its own step skill       | The step is independently triggerable outside the flow, or the flow will dispatch it in a subagent                                                                                                                                                                                                                                                                                                                           |
| Inline prose in the flow | Nothing above fits — the default                                                                                                                                                                                                                                                                                                                                                                                             |

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
a workflow, and no stage, saved workflow included, may call the runner.

**A step skill cannot be hidden.** `disable-model-invocation: true` would block the flow's own call
to it. Instead, its `description` must name the owning flow and route away from direct use.

### Phase 4 — Data contracts

The failure this prevents: a later step gets no declared shape, infers one from whatever artifact it
finds, infers it wrong, and the run keeps producing garbage past a green gate.

**When a schema is required.** Whenever a step's output is read by _any_ later step — N+m, not just
N+1 — and one artifact may have several consumers. A step that produces nothing, or a terminal
artifact nobody downstream reads, gets no schema.

- **Handoff is always a file.** Never conversation state: a step dispatched with `Agent` cannot see
  the caller's transcript, and compaction drops anything held only in context — including a
  `Skill`-invoked step's output, which does start out in the flow's own context. _Inside_ a saved
  workflow the handoffs between its own agents are script variables: map the schema onto
  `agent(..., { schema })` there. The stage boundary stays a file, with inputs passed in as `args`
  and the result written out as the stage's one `writes` file.
- **A fan-out writes one file per worker.** When a step runs N subagents over N items, each writes
  its own `<run>/<artifact>/<item>.md` and a following inline step merges them. Two concurrent
  workers appending to one artifact interleave and lose lines, and nothing downstream can tell that
  it happened. On a `fan_out` stage, declare `max_parallel`, `max_items` and the per-worker `output`
  file; the runner counts files against the item list before the gate, because a worker that died
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

### Phase 5 — Emit

Leaf-first, so every reference resolves the moment it is written:

1. Schema docs → `.claude/skills/<name>-flow/references/`
2. Scripts → `.claude/skills/<name>-flow/scripts/`
3. Saved workflows, if any → `.claude/workflows/<name>-<step>.js`
4. Step skills → `.claude/skills/<name>-<step>/SKILL.md`
5. The config → `.claude/skills/<name>-flow/flow.yaml`
6. The thin trigger skill → `.claude/skills/<name>-flow/SKILL.md`, and the invocation guide
   `.claude/skills/<name>-flow/README.md` (a skill directory's README is never loaded as context)

Paths inside `flow.yaml` are relative to its own directory, so a script is `scripts/<x>.sh` there. A
step skill reaches the same script through `${CLAUDE_SKILL_DIR}`, going up one level to
`<name>-flow/scripts/<x>.sh`. A bare `scripts/<x>.sh` in a skill body resolves against the repo
root, where `Bash` runs, and finds a different file or none.

**Each `.js` saved workflow.** Write it with LF line endings: CRLF fails at launch with "control
characters that would be hidden in the approval dialog". Then check the file:

- `export const meta` comes first, as a plain literal with `name` and `description`
- no `import()`, no `Date.now()`, no `Math.random()`, no no-argument `new Date()`
- every `phase()` title matches an entry in `meta.phases`
- at most 4,096 items in any one `parallel()` or `pipeline()`
- `null` results are filtered before use

Recommend the bundled `/workflow-authoring` skill (Claude Code v2.1.248+) for writing the body. When
any `.js` is emitted, add `.claude/workflows/*.js text eol=lf` to the target repo's `.gitattributes`.
These checks run here, in the target repo; this plugin repo's `validate.py` does not know them.

Then run these checks:

- **Resolution.** A generated step skill must have a directory that now exists under
  `.claude/skills/`. A pre-existing skill delegated to is a different check: it must be installed in
  the session and model-invocable, since a call to a skill with `disable-model-invocation: true`
  fails silently.
- **Config.** Check `flow.yaml` against every rule under Validation rules in
  `${CLAUDE_PLUGIN_ROOT}/references/flow-config-schema.md`. The three that matter most: every `reads`
  entry with a `from` names an artifact an _earlier_ stage `writes`, which is the likeliest
  generation bug once handoffs stop being adjacent; every such `reads` has a schema that exists; and
  every file the config names exists. A repo file with an established format names its `owner`
  instead of a schema.
- **Headless fit.** For every `approval` whose `headless` is `stop` or `preapproved-only`, the flow
  has `resumable: true`; set it for those, even when spec question 7 said one sitting, and tell the
  user why.

**The thin trigger skill.** Its body is only the moment and a hand-over to the runner. It declares
`compatibility` naming the `ceh-workflow-runner` plugin and, when a stage is a saved workflow,
Claude Code v2.1.269+ with the Workflow tool on. If the runner cannot be called, the skill stops
and says the plugin must be installed, and never runs the stages by hand.

**The invocation guide.** Emit the interactive and headless commands, derived from the config:

- `--allowedTools` is the union of every stage's `tools`, `Workflow(<workflow>)` for each saved
  workflow stage, and a `Bash` rule for each `script` stage, because headless nobody can approve
  a prompt.
- `--settings '{"enableWorkflows": true, "disableWorkflows": false}'` appears only when a `workflow`
  stage exists. The `enableWorkflows` key is undocumented and may change, so say so in the guide.
- Give PowerShell and Bash forms apart: PowerShell cuts a Bash-style `\"` at the first quote, so use
  a single-quoted prompt with plain `"` inside.
- Show the approval round trip when any `approval` exists: end at `FLOW STATUS: awaiting-approval
<stage-id>`, then resume with `--resume <session-id> 'APPROVED <stage-id>'`, or in a fresh session
  with `resume=latest approve=<stage-id>`.
- A saved workflow is launched by the runner through the Workflow tool, never as `/<workflow-name>`,
  which fails headless.

Show the user the file list and the stage/gate table (rendered from `flow.yaml`) before writing, and
write only after they agree. Emission creates several files in their repo; a wrong `<name>` means
cleaning all of them up.

Default destination is `.claude/skills/` in the target repo — no install step, picked up immediately.
Offer plugin packaging only when the user says the workflow is shared across repos.

## Rules

### Assumed capabilities

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

**The Workflow tool is not an assumed capability.** It is off by default and must be switched on
(Dynamic workflows in `/config`; headless, the undocumented `enableWorkflows` setting). When it is
absent, a tool-less session imitates a workflow by hand and the run looks successful on disk. A flow
with a `workflow` stage therefore declares a `fallback`, gets a `compatibility` naming Claude Code
v2.1.269+ and the setting, and relies on the runner failing or falling back, never imitating.

### Directories

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
`<run-id>` the start time (`20260913-0930`). Below, `<run>` means that directory. A flow that runs
every week into a fixed `<run-dir>/<name>/` finds last week's artifacts in place: a consumer's
exists-check passes on a stale file, and a finished `run-state.md` makes the new run skip every
step. State that must outlive a run, such as a last-processed watermark, sits one level up in
`<run-dir>/<name>/` and is written only after every step it summarises has succeeded.

For a workflow, the runner creates the run directory and reads `$CEH_WORKFLOW_RUN_DIR`, so
`flow.yaml` names neither the variable nor a path: it uses `{run}`. A single skill has no runner, so
it names the variable and its default in its own body, because the agent that runs it is not the
agent that built it and has none of this context. A flow with no `resumable`, no `writes` and no
`fan_out` has no run directory at all.

Run artifacts are never committed. When there is a run directory, check before finishing that the
target repo actually ignores it and append it to `.gitignore` if it does not; stating the requirement
in prose is not the same as meeting it. The runner checks again at the start of every run.

### What a gate does when it fails

"Do not proceed past a red gate" is a prohibition, not a behaviour, and a generated flow that stops
there leaves the agent inventing one at the worst possible moment. Every gate resolves into exactly
one of two shapes, and the gate says which (`gate.on_fail` in `flow.yaml`):

- **Stop.** The default. Report the failing step and why to the user and end the run, recording both
  in `run-state.md` if the flow emits one. Never continue in degraded mode, and never skip a step to
  reach a later one — the pipeline's ordering is the only reason the later step's inputs are valid.
- **Retry.** Only where re-running the step can plausibly change the outcome: a fix-then-re-run loop
  such as upgrade → test → fix → test. Then the flow must state **what changes between attempts**,
  **the bound** (a specific attempt count, usually 2 or 3), and **what happens when the bound is
  spent** — which is the Stop shape above. A retry loop with no bound is how a run burns a whole
  session on a failure that was never going to clear.

In `flow.yaml` a retrying gate carries `retry.max` and `retry.changes`, so the bound sits where the
gate is. In the stage/gate table shown to the user, write it as `<condition> — retry up to N, then
stop`. A stage with `approval` or `fan_out` never retries: the retry could fire an irreversible step
or a whole fan-out twice.

### Resumption, re-runs and irreversible steps

Emit a run-state file only when spec question 7 said the run can stop partway — otherwise skip this,
since a flow that finishes in one sitting does not need one. Emit it even when most steps leave a
trace in git: work the user never committed leaves none, so git alone cannot show where a run stopped.

`<run>/run-state.md`: one line per step recording `pending` / `done` / `awaiting-approval` /
`failed` plus the artifact path it wrote. For a workflow, set `resumable: true` in `flow.yaml` and
the runner keeps the file and handles resume (ask in interactive mode, `resume=latest|new` headless);
the flow writes none of that itself. A flow without `resumable` always starts a new run. A single
skill that can stop partway keeps its own `run-state.md` and opens by finding the newest run under
`<run-dir>/<name>/` and asking whether to resume it.

A step whose own work is long — a fact-check loop over twenty claims — must also be resumable
_inside_ itself. Say so explicitly in that step skill: append each unit of work to its output file as
it completes, rather than holding results in context and writing once at the end. Context that dies
mid-step takes unwritten results with it.

**Re-running is not the same as resuming.** `run-state.md` tells you where a run stopped only if it
survived the failure, so a step named in spec question 8 cannot rely on it. Such a step opens by
checking the world, not the ledger: does this schema already exist, has this row already been
inserted? In `flow.yaml` that is `unsafe_to_rerun: true` with a `world_check` that is true only
while the effect has not happened; the runner evaluates it before every attempt and stops when it is
false. In a single skill, make it the step's first instruction.

**Irreversible steps** from spec question 9 get two rules. They go as late in the pipeline as the data flow
allows, so a failure upstream costs nothing outside the machine. And the flow pauses for explicit user
confirmation immediately before each one — never on a re-run path where it could fire twice unnoticed.
A batch, such as one comment on each of thirty issues, gets one confirmation that shows the whole
batch, not thirty prompts. A declined confirmation is the Stop shape with the step left `pending`, so
a resumed run asks again instead of firing. Irreversible steps that follow each other with only a
mechanical gate between them — merge, then tag — share one confirmation placed before the first.

**The confirmation belongs to the flow, not to the step.** `AskUserQuestion` is stripped from every
subagent, so a step dispatched with `Agent` cannot ask and would proceed straight through the pause.
In a workflow, declare it as an `approval` on the stage; the runner asks immediately before the
dispatch, and never inside a step that might run isolated. Interactive it asks. Headless nobody can
answer, so every `approval` declares `headless`: `stop` (the default: end at `awaiting-approval`,
resume later with the approval), `preapproved-only` (proceed only if the launch passed
`approve=<stage-id>`) or `fail`. Never emit a "proceed anyway". Ask the user which they want for each
approval, since it decides whether an unattended run can ever reach that step.

### Frontmatter rules for everything emitted

`description` is always a folded block scalar (`>-`), with a uniform 2-space indent and no blank
lines — it is the only style with no escaping burden for colons, quotes, or backslashes. The
description carries the trigger moment _and_ negative routing to the nearest neighbour. Any other key
containing `: ` gets single quotes.

If `skill-creator` is installed in the session, use it for the mechanical `SKILL.md` authoring. It is
optional and this skill does not depend on it.

## Output

### Templates

Every emitted `SKILL.md` starts from a template in
`${CLAUDE_SKILL_DIR}/references/emitted-templates.md`: the single skill (the Phase 2 default), the
thin trigger skill that hands `flow.yaml` to the runner, and the step skill. Read it in Phase 5,
before writing the first `SKILL.md`.

### Final checklist

- [ ] All nine intake rows answered — by the spec or by the interview skill, never by silent
      assumption; a declined row carries its conservative reading written into the spec.
- [ ] Trigger is a moment, not a topic.
- [ ] Workflow emitted only because a Phase 2 condition holds — otherwise one skill.
- [ ] Every step's gate is falsifiable, stated against a schema where one exists.
- [ ] Every gate either stops the run or retries with a stated bound and a stop at the end of it.
- [ ] Every cross-step handoff is a file under the run directory, with a schema.
- [ ] Every `reads` has an earlier `writes`, and every cross-step `reads` has an existing schema.
- [ ] `flow.yaml` passes every rule in `flow-config-schema.md`, and the thin trigger skill only hands
      it to the runner, with the `ceh-workflow-runner` plugin named in its `compatibility`.
- [ ] `resumable: true` if and only if the run can stop partway or an approval stops headless; long
      steps resume internally.
- [ ] Every step that is unsafe to run twice has `unsafe_to_rerun` and a `world_check`, not
      `run-state.md`.
- [ ] No run artifact or config value holds a secret — only a reference to where one lives.
- [ ] Irreversible steps sit as late as the data flow allows, each behind an `approval` with a
      `headless` value, once per batch, and a "no" stops with the step still `pending`.
- [ ] Any fan-out gives each worker its own output file and declares `max_parallel` and
      `max_items`; a later step merges them.
- [ ] Each saved workflow has a `fallback`, LF line endings, the `.gitattributes` line, and passes
      the Phase 5 `.js` checks; no stage calls the runner.
- [ ] The invocation guide gives interactive and headless commands, with `--allowedTools` from the
      stages and `--settings` only when a `workflow` stage exists.
- [ ] Each run writes to its own `<run-id>` directory; only cross-run state sits beside them.
- [ ] Every script is referenced through `${CLAUDE_SKILL_DIR}` in a skill body, and relative to
      `flow.yaml` inside it, never a bare `scripts/` path in a skill body.
- [ ] Every delegated skill exists and is model-invocable, and a plugin skill's stage names a
      `fallback`.
- [ ] A committed repo file is read in place, and every second writer is declared in the schema.
- [ ] No step skill survives that is neither triggerable on its own nor dispatched in a subagent.
- [ ] `compatibility` present if and only if a step needs software the machine may lack, and each
      tool it names carries a minimum version and what fails without it. "Runnable through `uv run`"
      is neither.
- [ ] Run directory, if any, declared, defaulted, and actually present in the target repo's `.gitignore`.

## Stop conditions

- An intake row is unanswered and not declined → name every row that blocked the build and stop.
- A declined row other than 8 or 9 → stop and say which row blocked the build.
- The user has not agreed to the file list and the stage/gate table → write nothing.
- The build is requested headless (`claude -p`) → say building is interactive only and stop; the
  intake must not infer answers and nothing is written without the user's agreement.
- `flow.yaml` fails a rule in `flow-config-schema.md` → fix it before writing; if it cannot be
  fixed without changing an intake answer, stop and say which.

## Hands off to

- Invoke the Skill tool with skill="ceh-workflow-builder:interview-workflow-task" to fill any
  intake row the spec leaves open (Phase 1).
