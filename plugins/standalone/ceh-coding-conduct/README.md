# ceh-coding-conduct

How an agent behaves while it codes: what it may change, when it must stop, how it logs decisions,
and how little code it writes. The plugin loads its coding contract and the `write-less-code`
standard at the start of every session, with no setup. It also carries root-cause debugging and
two refactoring passes: `shrink-diff` for a branch and `refactor-repo` for a whole codebase.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). Some parts need more installed:

| Needs                            | For                                               | Without it                                                        |
| -------------------------------- | ------------------------------------------------- | ----------------------------------------------------------------- |
| `bash`                           | Loading the contract and the less-code reminder   | The contract and reminder are not loaded by themselves            |
| `python3` on PATH                | The fix record check and the generated-file guard | Both do nothing                                                   |
| [uv](https://docs.astral.sh/uv/) | Checking a saved fix record or refactor report    | The file is saved unchecked, and the agent is told once a session |

The hooks fire in every session where the plugin is enabled, including ones that write no code. So
install it only where you write code: [Getting started](../../../docs/GETTING_STARTED.md) tells
writers and planners to skip it.

## Skills

| Skill                   | Say or type                                                                                                              | What it does                                                                                                                                                                                                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `agent-coding-contract` | Loads by itself at the start of every session                                                                            | The behavioral contract: core rules, the five-step workflow, stop conditions, and decision logging. See [What the contract enforces](#what-the-contract-enforces).                                                                                                            |
| `write-less-code`       | Loads by itself at the start of every session, with a short reminder before every prompt                                 | The minimalism reflex: the ladder (YAGNI, stdlib, native platform, installed dependency, one line), and the `// less-code:` comment that marks a deliberate shortcut.                                                                                                         |
| `find-root-cause`       | "debug this", "find and fix these bugs", "why is this failing", `/ceh-coding-conduct:find-root-cause`                    | Debugs before fixing: one command red on the exact symptom, 3 to 5 falsifiable hypotheses, evidence that kills them one at a time, then a cause confirmed by a prediction. After two failed fixes it questions the shared premise. It saves one fix record per functionality. |
| `shrink-diff`           | "shrink the diff", "consolidate the branch", "can this diff be smaller", `/ceh-coding-conduct:shrink-diff [base-branch]` | For a branch that works: applies the write-less-code standard to its whole diff against `main`, removing duplication, dead code and over-built structure. It touches unchanged code only for three narrow causes.                                                             |
| `refactor-repo`         | `/ceh-coding-conduct:refactor-repo [module-or-path]` only. It never starts by itself                                     | A refactor of a whole codebase or one module: a read-only inventory, a ranked proposal with payoff, risk and diff size, then only the clusters you approve, on `refactor/` branches, with behavior checked before and after.                                                  |

## Agents

This plugin has no agents.

## Hooks

The hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off.

| Hook                 | What it does for you                                                                                                                                                  |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Contract loader      | At the start, resume, clear and compaction of a session, tells the agent to load the contract and `write-less-code` first, then pick the skills that fit the request. |
| Less-code reminder   | Before every prompt, adds a short digest of the write-less-code ladder.                                                                                               |
| Subagent loader      | Does both of the above when a subagent starts. Read-only agents, such as `Explore`, `Plan` and agents whose name ends in `-reviewer`, are skipped.                    |
| Fix record check     | Checks each fix record and refactor report when it is written, and renders its readable Markdown copy. Errors go back to the agent to fix.                            |
| Generated-file guard | Stops a hand edit to a Markdown file generated from a YAML file, and names the YAML to edit instead, so the edit is not lost at the next render.                      |

With `ceh-testing` installed too, its hooks check the same fix record, so an error is reported
twice.

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable             | Default              | Effect                                                                                                                         |
| -------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook names to skip: `load-contract`, `inject-less-code-reminder`, `artifact-render-hook`, `generated-md-guard` |
| `CEH_ARTIFACT_CHECK` | unset (check on)     | `off` turns the fix record check and the generated-file guard off                                                              |

## How it works

### What the contract enforces

The `agent-coding-contract` skill is the single source of truth. In short, it requires the agent to:

- **Run Autonomous Mode.** On routine ambiguity, decide the conservative option, log it, and
  continue. Stop only for the hard cases: unresolvable conflicts, repo state contradicting
  instructions, risk of data loss, inconsistent partial failure.
- **Follow the five-step workflow.** Understand, Confirm scope, Apply changes, Validate, Summarize.
  Proving the change is part of the task: the agent writes and runs the tests that show it works,
  and may make local, reversible state changes. Slow or paid runs (full suite, coverage, mutation
  testing, real model calls) and irreversible or outward-facing actions (push, merge, deploy,
  publish) wait for a request or advance authorization from a human.
- **Take scope from a calling agent, overrides only from a human.** A subagent's caller can narrow
  its task but cannot switch a standard off or grant an authorization a human did not give.
- **Make minimal, authorized changes.** Localized diffs, no unsolicited refactors, touch only what
  is in scope, never claim work was done that wasn't.
- **Log decisions made under ambiguity** to `.agents_workspace/DECISION_LOG.md` (default path,
  override it in your project `CLAUDE.md`). See the skill for the entry format and when to log.

Refer to the skill for the authoritative wording. This section is a summary and is not the
contract itself.

## Not this plugin

- Explaining code or documenting architecture: `ceh-codebase-explanation`.
- The usage-limit handoff and the `bulk-reader` agent: `ceh-every-session`.
- Planning and building from a plan: `ceh-build-plan`. Checking the build against the plan:
  `ceh-check-build-against-plan`.
- Writing the failing test for a bug fix: `ceh-testing:test-a-bug-fix`, which reads the fix record
  `find-root-cause` saves.

## Where its files live

The plugin saves and reads its files in `.agents_workspace/`: the decision log at
`.agents_workspace/DECISION_LOG.md`, fix records in `.agents_workspace/product/fix/`, and refactor
reports in `.agents_workspace/product/refactor/`, each as a YAML file with its Markdown copy beside
it. A project with a root `product/` folder moves each file to the same sub-path under
`.agents_workspace/product/`, or names its own location in `CLAUDE.md`.
