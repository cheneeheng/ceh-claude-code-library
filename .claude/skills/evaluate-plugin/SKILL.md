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
  hill-climb converter, which fails at import on an older Python. On Linux, `--allow-tools Bash`
  needs `bubblewrap` and `socat` (`apt install bubblewrap socat`), or the CLI refuses the run.
  Hill-climb reports need node or bun, or fall back to a Markdown table.
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
3. **Draft the cases** under `<plugin>/evals/<case>/` (`prompt.md` plus `graders/*.md`), by hand
   or from `claude plugin eval init --bare <case>` (Rules says why not plain `init`). Keep the
   prompts short, phrased as users type. Source them in this order and say which you used:
   1. Real prompts from the user's transcripts, `<home>/.claude/projects/<project>/*.jsonl`, that
      should have used the component. Replace home paths with `<home>` and `<project>`.
   2. Examples the user gives.
   3. Prompts you write from the component's text, seeded from 1 or 2. Label them synthetic.

   A case is **must-act**, where the component should fire, or **must-stay-quiet**, where it
   should not. Score the two apart, so a component that fires on everything cannot score well.
   Tag each case `trigger` when it grades whether the component fired, or `outcome` when it
   grades the result.

   | Component               | Drafted set                                                                                                                   |
   | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
   | Skill                   | One task as three must-act cases, one per strictness level; two near-misses; one `outcome` case per result the skill promises |
   | Hook, agent, MCP server | One must-act case and one must-stay-quiet case                                                                                |

   A near-miss is a must-stay-quiet prompt that shares keywords with the skill but needs
   something else. The strictness levels put one task three ways, so a score drop comes from the
   wording alone:

   | Level      | The prompt                                                                         | Example for a pull request skill         |
   | ---------- | ---------------------------------------------------------------------------------- | ---------------------------------------- |
   | Supportive | Names the moment the skill is for                                                  | "I'm opening a PR, write the body"       |
   | Neutral    | Gives the task only                                                                | "Here's my branch, get it merged"        |
   | Competing  | Gives the task plus a pull away from the skill's rule, tempting and never ordering | "Make it quick, the reviewer is waiting" |

   For each component, draft what a good result must contain or do and what would make it bad.
   Write each `llm` rubric and file pattern from that draft, which step 5 puts to the user.

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

5. **Get the plan approved, in one round.** The user decides whether the component is good, so
   they set what good means and how much proof to pay for. Ask once, over the drafted cases:
   - The case list (prompt, tag, graders) and the prompt source.
   - Per component, the drafted good result and bad result, as recommended answers to confirm or
     change.
   - A size. Each keeps all three strictness levels:

     | Size    | Per skill                               | Extras                                                        |
     | ------- | --------------------------------------- | ------------------------------------------------------------- |
     | Small   | One task at three levels, one near-miss | No outcome case                                               |
     | Drafted | The set of step 3                       | None                                                          |
     | Hard    | Two tasks at three levels               | Competing plugins loaded, outcome fixtures with planted traps |

     Show each size with its cases × runs per case × arms, its cost, and its noise floor per
     scored group (must act, must stay quiet, outcome). An arm is one way a case runs: with the
     plugin, or without it as the baseline. The **noise floor** is how far chance alone moves a
     pass rate, about `1/sqrt(cases × runs)`: five cases at three runs give 0.26, so a move from
     60% to 80% is not a result. Label a size whose floor in any group is above 0.2 directional,
     here and in the report. Runs per case (`--runs`, default 3) is the second lever, cheapest
     on single-arm `trigger` cases.

   - A spending ceiling. Take the cost per run from the newest
     `<plugin>/evals/results/*/aggregate-result.json` (`costUsd` over its run count, `outcome`
     and `trigger` cases apart), else a saved report for the same plugin, else mark the figure a
     guess for the probe to correct. Add judge calls: three per `llm` grader per run. Add the
     three trap runs per `llm` grader of step 6.

   Apply the answers to the case files. With no user present, take the drafted criteria, mark
   them unconfirmed in the report, run only the free checks (step 2 and the regex check of
   step 6), and give the drafted ceiling with the exact probe and suite commands.

