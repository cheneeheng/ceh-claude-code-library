# Trigger overlap: test results

Headless runs on 2026-11-17 to see which skill loads first when `ceh-build-plan` and
`ceh-testing` are both installed and the user asks for a feature. Both descriptions claim "add a
feature" and "build this", so the question was which one wins. The answer turned out to be neither,
most of the time.

**Read the results with this caveat:** every run also loaded the tester's own global
`~/.claude/CLAUDE.md`, which holds a rule to skip planning for "a very very small app".
`--setting-sources project` does not keep that file out. One Opus run quoted the rule as its reason
to skip the plan. So these results show one user's setup, not the two plugins alone. A clean
re-run is still to do (see §04).

## 01. Environment

| Item        | Value                                                                           |
| ----------- | ------------------------------------------------------------------------------- |
| OS / shell  | Windows 11, Git Bash                                                            |
| Claude Code | 2.1.326                                                                         |
| Plugins     | `ceh-build-plan` 2.0.18 and `ceh-testing` 1.6.31, loaded by `--plugin-dir`      |
| Fixture     | The notes app from `evals/wbp-feature-neutral/scaffold.sh`, in a fresh git repo |
| Tools       | `Read`, `Glob`, `Grep`, `Skill` allowed. `Edit`, `Write` and `Bash` refused     |
| Limits      | 4 turns and $0.50 per run                                                       |

`claude plugin eval` loads only one plugin, so it cannot test two plugins competing. Edit and Write
were refused so that each run stops at its first attempt to change code. That attempt shows whether
a skill loaded before the model started building.

## 02. Results

"Plan" is `ceh-build-plan:write-build-plan` and "test" is `ceh-testing:write-test-first`. "Edit
first" means the model tried an Edit or Write before loading any skill.

| Prompt                                                                           | Sonnet, 3 runs                               | Opus, 1 run                         |
| -------------------------------------------------------------------------------- | -------------------------------------------- | ----------------------------------- |
| "ok, go ahead and add tagging to the notes app, so notes can be filtered by tag" | plan 2, edit first then test 1               | no skill                            |
| "add a feature: notes can be pinned to the top of the list"                      | edit first in all 3: then test 1, no skill 2 | edit first, then test               |
| "build this: a GET /notes/search?q= endpoint that searches note bodies"          | edit first in all 3, then test               | no skill, citing the small-app rule |

- `write-build-plan` loaded in 2 of 12 runs, both on the one prompt that does not open with a
  trigger phrase.
- `write-test-first` never loaded before a change was attempted. It loaded only after an Edit or
  Write had been refused.
- On "build this", Opus wrote: "This is a tiny app, so I'm skipping the plan-and-review step under
  the \"very small app\" exception." Opus also tried `git switch -c` first, which matches the
  tester's branch-first rule.
- The 12 runs cost $1.23 in total: $0.75 for the nine Sonnet runs and $0.48 for the three Opus runs.

## 03. Method

`trigger-overlap.sh <repo-root> <prompt-index> [model] [run-label]` runs one prompt once. It builds
the fixture in a temporary folder, runs `claude -p` with both plugins, and prints the skills loaded
in order, the cost, and the log path:

```bash
#!/usr/bin/env bash
set -uo pipefail
REPO=$1
P=$2
MODEL=${3:-sonnet}
RUN=${4:-1}
SCAFFOLD=$REPO/plugins/standalone/ceh-build-plan/evals/wbp-feature-neutral/scaffold.sh
OUT=$(cd "$(dirname "$0")" && pwd)/trigger-overlap-results
mkdir -p "$OUT"
PROMPTS=(
  "ok, go ahead and add tagging to the notes app, so notes can be filtered by tag"
  "add a feature: notes can be pinned to the top of the list"
  "build this: a GET /notes/search?q= endpoint that searches note bodies"
)
LOG=$OUT/p$P-r$RUN.jsonl
d=$(mktemp -d)
(cd "$d" && bash "$SCAFFOLD" && git init -q && git add -A && git -c user.name=t -c user.email=t@t commit -qm init)
(cd "$d" && claude -p "${PROMPTS[$P]}" \
  --model "$MODEL" \
  --setting-sources project \
  --plugin-dir "$REPO/plugins/standalone/ceh-build-plan" \
  --plugin-dir "$REPO/plugins/standalone/ceh-testing" \
  --allowedTools "Read,Glob,Grep,Skill" \
  --max-turns 4 --max-budget-usd 0.5 \
  --output-format stream-json --verbose >"$LOG" 2>&1)
echo "claude exit: $?"
rm -rf "$d"
skills=$(grep -o '"name":"Skill","input":{"skill":"[^"]*"' "$LOG" | sed 's/.*"skill":"//;s/"$//' | paste -sd, -)
cost=$(grep -o '"total_cost_usd":[0-9.]*' "$LOG" | tail -1 | cut -d: -f2)
echo "prompt $P run $RUN: skills fired in order: ${skills:-<no Skill call>}; cost: ${cost:-unknown}; log: $LOG"
```

Most runs exit 1 because they hit the 4-turn limit after the refused edit. The skill order is
already in the log by then.

## 04. Still to do

- **A clean re-run.** `--bare` skips CLAUDE.md auto-discovery while still loading `--plugin-dir`,
  but it also skips plugin hooks and accepts only `ANTHROPIC_API_KEY` for auth. Add `--bare` to the
  `claude -p` line above and set the key. `--safe-mode` does not work here, because it turns off
  skills and plugins too.
- **More Opus runs.** One run per prompt is a hint, not a rate.
