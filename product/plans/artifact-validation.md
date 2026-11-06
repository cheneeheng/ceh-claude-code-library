---
schema: plan/v1
title: Handoff files as YAML validated by pydantic, with Markdown generated from it
status: ready
created: 2026-11-06
---

## Goal

A user who relies on the lifecycle plugins gets a deterministic guarantee that a handoff file one
stage writes and another reads follows its format, body included. The agent writes the artifact as
YAML. One pydantic model validates all of it, and a renderer turns it into the Markdown a person
reads, committed beside it. The agent never writes layout, so layout cannot drift, and every field
it does write is checked. This plan runs a trial on the build plan in the three plugins that own it,
`ceh-build-planning`, `ceh-build-from-plan` and `ceh-check-build-against-plan`. The other formats
follow once the user approves the trial. The flow that matters most: an agent writes
`product/plans/<slug>.yaml` with a phase that has no Check. The hook rejects the write with the
exact error, the agent fixes the YAML in the same turn, and the hook renders
`product/plans/<slug>.md`.

## Scope

**In:**

- `plan/v2`: the build plan as `product/plans/<slug>.yaml`, validated end to end by one pydantic
  model, with `product/plans/<slug>.md` rendered from it and committed beside it.
- A CLI, `artifact.py`, that checks a YAML artifact against its model and renders its Markdown.
- A PostToolUse hook that validates every write to a `plan/v2` YAML file, blocks the write with
  the errors, and renders the Markdown when the file is valid.
- A PreToolUse hook that denies a direct edit to a generated Markdown file and names its YAML.
- A loud warning in place of a silent pass when the check cannot run (no uv, no network on the
  first install, an unknown format version).
- The skills of the three trial plugins writing and editing the YAML, and `build-record-guard.py`
  reading Record entries from it.
- The two outside skills that append Record lines to a plan, `ceh-git-workflow:pull-request` and
  `ceh-testing:write-evidence-report`, appending to the YAML when one exists. They change in prose
  only and get no hook or model.
- A `validate.py` check that every model matches its YAML template and that every copy of a
  model, of the CLI and of the hooks is byte-identical, with uv installed in CI.
- Docs and a decision rule for the trial: uv as a stated requirement, the `CEH_ARTIFACT_CHECK`
  switch, the copied files registered, the format rules in STRATEGY and
  `decision-output-templates.md` updated.

**Out:**

- The other spine formats (`architecture`, `evidence`, `business-plan`, `vision`, `strategy`) and
  every report-only format: Phase 6, `unplanned` until the user approves the trial, because the
  mechanism should prove itself on one format before it is copied into many plugins.
- Converting existing `plan/v1` Markdown plans: they are records, so they stay as written. Skills
  keep editing a `v1` plan in place when no YAML exists beside it.
- Readers that only read the plan, such as `whats-next`, `document-architecture` and
  `find-product-market-fit`: they keep reading `<slug>.md`, whose layout `plan/v2` renders
  unchanged.
- Updating the plugins' eval cases (`evals/`) to the YAML: they still pass against the rendered
  Markdown, and running them costs model calls, so only on request per `decision-evaluation.md`.
- A TypeScript or zod validator: `model_json_schema()` keeps that door open, and nobody needs it
  yet.
- Validating a plan when a stage reads it: the write-time hook covers every write the plugins
  make.

## Design

- **Why this fits VISION principle 7 as written.** Principle 7 limits enforcement that narrows
  what an agent may do. This check narrows nothing: it holds a file that is a contract between two
  stages to the format the reading stage relies on. A broken handoff fails silently, in a later
  session and in a different plugin, and prose cannot catch that because the writer never learns
  of it. The vision stays as written, and the Phase 5 decision rule carries this argument.
- **Two files, one source.** `<slug>.yaml` is the source of truth. `<slug>.md` is generated, opens
  with frontmatter `schema: plan/v2` and `generated_from: <slug>.yaml`, and keeps the `plan/v1`
  body layout exactly, so a reader of the Markdown sees no change. Both are committed: the
  Markdown stays readable on GitHub and in fresh clones, and the YAML is what agents read and
  edit. YAML is used over JSON because long prose reads and diffs cleanly in `|` block scalars.
