# Plugin eval report schema

The report `evaluate-plugin` saves to
`.agents_workspace/product/eval/plugin/<plugin>/<YYYYMMDD-HHMMSS>-<session-id>-eval.md`, written
once per evaluation for someone who has never seen the plugin. Its layout is
`../assets/plugin-eval-report.template.md`, relative to this file. The time comes from one
`date +%Y%m%d-%H%M%S` call and the session id is the whole id of the session that ran the
evaluation.

## Frontmatter

- `plugin`: the plugin's name.
- `date`: the day of the evaluation.
- `criteria`: `confirmed` when the user confirmed the good and bad result per component,
  `unconfirmed` when no user was present and the drafted criteria were used.
- `ceiling_usd`: the approved spending ceiling, or the drafted one when no user was present.
- `spend_usd`: the total of every paid run of the session: the probe, the grader trap cases, each
  suite invocation, every re-run and every hill-climb round. `0` when no paid run started.

## Summary

Two sentences under the title: what the plugin does, and what the evaluated components do.

## Results

One `###` heading and one table per evaluated component, one row per scored group that has cases.

- **Group:** `must act`, `must stay quiet` or `outcome`. The first two are scored apart, so a
  component that fires on everything cannot score well.
- **Cases** and **Runs:** how many cases the group holds and how many runs each case got.
- **Pass with** and **Pass without:** passing runs out of all runs, with and without the plugin.
  Leave out runs with a non-null `error` that scored without graders, and say how many below the
  table.
- **Δ:** the pass rate with the plugin minus the pass rate without it.
- **Noise floor:** `1/sqrt(cases × runs)` for the group. Write `directional` after a floor above
  0.2.
- **Cost:** what the group's runs cost, judge calls included.

A single-arm run has no baseline: a `trigger` case run with `--ablation none`, and every
hill-climb round. Write `n/a` in **Pass without** and **Δ** for its row. When no paid run started,
list the drafted cases with `not run` in both pass columns, and give the exact probe and suite
commands below the tables.

## Failures

One bullet per failing case: the cause, by its name in the table of the skill's "Fix one gap per
round" step (description, body, prose cannot hold it, judge, grader, setup), then the grader's
explanation, quoted. `None.` when every case passes.

## Fixes

One row per fix tried: what changed, the pass rate of the affected cases before and after, and
whether it was kept or reverted. `None.` in place of the table when no fix was tried.

## Unproven

What stays unproven, each as one bullet: a component whose claim could not be turned into a check,
a group whose floor is above 0.2, a case not run. The last bullet names the next fix to try.
