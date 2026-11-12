# Run state schema

The run's state, updated after every stage change. The runner writes it as `run-state/v2`
(below), `{run}/run-state.yaml` with `{run}/run-state.md` rendered beside it, when a flow is
`resumable: true`, per `flow-config-schema.md` beside this file. The `v1` layout here is that
rendered Markdown, and the file a single emitted skill keeps for itself: a copy of
`../assets/run-state.template.md`, relative to this file, its `schema: run-state/v1` line kept as
written. This file is copied word for word into `ceh-workflow-builder` and `ceh-workflow-runner`.

## Header

- **Title:** `Run state: <flow>/<run id>`.
- `flow`: the flow's name.
- `config`: the path to its `flow.yaml`.
- `mode`: `interactive` or `headless`.
- `inputs`: the run's inputs, as `name=value` pairs separated by commas.

## Sections

- **Stages:** one line per stage, `<id>: <state> | <artifact paths or -> | <note>`. `<state>` is
  `pending`, `done`, `awaiting-approval`, or `failed`. The note carries the gate evidence in one
  line.
- **Approvals:** one line per decision, `<id>: <approved | rejected> | <source> | <time>`. The
  source is `interactive`, `approve=<id>`, or `resume-prompt`, and the time is ISO-8601.
- **`FLOW STATUS` line:** the file's last line, the same as the run's reply, per
  `flow-config-schema.md`.

## Worked example

```markdown
---
schema: run-state/v1
---

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

## run-state/v2: YAML with generated Markdown

A `run-state/v2` run state is `{run}/run-state.yaml`, a copy of `../assets/run-state.template.yaml`,
and `{run}/run-state.md` is generated from it in the `v1` layout above, beside it. The YAML is the
source: only the runner writes it, and nobody edits the Markdown, which opens with
`generated_from: run-state.yaml` and a do-not-edit `generated_note`. A `v1` `run-state.md` with no
`.yaml` beside it is still read as `v1`, and converted at the first write. The format in code is
`run-state-model.py` beside this file, and `scripts/artifact.py` in the skill checks and renders
it through uv:

```bash
uv run --script scripts/artifact.py check <run>/run-state.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <run>/run-state.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. A rule across keys reports `(top level)` and
names the key in its message.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `run-state/v2`. `flow`: the flow's name, a kebab-case slug. `run_id`: the start time and
  the id of the session that started the run, `<YYYYMMDD-HHMMSS>-<session-id>`, quoted. A run
  started under the older form keeps its id, `<YYYYMMDD-HHMM>` with a `-2`, `-3` suffix. `config`: the path to its
  `flow.yaml`. `mode`: `interactive` or `headless`.
- `inputs`: `[]` when none, each `name` and `value`, rendered `name=value` joined by `, `, or `-`
  when empty.
- `stages`: at least one, each `id` (kebab-case), `state` (`pending`, `done`, `awaiting-approval`
  or `failed`), `artifacts` (paths, `[]` when none, rendered joined by `, ` or `-`) and `note`
  (optional, the gate evidence or the fallback chosen, rendered `-` when absent).
- `approvals`: `[]` when none, rendered `- none`, each `stage`, `decision` (`approved` or
  `rejected`), `source` (`interactive`, `resume-prompt` or `approve=<stage-id>`) and `at`
  (ISO-8601 `YYYY-MM-DDTHH:MM`, with optional seconds and offset, quoted).
- `status` (optional): the text after `FLOW STATUS: `, `done`, `awaiting-approval <stage-id>` or
  `failed <stage-id or -> <reason>`, rendered as the file's last line. Absent while the run is in
  progress.

**Across keys.** Stage ids are unique, and at most one stage is `awaiting-approval`. Every
approval's `stage` names a stage, and an `approve=<id>` source names that same stage. `done` needs
every stage `done`, `awaiting-approval <id>` needs stage `<id>` to be `awaiting-approval`, and
`failed <id> ...` needs `<id>` to name a stage, while `failed - ...` constrains no stage. Every
value is one line. So a stage's `state` and the `status` change in one Write or Edit, never one at
a time, or the check rejects the file in between.

**Quoting:** single-quote any value that starts with `*`, `{` or `[`, contains `: ` or ` #`, or
holds a backslash, such as `'attempt 3 of 3: 2 tests red'` or `'{run}/approval-publish.md'`. Inside
a `{...}` flow mapping, also quote a value holding `,`, `?`, `[`, `]`, `{` or `}`, or YAML splits it
or fails to parse it. Quote every input `value`, so `10`, `true` or `no` stays text under the
strict model, and quote `run_id` and `at`.
