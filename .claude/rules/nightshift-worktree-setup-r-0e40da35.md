---
schema: nightshift-rule/v1
decided: 2026-11-24
source: "nightshift rule r-0e40da35"
---

# Worktree setup

Before creating a worktree for a task, run `git status` to check whether files the work needs are untracked, and dry-run the commands it needs there (such as `claude plugin eval --help`, which the worktree guard refuses because it contains "eval"); settle how runs will execute before asking the user to approve a plan, because an untracked `evals-interactive/` folder was missing from the worktree, and seven eval cases and a plan were drafted and approved before the guard refused the probe.
