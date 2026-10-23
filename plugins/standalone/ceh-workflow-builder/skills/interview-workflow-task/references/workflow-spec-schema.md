# Workflow spec schema

The spec `interview-workflow-task` writes to `$CEH_WORKFLOW_BUILD_DIR/<name>-workflow-spec.md`,
defaulting to `.agents_workspace/workflow/`, and `build-agentic-workflow` builds from. A new spec is a copy of
`../assets/workflow-spec.template.md`, relative to this file. The `schema: workflow-spec/v1` line
stays as written.

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
