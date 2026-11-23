---
name: evaluate-plugin
description: >-
  Load this skill when checking whether a plugin's skills, hooks, agents, or MCP servers work: write
  claude plugin eval cases, run the smallest paid check first, fix one gap per round. Trigger on
  "evaluate this plugin", "does this skill trigger", "hill-climb this skill".
argument-hint: "[plugin-dir] [component-name]"
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Needs Claude Code v2.1.269+ and git 2.31+ for `claude plugin eval`, and Python 3.9+ for the
  hill-climb converter, which fails at import on an older Python. Hill-climb reports need node or
  bun, or fall back to a Markdown table.
license: Apache-2.0
---

# Evaluate plugin

Measure whether a plugin's components do what they claim, using `claude plugin eval` as the only
runner, then fix the biggest gap and measure again. Done when a report is saved and every case
passes, or each remaining failure is named with its cause. With no user present, done when the
report is saved with the free checks' results, the drafted cases and the drafted ceiling, and no
paid run started.

## What waits for a request

The free checks of steps 2 and 6 run unasked. Every `claude plugin eval` run is a billed model
call. Get one yes for the cases and a spending ceiling before the first paid run, and a new yes
before spending past that ceiling. The ceiling covers every paid run of the session together: the
probe, the grader trap cases, each suite invocation, every re-run and every hill-climb round. Keep
a running total from each run's reported cost, and pass `--max-cost-usd` as what is left of the
ceiling, never the whole ceiling again.

## Procedure

1. **Read the target.** Take the plugin directory and component from `$ARGUMENTS`, or ask. Read
   each component in full and any existing `<plugin>/evals/`. For each component write down its
   claim, when it must act and when it must stay quiet, and what a session gets from it that a
   session without it does not.
2. **Run the free checks.** `python tools/validate-plugins/validate.py` and
   `claude plugin validate <plugin>`. For each hook command, pipe a sample event JSON on stdin and
   check its exit code and output: a hook's logic needs no model to test.
3. **Write the cases** under `<plugin>/evals/<case>/` (`prompt.md` plus `graders/*.md`), by hand
   or from `claude plugin eval init --bare <case>` (Rules says why not plain `init`). Source
   prompts in this order and say which you used:
   1. Real prompts from the user's transcripts, `<home>/.claude/projects/<project>/*.jsonl`, that
      should have used the component. Replace home paths with `<home>` and `<project>`.
   2. Examples the user gives.
   3. Prompts you write from the component's text, seeded from 1 or 2. Label them synthetic.

   Draft the proposed set, short prompts phrased as users type. Per skill: one task at the three
   strictness levels (step 4), two near-misses, and one outcome case per result the skill
   promises. Per hook, agent or MCP server: one must-act and one must-stay-quiet case. Step 5 lets
   the user shrink or grow it. Give each case a tag: `trigger` for cases about firing, `outcome`
   for cases about the result. Write each `llm` rubric and file pattern from a drafted answer to
   what a good result must contain or do and what would make it bad, which step 5 puts to the
   user.

4. **Shape graders by component.** Prefer free graders (`regex`, `tool_used`, `tool_order`,
   `file_exists`) and grade what the run left behind over what Claude said:

   | Component  | Must act                                                                         | Must stay quiet                                        |
   | ---------- | -------------------------------------------------------------------------------- | ------------------------------------------------------ |
   | Skill      | `tool_used: Skill`, `input_match` on the skill name; outcome graders on the work | Near-miss prompts, same grader with `min: 0`, `max: 0` |
   | Hook       | The blocked call never ran (`tool_used`, `max: 0`), deny text in `trace`         | An allowed call still runs                             |
   | Agent      | `Agent` in `allowed_tools`, `tool_used: Agent` matching `<plugin>:<agent>`       | Prompts the main session should handle alone           |
   | MCP server | Mocks in `evals/mocks/<server>/<tool>.md`, `regex` with `target: mock_calls`     | No mock call on prompts that need no server            |

   The doc's rules for a stable signal:

   - Grade long output, such as a generated file, with `regex` over the file. Keep `llm` for
     short output, with a rubric of concrete PASS and FAIL lines.
   - Give each `outcome` case one grader on the result and one on the steps (`tool_used`,
     `tool_order`).
   - For a build or test, have the prompt ask Claude to run it and write the outcome to a file.
     Grade that file, and add a `tool_used` grader whose `input_match` names the command.

   For a skill, write each positive at three strictness levels over the same task: supportive
   (names the moment), neutral (the task only), competing (the task plus a pull away from the
   rule, tempting and never ordering). Near-misses share keywords with the skill but need
   something else. Score must-act and must-stay-quiet cases apart, so a component that fires on
   everything cannot score well.