- **The `plan/v2` model**, `references/plan-model.py` beside `plan-schema.md`, defining
  `NAME = "plan"`, `VERSION = 2`, the `Plan` model and `render`. Every model sets
  `extra="forbid"` and is strict, so a mistyped key, or a value YAML retyped (`yes` read as a
  bool), is an error and the agent quotes it:

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
  | `phases`        | list of `{name, builds, check, status, evidence}`, at least one                                              |
  | `open`          | list of `{question: str, assumption: str}`, empty renders as `None`                                          |
  | `record`        | list of `{date: date, event, details: str}`, at least one                                                    |

  Phase `status` is `Literal["todo", "unplanned", "done"]`, and `evidence` is required exactly
  when the status is `done`. `event` is `Literal["Planned", "Reviewed", "Built Phase", "Design
changed", "Checked", "Evidence", "PR"]`. Cross-field rules are model validators: `built` means
  every phase is `done`, and `building` means at least one is `done`. Phases are numbered by their
  position, so the YAML holds no number to get wrong. Free-text fields (`goal`, `decision`,
  `details`) are the only content the model cannot check past being non-empty.

- **Renderer**, `def render(plan: Plan) -> str` in the same model module, built from f-strings,
  stdlib only. The same YAML always renders to byte-identical Markdown. The model module is the
  whole format in code: model, validators and renderer.
- **Template**, `assets/plan.template.yaml`: the YAML skeleton the writer copies, placeholders as
  strings (`<title>`), opening with `schema: plan/v2`. `plan-schema.md` keeps the reasons for each
  field and the Record and Phase rules, and drops its field list in favour of the model.
- **CLI**, `scripts/artifact.py`, a PEP 723 script with `requires-python = ">=3.10"` and
  `dependencies = ["pydantic>=2,<3", "pyyaml>=6,<7"]`, run as `uv run --script artifact.py
<command> <file>`. `check <yaml>`: it reads `schema:`, loads the plugin's `*-model.py` whose
  `NAME` and `VERSION` match, parses with `yaml.safe_load`, and validates. `render <yaml>`: it
  checks, then writes the rendered `.md` beside the YAML. Exit codes: `0` valid (and rendered), `1`
  errors as `<path>: <field path>: <error>` lines on stdout, `3` no model for that
  `<name>/v<N>`. A rerun gives the same result and rewrites the same bytes, so a retry is safe.
- **Hooks**, both stdlib and run as `python3 -I -S`, both off with `CEH_ARTIFACT_CHECK=off`:
  - `scripts/artifact-render-hook.py`, PostToolUse, matcher `Edit|Write|MultiEdit`, timeout 120
    (the first run installs pydantic). It exits silently unless the file is a `.yaml` whose first
    line is `schema: <name>/v<N>` with a model in this plugin. Then it runs `artifact.py render`.
    On exit 1 it prints `{"decision": "block", "reason": "<errors>\nFix <file>. The Markdown was
not regenerated."}`. On exit 3, with no uv, or on any other failure, it prints an
    `additionalContext` warning that names the file and the reason.
  - `scripts/generated-md-guard.py`, PreToolUse, matcher `Edit|Write|MultiEdit`. When the target
    `.md` has `generated_from:` in its frontmatter, it denies the edit with "this file is
    generated, edit <yaml> instead".
    When two installed plugins carry the same hooks, both give the same verdict and render the same
    bytes, which is harmless.
- **Who carries what.** The model, template, CLI and hooks live in all three trial plugins,
  copied word for word per `decision-shared-standards-duplication.md`, with no shared base plugin,
  per STRATEGY. The two outside skills only change prose, so they need no copy and no
  `dependencies` entry: reading or appending to a handoff file is not a dependency, per STRATEGY
  rule 2.
- **Repo check**, `tools/validate-plugins/checks/artifact_models.py`, run by `validate.py`. A
  stdlib part checks that each `*-model.py` has its `<name>-schema.md` and
  `../assets/<name>.template.yaml`, and that every copy of the model, `artifact.py` and both hooks
  is byte-identical. A uv part runs `uv run --script tools/validate-plugins/model_vs_template.py`,
  which checks that each template's keys, nested lists included, are exactly the model's fields.
  With no uv on `PATH`, the uv part prints a skip note and passes, the same precedent as
  shellcheck, and CI adds `astral-sh/setup-uv` so it always runs there. `checks/templates.py`
  accepts `.template.yaml` beside `.template.md`, with the same schema-line, citation and
  copy-identity rules.
- **Requirement change**: uv becomes a stated requirement of the three trial plugins, named in
  their READMEs and `docs/GETTING_STARTED.md`. Without uv, the plugins still work, the YAML goes
  unchecked and unrendered, and the hook warns on every plan write.

## Phases

### Phase 1: Model, renderer, template and CLI

- **Builds:** the `plan/v2` model, renderer, template and CLI in `ceh-build-planning`; the
  `plan-schema.md` update; the `templates.py` change for `.template.yaml`.
