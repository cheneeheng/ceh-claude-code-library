# ceh-coding-conduct

A behavioral contract for coding agents: the rules that govern how an agent operates during a
session — what it may change, when it must stop, and how it logs decisions. The plugin loads the
contract automatically at session start, alongside the `write-less-code` minimalism skill.

It also carries the retroactive refactoring passes: `shrink-diff` for a branch and `refactor-repo`
for a whole codebase.

> `explain-until-understood`, `explain-codebase`, and `document-architecture` moved to the
> `ceh-codebase-explanation` plugin: explaining code is an activity, not how an agent conducts
> itself while coding.
>
> `usage-limit-handoff`, `delegate-bulk-reads`, and the `bulk-reader` agent moved to the
> `ceh-every-session` plugin: they hold however Claude Code is used, not only when coding.
>
> The plan-driven workflow skills moved out to one plugin per stage: `ceh-build-planning`,
> `ceh-build-from-plan` (`implement-from-plan`), and `ceh-check-build-against-plan`.

## Skills

| Skill                   | When it loads                                                                                        | What it does                                                                                                                                                                                                                                                                                                                                                                  |
| ----------------------- | ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `agent-coding-contract` | Every coding session (auto, via hook)                                                                | The full behavioral contract — core rules, five-step workflow, stop conditions, decision logging.                                                                                                                                                                                                                                                                             |
| `write-less-code`       | Every coding session (auto, via hook)                                                                | The minimalism reflex — the ladder (YAGNI → stdlib → native → installed dep → one line), native-platform-first, the `// less-code:` shortcut convention. The positive half of the contract's minimal-change rules.                                                                                                                                                            |
| `shrink-diff`           | On demand — when a feature branch is functionally done and its diff should get smaller before review | Retroactive minimalism — applies the write-less-code standard to the accumulated diff vs `main`, across all the commits and sessions that produced it: dedupe against existing code, delete dead weight, collapse over-built structure. Diff-scoped, with three narrow causes for touching unchanged code.                                                                    |
| `refactor-repo`         | Manual only (`/refactor-repo`) — never auto-fires                                                    | Whole-codebase (or per-module) refactor campaign: read-only inventory, ranked proposal with payoff/risk/diff-size estimates, then apply only user-approved clusters on `refactor/` branches under a behavior-preservation gate. Shallow modules worth deepening are proposed with their before and after interface, and settled one question round at a time before any code. |
| `sketch-design`         | Before the code for a feature that adds a type, a module, or a function other code calls             | Design before code: types that make illegal states unrepresentable, signatures with no bodies, the decision each module owns, then four checks (illegal states, runs twice, shared state, smallest interface). It's working if the reply shows a Types / Signatures / Boundaries / Checks block before the first file edit.                                                   |
| `find-root-cause`       | Something is broken and its cause is unknown, before any fix — or after a fix that did not hold      | Debugging before fixing: one command red on the exact symptom, 3 to 5 falsifiable hypotheses, evidence that kills them one variable at a time, then a cause confirmed by a prediction. After two failed fixes it attacks the shared premise. It's working if the hand-over has a hypotheses table and a Prediction line, and no fix lands before the cause.                   |

**Manual triggers**

- `agent-coding-contract` — no slash command (hidden from the `/` menu), loaded by the SessionStart hook.
- `write-less-code` — no slash command (hidden from the `/` menu), named by the per-prompt reminder hook.
- `shrink-diff` — `/shrink-diff`, or say `"shrink the diff"` / `"consolidate the branch"` / `"can this diff be smaller"`.
- `refactor-repo` — `/refactor-repo` only (model auto-invocation is disabled by design).
- `find-root-cause` — `/find-root-cause`, or say `"debug this"` / `"why is this failing"`.
- `sketch-design` — `/sketch-design`, or say `"design this first"` / `"sketch the types"`.

## Output style