5. **Get the plan approved, in one round.** The user decides whether the component is good, so
   they set what good means and how much proof to pay for. Ask once, over the drafted cases:
   - The case list (prompt, tag, graders) and the prompt source.
   - Per component, the drafted good result and bad result, as recommended answers to confirm or
     change.
   - Three sizes, each keeping all three strictness levels: the drafted set; a smaller set (one
     task at three levels and one near-miss per skill, no outcome case); a hard set (two tasks at
     three levels per skill, competing plugins loaded, outcome fixtures with planted traps). Show
     each with cases × runs per case × arms, the noise floor `1/sqrt(cases × runs)` per scored
     group (must act, must stay quiet, outcome), and the cost. Runs per case (`--runs`, default 3) is a second lever, cheapest on single-arm `trigger` cases. Label a size whose floor in any
     group is above 0.2 directional, here and in the report.
   - A spending ceiling. Take the cost per run from the newest
     `<plugin>/evals/results/*/aggregate-result.json` (`costUsd` over its run count, `outcome`
     and `trigger` cases apart), else a saved report for the same plugin, else mark the figure a
     guess for the probe to correct. Add judge calls: three per `llm` grader per run. Add the
     three trap runs per `llm` grader of step 6.

   Apply the answers to the case files. No paid run starts before the yes. With no user present,
   take the drafted criteria, mark them unconfirmed in the report, run only the free checks
   (step 2 and the regex check in step 6), start no paid run, and give the drafted ceiling with
   the exact probe and suite commands.

6. **Probe first.** Before any paid run, check each `regex` grader whose target is the reply or a
   file against a correct and a wrong sample: it must pass the first and fail the second. Graders
   use JavaScript regex, so run the pattern with `node -e`. Without node, use Python's `re` with
   `m`, `i`, `s` mapped to `re.M`, `re.I`, `re.S`, and note that Python's `$` also matches before
   a final newline. Honor `match`: `not_contains` inverts the result, `count:N` needs exactly N
   matches. Leave `trace`, `files` and `mock_calls` patterns, and `tool_used` and `tool_order`
   graders, to the probe. Then run one case once with
   `claude plugin eval <plugin> --case <one> --runs 1 --ablation none --max-cost-usd 1 --no-publish`
   and recompute the total from its real cost. Past the ceiling → stop and ask. Add `--scaffold`
   when a case sets `context.scaffold_script`: without it the fixture never runs and every
   `source: file` grader fails on a missing path. Before `--allow-tools Bash` on Linux, install
   `bubblewrap` and `socat` (`apt install bubblewrap socat`), or the CLI refuses the run. After
   the probe, for each `llm` grader, add three throwaway cases with the same grader whose prompts
   make Claude reply with nothing, with "I don't know", and with a confident answer to the wrong
   question. Run them once each, with the probe's command and `--case` set to their names: all
   three must fail. Fix a grader that passes any of them, then delete the throwaway cases.
7. **Run the suite** in the background with `--max-cost-usd` set to what is left of the approved
   ceiling, `--no-publish`, and the probe's `--scaffold` and Bash setup. The two invocations
   below share the ceiling, so the second gets what the first left. Run `trigger` cases with
   `--ablation none`: under the default two-arm mode a `tool_used: Skill` grader only marks
   whether the plugin fired and does not count toward the score. Run `outcome` cases with the
   default two-arm mode, so `Δ` shows what the plugin adds. A `context.history_file` case on a
   path target runs single-arm with no `Δ` unless you pass `--ablation with-without`.
8. **Read the result.** Open `<plugin>/evals/results/<timestamp>/aggregate-result.json`. Leave out
   runs with a non-null `error` that scored without graders: those are API failures, not plugin
   failures. The noise floor on a pass rate is about `1/sqrt(cases × runs)`: a difference smaller
   than that is not a result. Read the grader explanations of three failing runs and confirm the
   verdict before trusting it.
9. **Fix one gap per round.** Pick the failure that costs the most cases and name its cause:

   | Failure                                                      | Cause                | Fix                                                                                                    |
   | ------------------------------------------------------------ | -------------------- | ------------------------------------------------------------------------------------------------------ |
   | Fails at neutral, passes at supportive                       | Description          | Rewrite the description: the Description loop below when skill-creator is installed, otherwise by hand |
   | Fails even at supportive                                     | Body                 | Rewrite the section that causes it                                                                     |
   | Fails at all three levels, and the step shows in a tool call | Prose cannot hold it | Propose a hook                                                                                         |
   | Two-arm run: `tool_used: Skill` passes but `Δ` is negative   | Judge                | Re-run with `--judge-model sonnet`, tighten the rubric so formatting cannot decide the verdict         |
   | The output is right but the grader fails it                  | Grader               | Fix the grader, re-run every case it grades                                                            |
   | Errored before producing output                              | Setup                | Fix the case's tools, mocks, or limits                                                                 |

   Before applying a fix, cut every sentence in it that changes nothing Claude does. Re-run only
   the affected cases (`--case`, `--tag`) at the same run count. Keep the fix if the pass rate
   rose past the noise floor without other cases dropping, and revert it otherwise.

