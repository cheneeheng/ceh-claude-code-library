# Archive

Retired plugins and plugin contents (skills, agents, hooks, scripts) kept for reference.

Nothing here is published: `archive/` sits outside `plugins/`, so it is not listed in
`.claude-plugin/marketplace.json` and `tools/validate-plugins/validate.py` does not scan it.
Move content back under `plugins/` to revive it, and re-register it per `CLAUDE.md`.

## Scenario bundles (retired 2026-10-10)

`ceh-scenario-service`, `-library`, `-webapp`, `-ideation`, and `-editorial` were manifests that
installed other plugins as dependencies. They were retired because they did not fit the lifecycle
in `docs/STRATEGY.md`. Three were cut by stack and two by stage. A stack bundle installed all of
Build and Prove at once, up to 13 plugins, and refused to let any of them be disabled.
`docs/GETTING_STARTED.md` replaces them: a small core, then one plugin per stage. Their READMEs'
links to `docs/` were written for their old place under `plugins/scenarios/`.

## `ceh-git-workflow:branch` (retired 2026-10-18)

Its naming table and rules restated industry-standard trunk-based branching, which the agent
followed without it: 57 of 61 branch creations in one project skipped the skill, and the one
session reviewed still named its branch by the convention. The prefix list stays in `branch-guard.py`'s deny message, rebasing stays in
`pull-request`, and the worktree guidance moved to `ceh-coding-conduct:agent-coding-contract`'s
Task decomposition.

## `ceh-orchestration-lab` (archived 2026-11-12)

The experiment ended on 2026-11-11, with the plugin audit of that day. The plugin ran real coding
tasks under two orchestration strategies and logged each run, so the strategy that worked could
become guidance. Its lessons were dropped by decision and moved into no other skill. The run
folders stay in each project's `.agents_workspace/orchestration-lab/`.

## `ceh-git-datastore` (archived 2026-11-12)

Archived unused on 2026-11-11, by the plugin audit of that day, not rejected: nothing in it was
found wrong. The folder is whole, so moving it back under `plugins/standalone/` and re-registering
it per `CLAUDE.md` re-enables it.

## Plugin eval cases (archived 2026-11-23)

`ceh-build-plan/evals/` and `ceh-product-direction/evals/` held the `claude plugin eval` cases
written up to 2026-11-22, before the repo-local `evaluate-plugin` skill let the user size the
cases and say what a good result is. They were archived so the next evals start anew under that
flow, not rejected. Their local `results/` folders moved with them and stay git-ignored. Run an
archived case from here with `claude plugin eval --eval-dir`, or move it back under its plugin.

## `ceh-ui-design` eval suites (archived 2026-11-23)

`ceh-ui-design/evals/` and `ceh-ui-design/evals-interactive/` are two `claude plugin eval` suites
for `design-ui`, written two ways to compare the approaches. `evals/` has seven cases on one
seeded page, with one claim per grader and three runs per arm, and it found the two gaps fixed in
`ceh-ui-design` 1.0.13. `evals-interactive/` has eight cases that cover more of the skill, each
graded by one LLM judge over six to eight claims, and none of its failures was confirmed as a
plugin gap. They were archived once the comparison was done, as the reference for the next cases:
the shape of `evals/`, with the scenarios of `evals-interactive/`. Their local `results/` folders
moved with them and stay git-ignored.
