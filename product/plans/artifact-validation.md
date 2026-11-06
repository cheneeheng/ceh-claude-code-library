---
schema: plan/v1
title: Handoff files as YAML validated by pydantic, with Markdown generated from it
status: building
created: 2026-11-06
---

## Goal

A user who relies on the lifecycle plugins gets a deterministic guarantee that a handoff file one
stage writes and another reads follows its format, body included. The agent writes the artifact as
YAML. One pydantic model validates all of it, and a renderer turns it into the Markdown a person
reads, committed beside it. The agent never writes layout, so layout cannot drift, and every field
it writes is checked twice: when it is written, and again when a stage reads it, so a Bash edit, a
merge, or a session without the hooks cannot slip an unchecked file past a reader. This plan runs a
trial on the build plan in the three plugins that own it, `ceh-build-planning`,
`ceh-build-from-plan` and `ceh-check-build-against-plan`. The other formats follow once the user
approves the trial. The flow that matters most: an agent writes `product/plans/<slug>.yaml` with a
phase that has no Check. The hook reports the exact error to the agent right after the write and
leaves the Markdown unrendered. The agent fixes the YAML in the same turn, and the hook renders
`product/plans/<slug>.md`.

## Scope

**In:**

- `plan/v2`: the build plan as `product/plans/<slug>.yaml`, validated end to end by one pydantic
  model, with `product/plans/<slug>.md` rendered from it and committed beside it.
- A CLI, `artifact.py`, that checks a YAML artifact against its model, reports a committed `.md`
  that differs from its rendering, and renders the Markdown.
- A PostToolUse hook that validates every write to a `plan/v2` YAML file, reports the errors to
  the agent after the write, and renders the Markdown when the file is valid.
- A PreToolUse hook that denies a direct edit to a generated Markdown file and names its YAML.
- A read-time check: each trial skill runs `artifact.py check` on a `plan/v2` YAML before acting
  on it, and stops on an error.
- A loud warning, once per session, in place of a silent pass when the check cannot run (no uv, no
  network on the first install, an unknown format version).
- The skills of the three trial plugins writing, editing and re-checking the YAML, and
  `build-record-guard.py` reading Record entries from it.
- The two outside skills that append Record lines to a plan, `ceh-git-workflow:pull-request` and
  `ceh-testing:write-evidence-report`, reading and appending to the YAML when one exists. They
  change in prose only and get no hook or model.
- Hook fixtures in `checks/hooks.py`, a `validate.py` check that every model matches its YAML
  template and every copy is byte-identical, and uv in CI.
- Docs and a decision rule for the trial, each landing in the phase that creates what it governs:
  uv as a stated requirement, the `CEH_ARTIFACT_CHECK` switch, the copied files registered, and the
  format rules in STRATEGY and `decision-output-templates.md`.

**Out:**

- The other spine formats (`architecture`, `evidence`, `business-plan`, `vision`, `strategy`) and
  every report-only format: Phase 6, `unplanned` until the user approves the trial, because the
  mechanism should prove itself on one format before it is copied into many plugins.
- Converting existing `plan/v1` Markdown plans: they are records, so they stay as written. Skills
  keep editing a `v1` plan in place when no YAML exists beside it.
- Readers outside the trial that only read the plan, such as `whats-next`, `document-architecture`
  and `find-product-market-fit`: they keep reading `<slug>.md`, whose frontmatter and body
  `plan/v2` renders in the `v1` layout. They get the read-time check in Phase 6 if the trial holds.
- Updating the plugins' eval cases (`evals/`) to the YAML: they still pass against the rendered
  Markdown, and running them costs model calls, so only on request per `decision-evaluation.md`.
- A TypeScript or zod validator: `model_json_schema()` keeps that door open, and nobody needs it
  yet.
- Deferring between hook copies of different installed versions: accepted risk, see Design.

## Design

- **Why the vision allows it.** VISION principle 7 asks what failure guidance did not prevent. The
  rule rests on the user's explicit instruction to make handoff artifacts as deterministic and
  checkable as possible (VISION, Who overrides), plus any handoff break later observed, which the
  decision rule cites when one is seen. Two parts narrow what the agent may do, and each has its
  reason: the PostToolUse hook pushes the agent to fix an invalid file, which a reading stage would
  otherwise trust, and `generated-md-guard.py` denies a direct edit to a generated file, which the
  next render would silently overwrite. The vision stays as written, and the Phase 5 decision rule
  carries this argument.