10. **Stop at a plateau.** After two or three rounds with no gain past the noise floor, stop
    editing and sort the remaining failures into the causes above. Report them instead of
    rewording again.
11. **Land the change.** A fix to a component follows `add-plugin-component`'s registration and
    version bump. Commit the cases under `<plugin>/evals/`; `evals/results/` stays git-ignored.

### Description loop

When skill-creator is installed, turn the skill's `trigger` cases into its eval set,
`[{"query": "<prompt>", "should_trigger": true|false}]`, saved as
`.agents_workspace/product/eval/skill/<skill>/<YYYYMMDD-HHMMSS>-<session-id>-trigger-set.json`,
the time and session id taken as Output says. Then follow the Description Optimization section of
`skill-creator:skill-creator` with that set. Confirm the new description with the plugin-eval
`trigger` cases afterwards, because those run in fresh sessions with only the plugin loaded.

### Hill-climb mode

Use it when the user asks for a hill-climb, or wants a skill tuned systematically over many rounds.
Load the `claude-api` skill with the argument `hillclimb`, and give its Step 0 this as the eval
command:

```bash
python "${CLAUDE_SKILL_DIR}/scripts/plugin_eval_round.py" --plugin <plugin-dir> \
  --flow .agents_workspace/product/eval/plugin/<plugin>/<YYYYMMDD-HHMMSS>-<session-id>-hillclimb \
  --variant <baseline|vN> --target <skill|hook|agent|mcp> --runs <R> -j 4 \
  --max-cost-usd <usd left> [--timeout-s <seconds>] [-- --allow-tools <tools>]
```

Take the flow folder's time and session id once, when the hill-climb starts, as Output says, and
keep that folder for every round of it, so a second hill-climb never overwrites the first.

The script first deletes what an earlier run of the same variant left, then runs
`claude plugin eval --ablation none --keep-temp --no-publish --trust-plugin --output-dir <flow>/<variant>/raw`.
`--trust-plugin` answers the eval's first-run trust question, so settle the Rules line on which
plugins to evaluate before the first round. The script writes the round as `results.jsonl`,
`traces/` and `errors.jsonl` beside `raw/`, in the layout the hill-climb guide reads, and creates
`summary.json` when it is missing, holding the variant name and `--target` only. It deletes the
temp directories `--keep-temp` left and warns on stderr for each one it could not delete. When
the eval dies before writing its result, the script exits 2 with nothing converted and names the
temp folder where kept directories remain: delete the `claude-eval-*` ones there by hand. A run
it cannot convert becomes a row in `errors.jsonl`. Each row carries the `model` that cost most,
every model as `models`, `usage`, exact `cost_usd` and `judge_cost_usd`, the grade per grader,
and the explanations. Tell the guide three things:

- The artifact under change is the component file, loaded through Claude Code's real discovery,
  so a round tests both whether the model finds it and whether it helps.
- The script has no harness-integrity gate. List the script and every `evals/` grader in
  `harness_paths`, and never edit them during a round.
- Below about 50 cases the guide's rule applies: no train and test split, more runs, and every
  score labelled directional.

## Rules

- Write the cases yourself rather than running `claude plugin eval init`, which the doc
  recommends. `init` opens its own interactive session and trials its graders before any ceiling
  is agreed, and the doc does not say it takes prompts from transcripts or writes three
  strictness levels. `claude plugin eval init --bare <case>` stays fine for a blank template.
- Never run the archived `ceh-evaluation` plugin. It is replaced by this skill and by Anthropic's
  tools.
- Keep run output out of the repo: results go to `<plugin>/evals/results/` (git-ignored) and the
  hill-climb flow to `.agents_workspace/`. Transcripts carry home paths.
- Only evaluate plugins you would run yourself: their hooks and any real MCP server run outside the
  eval's sandbox.

## Output

Save the report to `.agents_workspace/product/eval/plugin/<plugin>/<YYYYMMDD-HHMMSS>-<session-id>-eval.md`,
a copy of `${CLAUDE_SKILL_DIR}/assets/plugin-eval-report.template.md`, written for someone who has
never seen the plugin. Take `<YYYYMMDD-HHMMSS>` from one `date +%Y%m%d-%H%M%S` call and
`<session-id>` from `${CLAUDE_SESSION_ID}`. Every field and section, and what a single-arm run or
a run with no paid check puts in the tables, is in
`${CLAUDE_SKILL_DIR}/references/plugin-eval-report-schema.md`.

Reply with the report path, the tables, total spend, and the open failures.

## Stop conditions

- `claude plugin eval` is missing or older than v2.1.269, or git is older than 2.31 → report it and
  stop.
- The running total would pass the approved ceiling → stop and ask before running more.
- A component's claim cannot be turned into a check that passes and fails → say so, evaluate the
  rest, and mark that component unproven.
