# flow.yaml schema (version 1)

The config a built workflow runs from. `build-agentic-workflow` writes it and checks it against this
file; `run-agentic-workflow` reads it and checks it again before step 1. Two checkers in two plugins,
`ceh-workflow-builder` and `ceh-workflow-runner`, each carrying this file word for word, so the
rules below are the only rules.

The file lives at `.claude/skills/<name>-flow/flow.yaml`, beside the thin trigger skill that hands it
to the runner. **Every path in it is relative to the directory holding `flow.yaml`** (schemas,
scripts), except `.claude/workflows/<name>.js` and `repo_file` entries, which are relative to the
repo root.

## Format rules

- Plain YAML: mappings, lists and scalars. No anchors, aliases, merge keys, tags or multiple
  documents, because the runner is a model reading the file, not a YAML library, and those make the
  same file read two ways. Comments are fine.
- Unknown keys are an error, not ignored: a typo such as `retires:` would otherwise read as working
  config.
- Placeholders, substituted by the runner in every string value:

| Placeholder      | Becomes                                                            |
| ---------------- | ------------------------------------------------------------------ |
| `{run}`          | absolute path of this run's directory                              |
| `{run_id}`       | the run id, the start time `YYYYMMDD-HHMM` (`-2`, `-3` on a clash) |
| `{input.<name>}` | the value of a declared input                                      |
| `{item}`         | the current fan-out item id, in `fan_out.output` only              |

- **Secrets only by reference.** A value names the environment variable or secret-manager key, never
  the secret. The stage that needs it resolves it. A literal credential in the file is an error.

## Top-level keys

| Key           | Required | Meaning                                                                                                           |
| ------------- | -------- | ----------------------------------------------------------------------------------------------------------------- |
| `version`     | yes      | The integer `1`. Any other value fails.                                                                           |
| `name`        | yes      | Kebab-case flow name, the `<name>` in `<name>-flow` and in the run path. Not one of the reserved launch args.     |
| `description` | yes      | One line: what the flow does.                                                                                     |
| `resumable`   | no       | `true` writes `run-state.md` and allows resume (spec question 7). Default `false`: one sitting, always a new run. |
| `inputs`      | no       | List of launch arguments the flow accepts, below.                                                                 |
| `stages`      | yes      | Non-empty list, run in order.                                                                                     |

### `inputs`

| Key           | Required | Meaning                                                                                      |
| ------------- | -------- | -------------------------------------------------------------------------------------------- |
| `name`        | yes      | Kebab-case, unique, and not `config`, `mode`, `resume` or `approve`. Passed as `name=value`. |
| `required`    | no       | Default `false`. A missing required input is asked for (interactive) or fails (headless).    |
| `default`     | no       | Used when the input is not passed. Meaningless with `required: true`.                        |
| `description` | no       | What it is, for the ask and for the invocation docs.                                         |

## Stages

