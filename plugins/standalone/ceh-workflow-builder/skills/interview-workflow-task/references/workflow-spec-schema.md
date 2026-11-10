# Workflow spec schema

The spec `interview-workflow-task` writes to `$CEH_WORKFLOW_BUILD_DIR/<name>-workflow-spec.md`,
defaulting to `.agents_workspace/workflow/`, and `build-agentic-workflow` builds from. A new spec is a copy of
`../assets/workflow-spec.template.md`, relative to this file. The `schema: workflow-spec/v1` line
stays as written. A new spec is `v2` (below), whose Markdown is rendered in this `v1` layout.

## Frontmatter

- `name`: the workflow's name, derived from the moment. A provisional slug until the name is
  settled, then the file is renamed to match.
- `date`: the date the spec was started.

## Sections

Nine fixed headings, in this order, one per interview question. The builder gates on them by name,
so all nine stay as written. Anything no heading covers belongs in the reply, not a tenth section.

1. **Moment:** the trigger, a verb, not a topic.
2. **Manual procedure:** the steps, numbered, in the order they are done.
3. **Preconditions and proof:** per step, what must be true before it starts and how its success
   is checked: by a command, a file check, or a declared human go/no-go gate.
4. **Data flow:** per step, what it reads, naming the step that produces it, and what it leaves
   behind. Then what a run starts from: an argument, or what the previous run left.
5. **Tooling:** per step, the CLIs, credentials, services, or network access it needs. A credential
   is recorded by where it lives (a secret-manager key, an env var name), never its value.
6. **Done:** what is true at the end that was not true at the start.
7. **Interruption:** one sitting, or stop and resume partway.
8. **Unsafe to re-run:** the steps that would do damage if they ran a second time. The builder reads
   it as a run-once guard.
9. **Irreversible steps:** the steps that touch something outside this machine that cannot be
   taken back.

## Rules

- Under 2, 3, and 4, the same step keeps the same number in all three sections, because the builder
  reads them as one table.
- An unanswered question keeps its heading and says so underneath. A question the user declined
  holds `Declined` and their words.

## workflow-spec/v2: YAML with generated Markdown

A `workflow-spec/v2` spec is `$CEH_WORKFLOW_BUILD_DIR/<name>-workflow-spec.yaml`, a copy of
`../assets/workflow-spec.template.yaml`, and the `.md` of the same stem is generated from it in the
`v1` layout above, beside it. The YAML is the source: agents read and edit it, and nobody edits the
Markdown, which opens with `generated_from: <file>.yaml` and a do-not-edit `generated_note`. A `v1`
`.md` with no `.yaml` beside it is still read as `v1`, and converted before anything writes to it.
The format in code is `workflow-spec-model.py` beside this file, and `scripts/artifact.py` in the
skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. A rule across rows, such as the step numbers,
reports `(top level)` and names the row in its message.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `workflow-spec/v2`. `name`: the workflow's slug, `^[a-z0-9]+(-[a-z0-9]+)*$`. `date`:
  the date the spec was started, `YYYY-MM-DD`.
- Nine rows, one per question, rendered under the `v1` headings: `moment` (1), `procedure` (2),
  `proof` (3), `data_flow` (4), `tooling` (5), `done` (6), `interruption` (7), `rerun_unsafe` (8),
  `irreversible` (9).

**Row states.** Every row holds `state` and only the keys of that state. The template shows each
row `answered`, the shape the interview fills.

- `unanswered`: `question`, one line: what still has to be asked. Rendered `Unanswered: <question>`.
- `declined`: `words`, the user's words. On `rerun_unsafe` and `irreversible` only, an optional
  `assumption`, written by `build-agentic-workflow` per its Declined table. Rendered
  `Declined: <words>`, then `Assumed: <assumption>`.
- `answered`, with the row's content:
  - `moment`: `answer`, one line.
  - `procedure`: `steps`, at least one, each `n` and `step`, numbered 1, 2, 3 in order.
  - `proof`: `steps`, each `n`, `before` (the precondition), `by` (`command`, `file` or `human`)
    and `check`: the command, the file check, or for `human` who is shown what and that a no-go
    stops the run.
  - `data_flow`: `starts_from` (an argument, or what the previous run left), and `steps`, each
    `n`, `reads` (`[]` when none, each `artifact` and `from`: an earlier step's `n`, or
    `run start`) and `leaves` (`[]` when none).
  - `tooling`: `steps`, each `n` and `needs` (`[]` when none). A credential is named by where it
    lives.
  - `done`: `answer`, a list of at least one line.
  - `interruption`: `answer`, `one sitting` or `resumable`.
  - `rerun_unsafe`: `steps`, `[]` when the user said none, each `n` and `why`, and an optional
    `note` for an ordering hazard cross-referenced to `proof`.
  - `irreversible`: `steps`, `[]` when the user said none, each `n` and `effect`.

**Across rows.** `proof`, `data_flow`, `tooling`, `rerun_unsafe` and `irreversible` may be
`answered` only when `procedure` is. Then `proof` and `data_flow` hold exactly its step numbers in
order, and every other `n` names one of its steps. A `from` names a step before the reading one: a
later step's output can only come from the previous run, which is `run start`. So adding or
removing a step changes `procedure`, `proof` and `data_flow` in one Write or MultiEdit, never one
row at a time, or the check rejects the file in between.

**Quoting:** single-quote any value that starts with `*`, contains `: ` or ` #`, or holds a
backslash, such as `'git tag --list v* prints the tag'` or `'C:\tools\deploy.ps1'`. Inside a
`{...}` flow mapping, also quote a value holding `,`, `?`, `[`, `]`, `{` or `}`, or YAML splits it
or fails to parse it. Every
value is strict, so quote a value such as `1.10` that must stay text.
