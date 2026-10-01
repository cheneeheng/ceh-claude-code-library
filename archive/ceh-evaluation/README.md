# ceh-evaluation

Claude Code plugin for evaluating a **skill or plugin you just wrote** before you ship it. It reads
the target, derives that target's own success criteria, then runs an evidence-based battery and
loops fix → re-run until a 6-point readiness gate passes.

A skill that "looks fine" on read often under-triggers, restates what the model already knows, or
makes no measurable difference to outcomes. You only find out by running it. This plugin is that
measurement, made disciplined — the verdict is backed by trigger counts, cited lines, and
with-skill-vs-baseline deltas, never by assertion.

## How it works

The skill is a loop, not a one-shot grader:

```
Intake   → locate & read the target; detect optional cross-check tools
Derive   → extract the claim, trigger intent, and intended outcome; build the test batteries
Run      → measure 4 dimensions: structure, triggering, content, behavioral lift vs a no-skill baseline
Report   → aggregate evidence into SKILL_EVAL.md; score the 6-point gate; name the highest-leverage gap
Revise   → fix that gap, re-run only the affected dimension, re-score
         ↺ repeat run/revise until gate = 6/6 AND you confirm
Validate → flip status to passed; hand off the advisory backlog
```

The deliverable is a living `SKILL_EVAL.md` in the current run's folder under `.agents_workspace`
(`.agents_workspace/skill-evals/<target-name>/run-<NNN>/SKILL_EVAL.md`; schema in
`skills/evaluate-skill/references/eval-report-schema.md`). **The report holds findings, never
inputs**: trigger batteries, competing descriptions and task fixtures go in that run folder's
`fixtures/`, raw run outputs in its `iteration-<N>/`, both referenced from the report by path. Each
fresh evaluation gets a new `run-NNN` folder, so re-running never overwrites a prior run's report or
evidence.

The report is written for **someone who has never heard of the target** — it says what the target
does before reporting anything about it, heads each section with the question it answers, and states
what every number is out of. An evaluation nobody reads has measured nothing.

**Default gate thresholds** (defaults, not laws — a niche skill sets its own battery size, and the
threshold actually used is recorded in the report so the score is reproducible): a skill **triggers
on intent** when it fires on ≥ 8 of 10 positive prompts (a prompt counts as firing if it triggers in
≥ 2 of 3 runs), and **does not over-trigger** when it fires on ≤ 1 of 10 near-miss negatives.

There is no universal metric for "a good skill" — what success means depends on what the target
claims to do. So the criteria are **derived per target**; only the process and report are fixed.
The gate count (`eval_gate: N/6`) is the only summary number — there is deliberately **no fabricated
composite score**.

## Relationship to the Anthropic skill-creator and plugin-dev plugins

> **`skill-creator` and `plugin-dev:*` are Anthropic-provided plugins from a separate (official)
> marketplace — not part of this repo and not dependencies of this plugin.** This plugin is
> self-contained: every dimension runs with built-in tools and generic subagents alone. Where those
> Anthropic plugins (or a repo's own `validate.py`) are installed, this plugin uses them only as
> **optional cross-checks** — confirmation, not authority. When a cross-check disagrees with a
> finding, the disagreement is investigated rather than deferred to. The authoring principles in
> `references/eval-rubric.md` are distilled _from_ those plugins as reference material, restated here
> so this plugin needs none of them to run.

## Skills

| Skill                 | Description                                                                                                                                                                                                                                                                                                                                               |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `evaluate-skill`      | Derive a skill/plugin's own criteria, measure structure/triggering/content/behavioral lift with evidence, and loop fix→re-run until a 6-point readiness gate passes                                                                                                                                                                                       |
| `evaluate-skill-lite` | Fast dev-loop variant — runs only the three cheap dimensions (structure, single-pass triggering, content) and skips behavioral lift; reports a partial gate (max 4/6, criteria 5–6 unproven) for cheap iteration while you are still writing. Shares `evaluate-skill`'s rubric and report schema. Hand off to `evaluate-skill` for the full ship verdict. |

Invoke manually:

```
/ceh-evaluation:evaluate-skill        # full ship verdict (includes behavioral lift)
/ceh-evaluation:evaluate-skill-lite   # fast dev-loop check (skips behavioral lift)
```

## Roadmap

The plugin name is deliberately broader than its current single skill: planned additions are an
evaluator **agent** (autonomous deep evaluation of a target) and a post-write **hook** (auto-flag a
changed `SKILL.md` for evaluation).