- **Two files, one source.** `<slug>.yaml` is the source of truth. `<slug>.md` is generated, and
  both are committed: the Markdown stays readable on GitHub and in fresh clones, and the YAML is
  what agents read and edit. YAML is used over JSON because long prose reads and diffs cleanly in
  `|` block scalars. The rendered frontmatter is, in this order: `schema: plan/v2`,
  `generated_from: <slug>.yaml`, `title`, `status`, `created`, and `business_plan` when set, so
  readers that grep `status: built` keep working. The body keeps the `plan/v1` layout exactly.
- **The `plan/v2` model**, `references/plan-model.py` beside `plan-schema.md`, defining
  `NAME = "plan"`, `VERSION = 2`, the `Plan` model, `MODEL = Plan` (the name `artifact.py`
  validates with, the same in every format's model) and `render`. Every model sets
  `extra="forbid"` and `strict=True`, so a mistyped key, or a value YAML retyped (`yes` read as a
  bool), is an error. YAML keys are model aliases: `schema` is `Field(alias="schema")` on a field
  named `schema_`, and `in` is `Field(alias="in")` on `in_`, because `in` is a Python keyword and
  `schema` shadows a `BaseModel` attribute.

  | Key             | Type                                                                                                         |
  | --------------- | ------------------------------------------------------------------------------------------------------------ |
  | `schema`        | `Literal["plan/v2"]`                                                                                         |
  | `title`         | non-empty `str`, one line                                                                                    |
  | `status`        | `Literal["draft", "ready", "building", "built"]`                                                             |
  | `created`       | `date`                                                                                                       |
  | `business_plan` | `str`, optional                                                                                              |
  | `goal`          | non-empty `str`                                                                                              |
  | `scope.in`      | list of non-empty `str`, at least one                                                                        |
  | `scope.out`     | list of `{item: str, reason: str}`                                                                           |
  | `design`        | list of `{topic: str, decision: str}`, at least one. `decision` may hold Markdown, including a Mermaid block |
  | `phases`        | list of `{name, builds, check, status, evidence, note}`, at least one                                        |
  | `open`          | list of `{question: str, assumption: str}`, empty renders as `None`                                          |
  | `record`        | list of `{date: date, event, phase, details: str}`, at least one                                             |

  Phase `status` is `Literal["todo", "unplanned", "done"]`. `evidence` is required exactly when
  the status is `done`. `note` is an optional `str` allowed in any status, rendered after the
  Status value, and holds what `implement-from-plan` writes into a phase's Status today: a failed
  attempt, a check that could not run, a departure from Design. `event` is `Literal["Planned",
"Reviewed", "Built Phase", "Design changed", "Checked", "Evidence", "PR"]`. `phase` is an `int`
  of at least 1, required exactly when `event` is `Built Phase`, and rendered as
  `Built Phase <phase>:`. Model validators hold the rules across fields: `built` means every phase
  is `done`, `building` means at least one is `done`, and `draft` or `ready` means none is. Phases
  are numbered by their position, so the YAML holds no number to get wrong. Free-text fields
  (`goal`, `decision`, `builds`, `check`, `evidence`, `note`, `details`) are the only content the
  model cannot check past being non-empty.

- **Free text as block scalars.** In a plain YAML scalar, ` #` starts a comment, so
  `details: merged in PR #12` loads as `merged in PR`. The template writes every free-text field
  as a `|` block scalar, and `plan-schema.md` says why. The CLI also rejects a plain-scalar
  free-text value whose source line holds ` #` after the value it loaded, so a cut value is an
  error, not a silent loss.
- **Renderer**, `def render(plan: Plan, source: str) -> str` in the same model module, built from f-strings,
  stdlib only. The same YAML always renders to byte-identical Markdown. The model module is the
  whole format in code: model, validators and renderer.
- **Template**, `assets/plan.template.yaml`: the YAML skeleton the writer copies, placeholders as
  strings (`<title>`), with `schema: plan/v2` as its first key. `plan-schema.md` gains a `plan/v2`
  section that names the template and the model and gives the reason for each field, and keeps its
  `plan/v1` field list for as long as `v1` plans are edited. Its Record and Phase rules apply to
  both versions.
- **CLI**, `scripts/artifact.py`, a PEP 723 script with `requires-python = ">=3.10"` and
  `dependencies = ["pydantic>=2,<3", "pyyaml>=6,<7"]`, run as `uv run --script artifact.py
<command> <file>`. It finds models by globbing `**/references/*-model.py` under
  `Path(__file__).parent.parent`, the plugin root, which holds in every copy, and loads the one
  whose `NAME` and `VERSION` match with `importlib.util.spec_from_file_location`.
  - `check <yaml>` parses with `yaml.safe_load`, validates, and, when `<slug>.md` exists beside
    it, reports it as stale if its bytes differ from `render(plan)`.
  - `render <yaml>` checks the YAML, then leaves an `.md` that already matches untouched, and
    otherwise writes it to a temp file in the same folder and moves it into place with
    `os.replace`, retried briefly while Windows holds the target open, the temp file removed
    either way, so two renders at once never leave a half-written file or a stray `.tmp`.
  - Exit codes: `0` valid (and rendered), `1` errors as `<path>: <field path>: <error>` lines on
    stdout (a YAML syntax error as `<path>:<line>:<col>: <problem>`, a stale `.md` as `<path>:
stale, run render`), `2` any other failure with the exception on stdout, `3` no model for that
    `<name>/v<N>`. A rerun gives the same result and rewrites the same bytes, so a retry is safe.
- **Hooks**, both stdlib and run as `python3 -I -S`. Both are off with `CEH_ARTIFACT_CHECK=off`,
  and each honours `CEH_DISABLED_HOOKS` by its script stem, as every hook script in the repo does.
  - `scripts/artifact-render-hook.py`, PostToolUse, matcher `Edit|Write|MultiEdit`, timeout 120
    seconds (the first run installs pydantic). It acts on a `.yaml` whose first `schema:` key,
    after any `---` and comment lines, names a model in this plugin, and on any
    `product/plans/*.yaml` whatever its first line, so a plan missing its schema key is an error,
    not a skip. Then it runs `artifact.py render`. On exit 1 it prints
    `{"decision": "block", "reason": "<errors>\nFix <file>. The Markdown was not regenerated."}`.
    The tool has already run, so the invalid YAML stays on disk until the agent fixes it. On exit 2
    or 3, or with no uv on `PATH`, it prints
    `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "<file> was not checked against its format: <why>. <how to fix>"}}`,
    once per session and reason, using a marker file in the temp folder keyed by `session_id`.
  - `scripts/generated-md-guard.py`, PreToolUse, matcher `Edit|Write|MultiEdit`. When the target
    `.md` has `generated_from:` in its frontmatter, it denies the edit with "this file is
    generated, edit <yaml> instead", in the deny shape `build-record-guard.py` already uses.
    Each installed plugin's copy of a hook runs separately and in parallel. Copies of the same
    version give the same verdict and, through `os.replace`, the same file. Copies of different
    versions (the plugins update on their own schedules) can disagree. That is accepted for the
    trial, because a version bump of the model lands in all three plugins in one PR, and the Phase 6
    plan revisits it.
- **Read-time check.** `review-build-plan`, `implement-from-plan` and `check-build-against-plan`
  run `artifact.py check` on a `plan/v2` YAML before acting on it. Exit 1 stops the skill with
  the errors, and a stale `.md` is fixed by running `render` first. Exit 2 or 3, or no uv, is
  stated in the reply as "not checked", and the skill goes on. The outside skills read and append
  Record state from the YAML when one exists, stage both files, and say in the reply when the
  `.md` was not re-rendered because no trial plugin is installed.
- **Who carries what.** The model, template, CLI and hooks live in all three trial plugins,
  copied word for word per `decision-shared-standards-duplication.md`, with no shared base plugin,
  per STRATEGY. The two outside skills only change prose, so they need no copy and no
  `dependencies` entry: reading or appending to a handoff file is not a dependency, per STRATEGY
  rule 2.
- **Repo checks.**
  - `checks/templates.py` gains two changes: for `.template.yaml`, the schema line is the first
    `schema:` key, not the line after `---`, and the Output-section rule accepts a skill that cites
    either `.template.md` or `.template.yaml`. The schema-file, citation and copy-identity rules
    apply to both suffixes unchanged.
  - `checks/hooks.py` gains fixtures for both hooks, keyed `<plugin>/<script>` for every copy:
    block, render, non-plan file, a plan YAML opening with `---`, no-uv warning, generated `.md`
    denied, `CEH_ARTIFACT_CHECK=off`, and `CEH_DISABLED_HOOKS`. The render and block fixtures are
    skipped when `shutil.which("uv")` is None, the shellcheck precedent in `checks/scripts.py`.
  - `checks/artifact_models.py`, added to `CHECKS` in `validate.py` and to the tool's README, in
    two parts. The stdlib part, in Phase 3 with the copies it guards, checks that each
    `*-model.py` has its `<name>-schema.md` and `../assets/<name>.template.yaml`, and that every
    copy of the model, `artifact.py` and both hooks is byte-identical. The uv part, in Phase 4,
    runs `uv run --script tools/validate-plugins/model_vs_template.py`, which checks that each
    template's keys, nested lists included, are exactly the model's aliases as
    `model_json_schema()` reports them. With no uv it prints a skip note and passes.
  - CI adds `astral-sh/setup-uv` to `validate.yml` in Phase 2, so the uv fixtures and checks
    always run there from the first hook on.
- **Requirement change**: uv becomes a stated requirement of the three trial plugins, named in
  their READMEs and `docs/GETTING_STARTED.md`. Without uv, the plugins still work, the YAML goes
  unchecked and unrendered, and the hook and each read-time check say so once.
- **Landing.** Each phase lands as its own PR with its version bumps (`ceh-build-planning`,
  `ceh-build-from-plan` and `ceh-check-build-against-plan` MINOR in the phase that gives them
  hooks, PATCH otherwise, and `ceh-git-workflow` and `ceh-testing` PATCH in Phase 3), its
  `CHANGELOG.md` entry and its `docs/PLUGIN_VERSIONS.md` rows.

## Phases

### Phase 1: Model, renderer, template, CLI and format rules

- **Builds:** the `plan/v2` model, renderer, template and CLI in `ceh-build-planning`; the
  `plan/v2` section in all three copies of `plan-schema.md` at once; the `templates.py` changes;
  `decision-output-templates.md` and STRATEGY handoff rule 3 allowing a YAML template, a model
  beside the schema file, and a generated Markdown.
- **Check:** a hand conversion of this plan to `artifact-validation.yaml` in the scratchpad passes
  `uv run --script plugins/standalone/ceh-build-planning/scripts/artifact.py render <file>`, and
  the rendered Markdown, frontmatter included, matches this file apart from the
  `schema: plan/v2` and `generated_from` lines, with `diff` showing only whitespace. Each of these
  copies exits 1 naming its field path: a phase missing `check`, `status: done` without
  `evidence`, `status: built` with a `todo` phase, `status: ready` with a `done` phase, a
  `Built Phase` entry without `phase`, an unknown key, an unquoted `details: PR #12`, and a YAML
  syntax error (with line and column). A copy with `schema: plan/v3` exits 3, and an edited `.md`
  beside a valid YAML is reported stale. `python tools/validate-plugins/validate.py` is green.
- **Status:** done, a scratchpad `selfcheck.py` ran every case above through `artifact.py` and
  printed "ALL PASSED", and `validate.py` printed "OK: all plugin checks passed". The conversion
  to YAML was made by a scratch converter, not by hand, and the round-trip `diff -w` showed one
  blank line. `plan.template.yaml` landed in all three plan plugins in this phase, not in Phase 3,
  because the shared `plan-schema.md` cites `../assets/plan.template.yaml` and a reference must
  resolve in every copy. `decision-skill-bundled-files.md` and `plugins/CLAUDE.md` also changed, to
  admit `<schema>-model.py` in `references/` and `scripts/artifact.py` as a script bundle.

### Phase 2: Hooks in `ceh-build-planning`, with fixtures and uv in CI

- **Builds:** both hooks, wired in `ceh-build-planning/hooks/hooks.json`; their fixtures in
  `checks/hooks.py`; the `setup-uv` step in `.github/workflows/validate.yml`.
- **Check:** `python tools/validate-plugins/validate.py` is green with every fixture listed under
  Repo checks passing, and CI on the PR is green with the uv fixtures run, not skipped, as its log
  shows. With `UV_CACHE_DIR` pointing at an empty scratchpad folder, the first `artifact.py check`
  is timed and the time is written in this phase's Status, which settles the timeout question
  under Open.
- **Status:** done, `python tools/validate-plugins/validate.py` printed "OK: all plugin checks
  passed" locally with uv, and CI went green on the PR, where `checks/hooks.py` now fails when
  `CI` is set and uv is missing, so green means the uv fixtures ran. Breaking each hook on purpose
  turned three fixtures red. The first `artifact.py check` with an empty `UV_CACHE_DIR` took
  1.9 s, and a warm one 0.7 s, so the 120-second timeout stands. The plugin README's Hooks section
  and the `CEH_ARTIFACT_CHECK` row in `docs/ENVIRONMENT_VARIABLES.md` landed here, not in Phase 5,
  because a shipped hook documents its switch.

### Phase 3: Skills write and re-check the YAML, and the copies

- **Builds:** `write-build-plan` writes the YAML from the template, and `review-build-plan`
  re-checks it and appends its Reviewed entry. The model, template, CLI and hooks are copied into
  `ceh-build-from-plan` and `ceh-check-build-against-plan`, with fixtures for each copy, every
  copy registered in `docs/CROSS_REFERENCES.md`, and the stdlib part of `checks/artifact_models.py`
  in `CHECKS` and the tool's README, so the copies cannot drift from the PR that creates them. `implement-from-plan` re-checks the YAML, writes
  its minimal plan in step 1 as `plan/v2` YAML from the template, and edits phase status, `note`,
  Design and Record in the YAML. `build-record-guard.py` detects a new `event: Built Phase` entry
  in a plan YAML as it detects the Markdown line today. `check-build-against-plan` re-checks and
  reads the YAML and appends its Checked entry to it. `pull-request` and `write-evidence-report`
  read and append Record state in the YAML when one exists, stage both files, and note an
  unrendered `.md`. Every skill still edits a `plan/v1` Markdown plan in place when no YAML exists.
- **Check:** `python tools/validate-plugins/validate.py` is green, and adding a line to one
  `plan-model.py` copy, then to one `artifact.py` copy, turns it red for copy drift (revert
  both). The guard, piped a Write that
  adds an `event: Built Phase` entry with no skill started, denies it. Then one real session in a
  scratch repo with the three plugins installed locally: "plan a CLI that counts words" writes a
  valid YAML and its rendered Markdown. "Add a phase 2 with no check" is blocked, and the session
  records whether the agent fixed the YAML in the same turn. "Build phase 1" re-checks the plan,
  moves phase 1 to `done`, appends a Built Phase entry, and re-renders the Markdown. This check is
  manual because only a live session shows the skills, hooks and guard working together, and it
  spends model calls, so the builder asks the user whether to run it in the session or hand over
  the steps.
- **Status:** done, `python tools/validate-plugins/validate.py` printed "OK: all plugin checks
  passed", the guard fixture denies a hand-written `event: Built Phase` entry, and a planted line
  in one copy of `plan-model.py` and of `artifact.py` turned `artifact-models` red. The user chose
  to run the live session here: four `claude -p` prompts on Sonnet in a scratch repo, about $1.10.
  "Plan a small CLI that counts the words in a text file" wrote a valid YAML and its rendered
  Markdown. "Build phase 1" re-checked the plan, built test first, moved phase 1 to `done`, added a
  Built Phase entry with `phase: 1`, set `building` and re-rendered, and `artifact.py check` exits
  0 on the result. Two seeded broken writes never reached the hook: asked for a phase "with no
  check", the agent filled `check` with a note because the schema requires it, and asked for the
  name "Lines flag #2", it quoted the value because `plan-schema.md` explains ` #`. So the
  same-turn fix after a block is proven only by the piped fixtures, not live. The first render in
  the session collided on Windows (access denied on the rename, a stray `.tmp` left), so
  `artifact.py` now skips an unchanged `.md`, retries the rename, and always removes the temp
  file. Forty parallel renders in a scratch race test all passed after the fix, but the old code
  passed too, so the collision was not reproduced outside the session.

### Phase 4: Model-to-template repo check

- **Builds:** the uv part of `checks/artifact_models.py`, and `model_vs_template.py`, in the
  tool's README.
- **Check:** `python tools/validate-plugins/validate.py` is green. Removing `open` from every
  `plan.template.yaml` copy turns it red, naming the template and the model (then revert). CI on
  the PR is green, with the uv part run and not skipped, as its log shows.
- **Status:** done, `python tools/validate-plugins/validate.py` printed "OK: all plugin checks
  passed". With `open` removed from all three `plan.template.yaml` copies, `artifact-models`
  reported each one: "does not match its model: (top level): missing ['open']", then the copies
  were restored. In CI, `artifact-models` fails when uv is missing, so a green run means the
  comparison ran.

### Phase 5: Docs and decision rule

- **Builds:** the requirement change in the three READMEs and `docs/GETTING_STARTED.md`;
  `CEH_ARTIFACT_CHECK` in `docs/ENVIRONMENT_VARIABLES.md`, and `ceh-build-planning` and
  `ceh-check-build-against-plan` added to its `CEH_DISABLED_HOOKS` row; the Build row of
  STRATEGY's spine table naming `product/plans/<slug>.yaml` beside the `.md`; a new
  `.claude/rules/decision-artifact-validation.md` through
  `ceh-every-session:record-project-decisions`, carrying the argument under Why the vision allows
  it.
- **Check:** `python tools/validate-plugins/validate.py` is green, and
  `grep -l CEH_ARTIFACT_CHECK docs/ENVIRONMENT_VARIABLES.md`,
  `grep -l "plans/<slug>.yaml" docs/STRATEGY.md` and
  `grep -l "Who overrides" .claude/rules/decision-artifact-validation.md` each find their file.
- **Status:** todo

### Phase 6: Remaining formats

- **Builds:** YAML models and renderers for `architecture`, `evidence`, `business-plan`, `vision`
  and `strategy`, then the report-only formats, and the read-time check in readers outside the
  trial, planned in full once the user approves the trial.
- **Check:** planned with the phase.
- **Status:** unplanned

## Open

None

## Record

- 2026-11-06 Planned: status ready
- 2026-11-06 Reviewed: Revise first, 5 blocking (schema copies drift in Phase 1, hooks lack fixtures, Phases paragraph cannot round-trip, no note field for a todo phase, write-time hook does not cover every write)
- 2026-11-06 Design changed: was "defining `NAME = "plan"`, `VERSION = 2`, the `Plan` model and `render`", now adds "`MODEL = Plan`", because `artifact.py` needs one name to validate with in every format's model
- 2026-11-06 Design changed: was "`def render(plan: Plan) -> str`", now "`def render(plan: Plan, source: str) -> str`", because the rendered frontmatter's `generated_from` names the source YAML
- 2026-11-06 Built Phase 1: scratchpad selfcheck.py through artifact.py, "ALL PASSED"
- 2026-11-06 PR: #199 https://github.com/cheneeheng/ceh-claude-code-library/pull/199
- 2026-11-06 Design changed: was "`checks/artifact_models.py` ... checks ... that every copy of the model, `artifact.py` and both hooks is byte-identical" in Phase 4, now its stdlib part lands in Phase 3, because Phase 3 creates the copies and nothing else catches their drift until Phase 4
- 2026-11-06 PR: #201 https://github.com/cheneeheng/ceh-claude-code-library/pull/201
- 2026-11-06 Built Phase 2: `python tools/validate-plugins/validate.py`, "OK: all plugin checks passed"
- 2026-11-06 PR: #203 https://github.com/cheneeheng/ceh-claude-code-library/pull/203
- 2026-11-06 Design changed: was "`render <yaml>` checks the YAML, then writes the rendered `.md` to a temp file in the same folder and moves it into place with `os.replace`", now it also skips an unchanged `.md`, retries the rename and always removes the temp file, because the live session's first render collided on Windows and left a stray `.tmp`
- 2026-11-06 Built Phase 3: `python tools/validate-plugins/validate.py`, "OK: all plugin checks passed", and the live session in a scratch repo
- 2026-11-06 PR: #204 https://github.com/cheneeheng/ceh-claude-code-library/pull/204
- 2026-11-06 Built Phase 4: `python tools/validate-plugins/validate.py`, "OK: all plugin checks passed"
