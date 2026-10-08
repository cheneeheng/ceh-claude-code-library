# ceh-plan-build-review

The plan-driven development loop as one plugin: **plan** a fullstack app (one release at a time, or
all the way to MVP in a single session), **build** it by implementing the plan section by section,
and **review** the implementation against the plan.

All four skills share the same plan document schema (`SKELETON.md` / `ITER_NN.md`, including
version-tagged families like `SKELETON_v2.md`), so artifacts produced by the planning skill are
directly consumable by the implement, review, and patch skills. Plan artifacts are written to
`.agents_workspace/planning/`.

## Skills

| Skill                        | Invoke                                              | Triggers when                                                                                                                                                                                                    |
| ---------------------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plan-fullstack-app`         | `/ceh-plan-build-review:plan-fullstack-app`         | Planning a project: next-release mode writes one scoped `SKELETON.md` or `ITER_NN.md`, whole-build mode writes the skeleton plus every iteration to MVP behind a complexity gate that falls back to next-release |
| `implement-from-plan`        | `/ceh-plan-build-review:implement-from-plan`        | Pointing at a plan and asking to build it: implements a `SKELETON.md` / `ITER_NN.md` section by section (§01–§06), resolving iteration pointers to the authoritative spec                                        |
| `review-against-plan`        | `/ceh-plan-build-review:review-against-plan`        | Auditing the code against a plan: checks each in-scope section against the spec, finds gaps, deviations, and errors, then fixes them                                                                             |
| `apply-small-fix-to-version` | `/ceh-plan-build-review:apply-small-fix-to-version` | Making a small, non-feature change to a version that is already built: routes features out to the iterative planner, otherwise records a `patch: true` `ITER_NN.md` and implements only the touched sections     |

## The loop

```text
plan-fullstack-app ──► SKELETON.md / ITER_NN.md ──► implement-from-plan ──► review-against-plan
                                  │
                                  └── small non-feature change after a version ships ──► apply-small-fix-to-version
                                      (feature? → back to plan-fullstack-app)
```

`apply-small-fix-to-version` does not bump versions or tag. It hands the SemVer PATCH bump to
`ceh-git-workflow:release`, which is a prose handoff, not a dependency.

## Plan mode is for the research before these skills, not for running them

Claude Code's built-in plan mode (`Shift+Tab`, or `/plan` on a single prompt) allows reads and
classifier-approved commands only: **file writes are blocked until you approve a plan**. Every
skill here except the audit half of `review-against-plan` produces or edits a file: a
`SKELETON.md`, an `ITER_NN.md`, or the implementation itself. Running them inside plan mode blocks
the deliverable.

Use plan mode for the step _before_: exploring an unfamiliar codebase to decide what to plan. Then
leave plan mode and invoke the planning skill, which needs write access to emit its artifact.

Do not set `"defaultMode": "plan"` in a repo where these skills are the main workflow.

## Shared reference files

Four files live once in `references/` at the plugin root and are read through
`${CLAUDE_PLUGIN_ROOT}`:

- `plan-schema.md`, the plan document schema (file naming, version families, frontmatter, pointers,
  resolution order, and how to locate plan files), read by all four skills.
- `section-specs.md`, the expected contents of §01–§06 at skeleton and iteration level, read by
  `plan-fullstack-app`.
- `audit-checklist.md`, the pre-delivery audit checklist, read by `plan-fullstack-app`.
- `implementation-gotchas.md`, the technical traps in §04, §05, and §06, read by
  `plan-fullstack-app` (to address them in the plan), by `implement-from-plan` and
  `apply-small-fix-to-version` (to avoid them in code), and by `review-against-plan` (a trap present in
  §04 or §05 code is an Error).