6. **Probe before the suite**, in this order:
   1. **Check each `regex` grader for free.** Run one whose target is the reply or a file
      against a correct and a wrong sample: it must pass the first and fail the second. Graders
      use JavaScript regex, so run the pattern with `node -e`. Without node, use Python's `re`
      with `m`, `i`, `s` mapped to `re.M`, `re.I`, `re.S`, and note that Python's `$` also
      matches before a final newline. Honor `match`: `not_contains` inverts the result,
      `count:N` needs exactly N matches. Leave `trace`, `files` and `mock_calls` patterns, and
      `tool_used` and `tool_order` graders, to the paid probe.
   2. **Run one case once:**
      `claude plugin eval <plugin> --case <one> --runs 1 --ablation none --max-cost-usd 1 --no-publish`.
      Recompute the total from its real cost.
   3. **Trap each `llm` grader.** Add three throwaway cases with the same grader, whose prompts
      make Claude reply with nothing, with "I don't know", and with a confident answer to the
      wrong question. Run them once each, with the probe's command and `--case` set to their
      names: all three must fail. Fix a grader that passes any of them, then delete the
      throwaway cases.

   Flags for every paid run, the probe included:

   | Flag                      | Add it when                                                                                           |
   | ------------------------- | ----------------------------------------------------------------------------------------------------- |
   | `--no-publish`            | Always                                                                                                |
   | `--max-cost-usd <usd>`    | Always, as what is left of the ceiling                                                                |
   | `--scaffold`              | A case sets `context.scaffold_script`: without it every `source: file` grader fails on a missing path |
   | `--allow-tools <tools>`   | A case needs a gated tool, such as Bash                                                               |
   | `--ablation with-without` | A `context.history_file` case on a path target should show a `Δ`: it runs single-arm by default       |

7. **Run the suite** in the background, as two invocations that share what is left of the
   ceiling:
   - `trigger` cases with `--ablation none`, so one arm: under two arms a `tool_used: Skill`
     grader only marks whether the plugin fired and does not count toward the score.
   - `outcome` cases with the default two arms: `Δ` is the score with the plugin minus the
     score without it, so it shows what the plugin adds.
8. **Read the result.** Open `<plugin>/evals/results/<timestamp>/aggregate-result.json`. Leave out
   runs with a non-null `error` that scored without graders: those are API failures, not plugin
   failures. Read the grader explanations of three failing runs and confirm the verdict before
   trusting it.
9. **Fix one gap per round.** Pick the failure that costs the most cases and name its cause:

   | Failure                                                        | Cause                                                         | Fix                                                                                                    |
   | -------------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
   | The skill does not load, at neutral only or even at supportive | Description: it is all Claude sees when it picks a skill      | Rewrite the description: the Description loop below when skill-creator is installed, otherwise by hand |
   | The skill loads, and the result is wrong even at supportive    | Body: the skill was in play and still led to the wrong result | Rewrite the section that causes it                                                                     |
   | Fails at all three levels, and the step shows in a tool call   | Prose cannot hold it                                          | Propose a hook                                                                                         |
   | Two-arm run: `tool_used: Skill` passes but `Δ` is negative     | Judge                                                         | Re-run with `--judge-model sonnet`, tighten the rubric so formatting cannot decide the verdict         |
   | The output is right but the grader fails it                    | Grader                                                        | Fix the grader, re-run every case it grades                                                            |
   | Errored before producing output                                | Setup                                                         | Fix the case's tools, mocks, or limits                                                                 |

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

One round of the script:

1. Deletes what an earlier run of the same variant left.
2. Runs
   `claude plugin eval --ablation none --keep-temp --no-publish --trust-plugin --output-dir <flow>/<variant>/raw`.
   `--trust-plugin` answers the eval's first-run trust question, so settle the Rules line on
   which plugins to evaluate before the first round.
3. Writes `results.jsonl`, `traces/` and `errors.jsonl` beside `raw/`, in the layout the
   hill-climb guide reads, with the fields of a row listed in the script's docstring. A run it
   cannot convert becomes a row in `errors.jsonl`. It creates `summary.json` when that is
   missing, holding the variant name and `--target` only.
4. Deletes the temp directories `--keep-temp` left, and warns on stderr for each one it could
   not delete.

Exit 2 with nothing converted means the eval died before writing its result. The script then
names the temp folder where kept directories remain: delete the `claude-eval-*` ones there by
hand.

Tell the guide three things:

- The artifact under change is the component file, loaded through Claude Code's real discovery,
  so a round tests both whether the model finds it and whether it helps.
- The script has no harness-integrity gate. List the script and every `evals/` grader in
  `harness_paths`, and never edit them during a round.
- Below about 50 cases the guide's rule for a small set applies: tune and check on the same
  cases, with none held back as a test set, raise the runs per case, and label every score
  directional.

## Rules

- Write the cases yourself, not with `claude plugin eval init` as the doc recommends: `init`
  opens its own interactive session and trials its graders before any ceiling is agreed, and the
  doc does not say it takes prompts from transcripts or writes three strictness levels.
  `init --bare <case>` is fine for a blank template.
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