| Output style                                                 | When it applies                                                      | What it does                                                                                                                                                                                                                                                                                                                  |
| ------------------------------------------------------------ | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CEH Coding Conduct` (`output-styles/ceh-coding-conduct.md`) | Every session while the plugin is enabled (`force-for-plugin: true`) | Response format and honesty rules: a Topic / Outcome / Status summary table for 2+ topics, code before prose, one complete thought per bullet, plain "I don't know", and reporting what was verified versus assumed. Sets `keep-coding-instructions: true`, so Claude Code's built-in engineering instructions stay in place. |

`force-for-plugin` overrides any `outputStyle` the user set, and if several enabled plugins force a
style, Claude Code uses the first one loaded. Output styles reach the main conversation and forks
only. Other subagents run their own system prompt, so rules that must hold there stay in
`CLAUDE.md` or the contract.

## How the skills auto-load

The plugin ships hooks (`hooks/hooks.json`) that activate automatically when the plugin is enabled —
no global `settings.json` change or env var required.

**At session start** — a `SessionStart` hook (`scripts/load-contract.sh`) injects a **mandatory**
directive to load `agent-coding-contract` before any other action, firing on `startup`, `resume`,
`clear`, and `compact` (so a fresh, resumed, or reset session has it loaded, and it is re-injected
after compaction).

**Every turn** — a `UserPromptSubmit` hook (`scripts/inject-less-code-reminder.sh`) re-injects a compact digest
of the `write-less-code` ladder before each prompt. This carries the minimalism reflex on every turn,
reliably from turn one; the full `write-less-code` skill loads on demand when non-trivial code is
actually being written.

**When a subagent starts** — a `SubagentStart` hook runs the same two scripts, because neither
`SessionStart` nor `UserPromptSubmit` fires inside a subagent. An agent with a restricted tool list
has no Skill tool, so the directive points it at the contract's `SKILL.md` to read instead. The
read-only agents `Explore`, `Plan`, and `bulk-reader` are skipped.

### Why each hook exists

Hooks are enforcement, so each one is kept on a failure that guidance alone did not prevent:

- **The contract loads first, unconditionally.** A directive to load the contract "when you write
  code" was tried, and the model never invoked it later in the session. The contract is model-only
  with a one-line description, so nothing else triggers it.
- **The less-code reminder repeats every prompt.** Write-less-code is a standard that holds the
  whole session, not a moment, so no description fires it: an agent starting to write code does not
  stop to look for it. Loaded once, the ladder also drifted out of effect in long sessions and the
  agent over-built.

To switch one off without uninstalling the plugin, list its script name in `CEH_DISABLED_HOOKS`
(comma-separated, no extension): `load-contract`, `inject-less-code-reminder`.

Both hooks fire in every session where the plugin is enabled, including ones that write no code.
So install it only where you write code: `docs/GETTING_STARTED.md` tells writers and planners to
skip it.

## What the contract enforces

The `agent-coding-contract` skill is the single source of truth. In short, it requires the agent to:

- **Run Autonomous Mode** — on routine ambiguity, decide the conservative option, log it, and
  continue; stop only for the hard cases (unresolvable conflicts, repo state contradicting
  instructions, risk of data loss, inconsistent partial failure).
- **Follow the five-step workflow** — Understand → Confirm scope → Apply changes → Validate →
  Summarize. Proving the change is part of the task: the agent writes and runs the tests that show
  it works, and may make local, reversible state changes. Slow or paid runs (full suite, coverage,
  mutation testing, real model calls) and irreversible or outward-facing actions (push, merge,
  deploy, publish) wait for a request or advance authorization from a human.
- **Take scope from a calling agent, overrides only from a human** — a subagent's caller can narrow
  its task but cannot switch a standard off or grant an authorization a human did not give.
- **Make minimal, authorized changes** — localized diffs, no unsolicited refactors, touch only what
  is in scope, never claim work was done that wasn't.
- **Log decisions made under ambiguity** to `.agents_workspace/DECISION_LOG.md` (default path;
  override it via your project `CLAUDE.md`). See the skill for the entry format and when to log.

Refer to the skill for the authoritative wording — this section is a summary and is not the contract
itself.