| Key               | Required               | Meaning                                                                                                                                                                                                                 |
| ----------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`              | yes                    | Kebab-case, unique across the flow. Named in run state, `approve=` and the status line.                                                                                                                                 |
| `run`             | yes                    | What the stage does, per kind below.                                                                                                                                                                                    |
| `reads`           | no                     | Inputs from earlier stages or the repo.                                                                                                                                                                                 |
| `writes`          | no                     | Outputs this stage produces.                                                                                                                                                                                            |
| `approval`        | no                     | A human confirmation before the stage.                                                                                                                                                                                  |
| `unsafe_to_rerun` | no                     | `true` when running twice damages something (spec question 8). Needs `world_check`.                                                                                                                                     |
| `world_check`     | with `unsafe_to_rerun` | A falsifiable condition that is true only when the stage's effect has not happened yet.                                                                                                                                 |
| `fan_out`         | no                     | Run an `agent` stage once per item, in parallel.                                                                                                                                                                        |
| `tools`           | no                     | Tool permission rules the stage and its gate need beyond Read, Write and Edit, written as `--allowedTools` entries such as `Bash(uv run pytest:*)`. Headless runs have nobody to prompt, so the builder collects these. |
| `gate`            | yes                    | What must be true before the next stage. The last stage's gate is the flow's done condition.                                                                                                                            |

### `run` kinds

| `kind`     | Keys                                                                                             | The runner does                                                                                             |
| ---------- | ------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| `skill`    | `skill`, `args` (string), `fallback`, `instructions`                                             | Calls the Skill tool in its own context, with `args` plus `run={run}`.                                      |
| `agent`    | `subagent_type` (default `general-purpose`), exactly one of `instructions` or `skill`            | Dispatches the Agent tool. The prompt carries `{run}`, every input path and every schema path.              |
| `script`   | `script` (path), `args` (list of strings)                                                        | Runs `bash <path> <args>` with Bash. A non-zero exit is a red gate.                                         |
| `inline`   | `instructions`                                                                                   | Does the work itself, in its own context.                                                                   |
| `workflow` | `workflow` (name of `.claude/workflows/<name>.js`), `args` (mapping), `fallback`, `instructions` | Calls the Workflow tool by name with `args`, waits, and writes the result to the stage's one `writes` file. |

`fallback` is `fail` (default), `agent` or `inline`, and applies only when the capability is
**absent**: the Workflow tool is not available, or a plugin-namespaced skill (`plugin:skill`) is not
installed. `agent` and `inline` run the stage's `instructions` instead, so those are required with
them. A call that is attempted and denied or errors is a failed stage, never a fallback: a fallback
there would hide a missing permission.

### `reads` and `writes`

Handoff is always a file. Each entry has exactly one of `artifact` or `repo_file`.

`writes` entries:

| Key         | Meaning                                                                                                  |
| ----------- | -------------------------------------------------------------------------------------------------------- |
| `artifact`  | Path under `{run}`. A trailing `/` means a directory of per-item files.                                  |
| `schema`    | Path to the handoff schema doc. Required when any later stage reads the artifact.                        |
| `repo_file` | A committed repo file this stage creates or amends, in a format that already has an owner.               |
| `owner`     | With `repo_file`, required: what owns its format (a skill, a manifest spec). No schema is copied for it. |

`reads` entries:

| Key         | Meaning                                                                                                |
| ----------- | ------------------------------------------------------------------------------------------------------ |
| `artifact`  | Path under `{run}` that an earlier stage writes. Needs `from`.                                         |
| `from`      | The `id` of that earlier stage. The schema is the one on its `writes` entry: one writer, many readers. |
| `repo_file` | A repo file read in place, never copied into the run directory. Needs `owner`. `from` is optional.     |
| `owner`     | What owns the file's format.                                                                           |

Before a stage runs, the runner checks that every `reads` file exists, because an intervening stage
may have failed. The schema is cited in the stage's dispatch so a subagent, which sees nothing else,
knows the shape.

### `approval`

A confirmation before the stage runs: an irreversible step (spec question 9) or a human go/no-go on
earlier output (spec question 3). A proof only a human can judge is an `approval` on the _next_
stage. When it is the final stage's proof, add a last `inline` stage that reports and carries the
approval.

| Key        | Required | Meaning                                                                                                                         |
| ---------- | -------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `kind`     | yes      | `confirm` (irreversible step) or `go-no-go` (judgement on earlier output). Same mechanics, different wording.                   |
| `show`     | yes      | What the human sees: the exact data, batch or diff. One approval shows a whole batch, not one prompt per item.                  |
| `headless` | no       | `stop` (default), `preapproved-only` or `fail`. There is no "proceed anyway".                                                   |
| `covers`   | no       | Ids of the stages immediately following, that share this approval (merge then tag). Only mechanical gates may sit between them. |

`headless` values:

- `stop` — end the run as `awaiting-approval <stage-id>`; a later launch supplies the approval.
- `preapproved-only` — proceed only if the launch passed `approve=<stage-id>`, else stop as above.
- `fail` — end as `failed <stage-id> approval-required`.

A decline is `failed <stage-id> declined`, with the stage left `pending` so a resumed run asks again.

### `fan_out`

Agent stages only. One worker per item, each writing its own file.

| Key            | Required | Meaning                                                                                          |
| -------------- | -------- | ------------------------------------------------------------------------------------------------ |
| `items_from`   | yes      | An artifact named in this stage's `reads`. Its schema must say where the item list is.           |
| `item_id`      | no       | How to turn an item into a filesystem-safe id. Default: its heading or first field, kebab-cased. |
| `max_parallel` | yes      | Workers at once, 1 to 16.                                                                        |
| `max_items`    | yes      | Most items accepted. More fails the stage as `too-many-items`, so cost is bounded by the config. |
| `output`       | yes      | Per-worker file, under `{run}`, containing `{item}`. Must sit inside a directory `writes` entry. |

After the workers return, the runner counts output files against the item list before the gate runs,
since a worker that died leaves no file rather than a failing one. A resumed run dispatches only the
items with no file. A single merged artifact comes from a later `inline` stage.

### `gate`

| Key       | Required     | Meaning                                                                                                                |
| --------- | ------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `check`   | yes          | Falsifiable: a command's exit, a file's existence, the presence of every required field in a schema. Not "looks good". |
| `on_fail` | yes          | `stop` or `retry`.                                                                                                     |
| `retry`   | with `retry` | `max` (1 to 5 further attempts) and `changes` (what is different on the next attempt).                                 |

A red gate stops the run, or retries within the bound and then stops. It never continues degraded
and never skips ahead.

## Validation rules

The builder and the runner check these, in this order. Each failure names the rule and the stage.

1. `version` is `1`; required keys are present; no unknown keys; ids and input names are kebab-case
   and unique; no input uses a reserved name.
2. Every file named — `schema`, `script`, `.claude/workflows/<name>.js`, a project skill's
   `SKILL.md` — exists.
3. Every `reads` entry with `from` names an **earlier** stage that has a matching `writes` entry, and
   that entry has a `schema`. Every `repo_file` entry has an `owner`.
4. `unsafe_to_rerun` and `world_check` come together.
5. `on_fail: retry` carries `retry`; `on_fail: stop` does not. A stage with `fan_out` or `approval`
   uses `stop`: a retry must not fire an irreversible step or re-run a fan-out twice.
6. `fan_out` is on an `agent` stage, `items_from` is in that stage's `reads`, and `output` sits inside
   a directory `writes` entry.
7. `fallback: agent` or `inline` has `instructions`. A `workflow` stage has at most one `writes`
   entry.
8. A stage with `approval.headless` of `stop` or `preapproved-only` needs top-level
   `resumable: true`, or stopping would end a run that cannot be resumed. `covers` names only the
   stages that immediately follow.
9. No stage runs the runner: a `skill` stage does not name `run-agentic-workflow`, and no project
   skill it names invokes it. Nesting is capped at one level.
10. No value is a literal secret.

## `run-state.md`

Written to `{run}/run-state.md` when `resumable: true`, updated after every stage change:

```markdown
# Run state: prepublish/20261003-0930

