# ceh-build-plan design notes

Maintainer detail moved out of the plugin README on 2026-11-24, when the README was rewritten for
the person installing the plugin. The site does not publish this file.

## The plan as the handoff

The plan is the handoff between the lifecycle stages. `implement-from-plan` builds it phase by
phase, and `ceh-check-build-against-plan` checks the finished build against it. Each of the two
plugins works installed alone, and each of their skills carries the plan format in its own
`references/plan-schema.md`. A built plan keeps an append-only `## Record`, so the build keeps its
history.

## Skill checks

What each skill's run looks like when it works, from the README's old Skills table:

- `write-technical-design`: the reply lists each entry by topic and the rendered `ARCHITECTURE.md`
  shows `**Planned:** not built yet.` under each new diagram. Each entry holds the contract as
  Markdown (lists, tables, code) with small parts of at most 30 lines. A later change edits the
  entry in place and adds one Key Decisions entry.
- `write-build-plan`: it announces the triage label (spike, bounded, or architectural) first and
  saves `.agents_workspace/product/plan/<YYYYMMDD-HHMMSS>-<slug>.yaml` with its rendered `.md`, one
  plan per functionality, then hands the plans it saved in the session to `review-build-plan` in
  one batch.
- `review-build-plan`: it adds a round to the plan's one review file,
  `.agents_workspace/product/review/plan/<YYYYMMDD-HHMMSS>-<plan-slug>.yaml`, with its rendered
  `.md`, ticking off findings the plan now fixes, and the reply gives the verdict, the blocking
  findings, the findings still open, and that path.
- `implement-from-plan`: each finished phase's Status in the plan reads `done` with a commit or
  check output.

## Hooks

The artifact check and the generated-file guard act on `plan/v2` plans, the YAML format in each
skill's `references/plan-schema.md`, which the skills write, and on the `ARCHITECTURE.yaml`,
`VISION.yaml`, `STRATEGY.yaml` and `PRD.yaml` the skills write or check before reading, because
the skills carry those models too.

| Hook                 | Event                                        | Script                    |
| -------------------- | -------------------------------------------- | ------------------------- |
| Build record guard   | `PreToolUse` (`Edit`, `Write`, `MultiEdit`)  | `build-record-guard.py`   |
| Artifact check       | `PostToolUse` (`Edit`, `Write`, `MultiEdit`) | `artifact-render-hook.py` |
| Generated-file guard | `PreToolUse` (`Edit`, `Write`, `MultiEdit`)  | `generated-md-guard.py`   |

The artifact check runs `scripts/artifact.py render` on each write to a
`.agents_workspace/product/plan/*.yaml`, or to any YAML whose `schema:` names a model in this
plugin. Errors go back to the agent to fix, and the Markdown beside the YAML is rendered only once
the YAML is valid. It needs [uv](https://docs.astral.sh/uv/), which installs pydantic and PyYAML on
first use. The guard denies a hand edit to a Markdown file whose frontmatter says
`generated_from:`, and names the YAML to edit instead. `implement-from-plan` also runs
`artifact.py check` before it acts on a `plan/v2` plan.

The build record guard denies an edit that adds a `- YYYY-MM-DD Built Phase` line to a plan in
`.agents_workspace/product/plan/`, unless `implement-from-plan` was started in the session, by the
Skill tool or its slash command. A Built Phase line is the plan's evidence that a phase was built
test first and proven by its own check, so a line written by hand records a build that procedure
never ran. It happened once: a session hand-wrote three Built lines, recorded in the
repeat-mistake report of 2026-10-26 in this library's repo. Built lines already in the file do not
count, so rewriting a plan that has them passes. The guard fails open: unparseable input or a
missing transcript allows the edit. In a `plan/v2` YAML plan, it guards a new
`event: Built Phase` record entry the same way.

## History

Since 2026-11-14 this plugin saves and reads product files in `.agents_workspace/product/`.