- **Check:** a hand conversion of this plan to `artifact-validation.yaml` in the scratchpad passes
  `uv run --script plugins/standalone/ceh-build-planning/scripts/artifact.py render <file>`, and
  the rendered Markdown matches this file's body section for section, with `diff` showing only
  whitespace. Copies with a phase missing `check`, `status: done` without `evidence`, `status:
built` with a `todo` phase, and an unknown key each exit 1, naming the field path. A copy with
  `schema: plan/v3` exits 3. `python tools/validate-plugins/validate.py` is green.
- **Status:** todo

### Phase 2: Hooks in `ceh-build-planning`

- **Builds:** both hooks, wired in `ceh-build-planning/hooks/hooks.json`.
- **Check:** each of these, piped into its hook as `{"cwd": "<repo>", "tool_name": "Write",
"tool_input": {"file_path": "<file>"}}`: a broken YAML prints a `"decision": "block"` object
  naming the error, and its `.md` is untouched; a valid YAML prints nothing and its `.md` is
  rendered; `README.md` prints nothing and starts no uv; the broken YAML with uv removed from
  `PATH` prints an `additionalContext` warning; an edit to a generated `.md` is denied, naming
  the YAML; `CEH_ARTIFACT_CHECK=off` prints nothing for each.
- **Status:** todo

### Phase 3: Skills write the YAML, and the copies

- **Builds:** `write-build-plan` and `review-build-plan` write and append to the YAML. The model,
  template, CLI and hooks are copied into `ceh-build-from-plan` and `ceh-check-build-against-plan`.
  `implement-from-plan` edits phase status, Design and Record in the YAML.
  `build-record-guard.py` detects a new `event: Built Phase` entry in a plan YAML as it detects
  the Markdown line today. `check-build-against-plan` reads the YAML. `pull-request` and
  `write-evidence-report` append to the YAML when one exists beside the plan. Every skill still
  edits a `plan/v1` Markdown plan in place when no YAML exists.
- **Check:** `python tools/validate-plugins/validate.py` is green. The guard, piped a Write that
  adds an `event: Built Phase` entry with no skill started, denies it. Then one real session in a
  scratch repo with the three plugins installed locally: "plan a CLI that counts words" writes a
  valid YAML and its rendered Markdown, and "build phase 1" moves that phase to `done`, appends a
  Built Phase entry, and the Markdown re-renders. This one is manual because only a live session
  shows that the skills, hooks and guard work together.
- **Status:** todo

### Phase 4: Repo check and CI

- **Builds:** the repo check, `model_vs_template.py`, and the `setup-uv` step in
  `.github/workflows/validate.yml`.
- **Check:** `python tools/validate-plugins/validate.py` is green. Removing `open` from one
  `plan.template.yaml` copy turns it red, naming the template and the model, and adding a field to
  one `plan-model.py` copy turns it red for copy drift (revert both). CI on the PR is green, with
  the uv part run and not skipped, as its log shows.
- **Status:** todo

### Phase 5: Docs and decision rule

- **Builds:** the requirement change in the three READMEs and `docs/GETTING_STARTED.md`;
  `CEH_ARTIFACT_CHECK` in `docs/ENVIRONMENT_VARIABLES.md`; every copied file in
  `docs/CROSS_REFERENCES.md`; STRATEGY handoff rule 3 and `decision-output-templates.md` allowing
  a YAML template, a model beside the schema file, and a generated Markdown; a new
  `.claude/rules/decision-artifact-validation.md` through
  `ceh-every-session:record-project-decisions`, carrying the principle 7 argument.
- **Check:** `python tools/validate-plugins/validate.py` is green, and
  `grep -l CEH_ARTIFACT_CHECK docs/ENVIRONMENT_VARIABLES.md` and
  `grep -l generated_from docs/STRATEGY.md .claude/rules/decision-output-templates.md` find all
  three files.
- **Status:** todo

### Phase 6: Remaining formats

- **Builds:** YAML models and renderers for `architecture`, `evidence`, `business-plan`, `vision`
  and `strategy`, then the report-only formats, planned in full once the user approves the trial.
- **Check:** planned with the phase.
- **Status:** unplanned

Each phase lands as its own PR with its version bumps (`ceh-build-planning`,
`ceh-build-from-plan` and `ceh-check-build-against-plan` MINOR in the phase that gives them hooks,
PATCH otherwise, and `ceh-git-workflow` and `ceh-testing` PATCH in Phase 3), its `CHANGELOG.md`
entry and its `docs/PLUGIN_VERSIONS.md` rows.

## Open

- How long uv's first install of pydantic and PyYAML takes on a cold machine: assumed under the
  120-second hook timeout. Phase 2 measures it, and a slower result raises the timeout.
- Whether agents write long Design entries well inside YAML block scalars: assumed yes. Phase 3's
  real session shows it, and a poor result is reported before Phase 6 is planned.

## Record

- 2026-11-06 Planned: status ready