flow: prepublish
config: .claude/skills/prepublish-flow/flow.yaml
mode: headless
inputs: repo=.

## Stages

- audit: done | findings.md | fallback: agent (Workflow tool absent)
- fix: done | fixes/ | 12 items
- verify: failed | - | attempt 3 of 3: 2 tests red
- publish: awaiting-approval | - | {run}/approval-publish.md

## Approvals

- publish: approved | approve=publish | 2026-10-03T10:05

FLOW STATUS: awaiting-approval publish
```

Each stage line is `<id>: <state> | <artifact paths or -> | <note>`, with `<state>` one of
`pending`, `done`, `awaiting-approval`, `failed`. The note carries the gate evidence in one line.
The approvals section records the decision, its source (`interactive`, `approve=<id>`, or
`resume-prompt`) and the time. When a stage reaches `awaiting-approval`, the runner also writes what
`show` asks for to `{run}/approval-<stage-id>.md`, so the person approving sees the same thing the
run would have asked about.

## The `FLOW STATUS` line

The run's last line, in the reply and in `run-state.md`. A headless caller branches on it.

```
FLOW STATUS: done
FLOW STATUS: awaiting-approval <stage-id>
FLOW STATUS: failed <stage-id> <reason>
```

A failure before any stage runs (config, preflight, inputs) uses `-` for the stage id:
`FLOW STATUS: failed - config invalid: rule 3, stage verify`.

## Complete example

```yaml
version: 1
name: prepublish
description: Audit, fix, verify and publish a release candidate.
resumable: true
inputs:
  - name: repo
    required: true
    description: Path of the repo to release.
stages:
  - id: audit
    run:
      kind: workflow
      workflow: prepublish-audit # .claude/workflows/prepublish-audit.js
      args: { paths: "src/" }
      fallback: agent
      instructions: "Audit {input.repo}/src for release blockers and list each as a finding."
    writes:
      - artifact: findings.md
        schema: references/findings-schema.md
    tools: ["Workflow(prepublish-audit)"]
    gate:
      check: "{run}/findings.md exists and has every required field in findings-schema.md"
      on_fail: stop

  - id: fix
    run:
      kind: agent
      subagent_type: general-purpose
      instructions: "Fix the one finding you were given, commit it tagged fix-{run_id}, and describe it."
    reads:
      - artifact: findings.md
        from: audit
    fan_out:
      items_from: findings.md
      max_parallel: 4
      max_items: 20
      output: "{run}/fixes/{item}.md"
    writes:
      - artifact: fixes/
        schema: references/fix-schema.md
    unsafe_to_rerun: true
    world_check: "git log shows no commit tagged fix-{run_id}"
    gate:
      check: "one file per finding under {run}/fixes/, each with every required field in fix-schema.md"
      on_fail: stop

  - id: verify
    run:
      kind: agent
      instructions: "Run the test suite and fix only the tests the fixes in {run}/fixes/ broke."
    reads:
      - artifact: fixes/
        from: fix
    tools: ["Bash(uv run pytest:*)"]
    gate:
      check: "uv run pytest exits 0"
      on_fail: retry
      retry:
        {
          max: 2,
          changes: "re-read the failing test output and fix only those tests",
        }

  - id: publish
    approval:
      kind: confirm
      show: "the version, the changelog entry and the target registry"
      headless: stop
    run:
      kind: script
      script: scripts/publish.sh
      args: ["{input.repo}"]
    tools: ["Bash(bash *prepublish-flow/scripts/publish.sh:*)"]
    gate:
      check: "the registry lists the new version"
      on_fail: stop
```

## Not in version 1

Conditional stages, loops across stages, parallel stages other than a `fan_out`, per-stage `mode`
overrides, and a stage that is itself a flow. Each would make the order something the runner decides
rather than reads off the file.
