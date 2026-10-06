# ceh-coding-agent

A behavioral contract for coding agents: the rules that govern how an agent operates during a
session — what it may change, when it must stop, and how it logs decisions. The plugin loads the
contract automatically at session start, alongside the `write-less-code` minimalism skill.

It also carries the whole-repo passes an agent runs over code it did not write: `explain-codebase`
and `refactor-repo`.

> `usage-limit-handoff`, `delegate-bulk-reads`, and the `bulk-reader` agent moved to the
> `ceh-core` plugin: they hold however Claude Code is used, not only when coding.
>
> The plan-driven workflow skills (`implement-from-plan`, `review-against-plan`) moved to the
> `ceh-plan-build-review` plugin, which bundles them with the planning skills.

## Skills

| Skill                      | When it loads                                                                                         | What it does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| -------------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `agent-coding-contract`    | Every coding session (auto, via hook)                                                                 | The full behavioral contract — core rules, five-step workflow, stop conditions, decision logging.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `write-less-code`          | Every coding session (auto, via hook)                                                                 | The minimalism reflex — the ladder (YAGNI → stdlib → native → installed dep → one line), native-platform-first, the `// less-code:` shortcut convention. The positive half of the contract's minimal-change rules.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `shrink-diff`              | On demand — when a feature branch is functionally done and its diff should get smaller before review  | Retroactive minimalism — applies the write-less-code standard to the accumulated diff vs `main`, across all the commits and sessions that produced it: dedupe against existing code, delete dead weight, collapse over-built structure. Diff-scoped, with three narrow causes for touching unchanged code.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `refactor-repo`            | Manual only (`/refactor-repo`) — never auto-fires                                                     | Whole-codebase (or per-module) refactor campaign: read-only inventory, ranked proposal with payoff/risk/diff-size estimates, then apply only user-approved clusters on `refactor/` branches under a behavior-preservation gate.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `explain-until-understood` | On demand — when someone in the session needs a subsystem, design, diff, or unfamiliar tool explained | How an explanation is built and what to do when it misses: assume the reader is new to the project and knows nothing about the subject, and say what floor you are building from; read the real code (never a design doc), foundations before the specific case, plain language (concept before name, every term of art defined at first use, project-local names included), verified output over described output, plain-ASCII pictures for structure and time (no box-drawing or arrow glyphs), a numbered walk of one ordinary case end to end, close on a transferable rule plus a self-test. Ships the escalation ladder — prose → steps → pictures → foundations — with the rule that a miss at pictures means a skipped foundation, not a missing detail; a reader lost on a _word_ is not on the ladder at all. Writes no files by default — `.agents_workspace/` scratch notes on request, and one narrow repo path for a subsystem explainer no other skill owns. |
| `explain-codebase`         | On demand — when the ask is to understand a whole repo and leave the understanding in a file          | Whole-repo orientation: what each component does, how they connect, and the key flows, written into a git-ignored `.agents_workspace/CODEBASE_EXPLAINED.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `document-architecture`    | On demand — when the system's shape or a durable decision needs recording                             | The living `.agents_workspace/ARCHITECTURE.md`: a 3-second Overview, Mermaid diagrams (components, key flows, data model, state machines), and an append-only Key Decisions log. Updated on shape change, not every commit.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

**Manual triggers**

- `agent-coding-contract` — no slash command (hidden from the `/` menu), loaded by the SessionStart hook.
- `write-less-code` — no slash command (hidden from the `/` menu), say `"write less code"` / `"be lazy"` / `"simplest solution"` / `"yagni"`.
- `shrink-diff` — `/shrink-diff`, or say `"shrink the diff"` / `"consolidate the branch"` / `"can this diff be smaller"`.
- `refactor-repo` — `/refactor-repo` only (model auto-invocation is disabled by design).
- `explain-until-understood` — `/explain-until-understood [what to explain]`, or ask for something to be explained until it makes sense.
- `explain-codebase` — `/explain-codebase`, or say `"explain this codebase"` / `"what does this repo do"`.
- `document-architecture` — `/document-architecture`, or say `"write the architecture doc"` / `"diagram the system"` / `"record this decision"`.

## Output style

| Output style                                             | When it applies                                                      | What it does                                                                                                                                                                                                                                                                                                                  |
| -------------------------------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CEH Coding Agent` (`output-styles/ceh-coding-agent.md`) | Every session while the plugin is enabled (`force-for-plugin: true`) | Response format and honesty rules: a Topic / Outcome / Status summary table for 2+ topics, code before prose, one complete thought per bullet, plain "I don't know", and reporting what was verified versus assumed. Sets `keep-coding-instructions: true`, so Claude Code's built-in engineering instructions stay in place. |

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

**Every turn** — a `UserPromptSubmit` hook (`scripts/less-code-payload.sh`) re-injects a compact digest
of the `write-less-code` ladder before each prompt. This carries the minimalism reflex on every turn,
reliably from turn one; the full `write-less-code` skill loads on demand when non-trivial code is
actually being written.

**When a subagent starts** — a `SubagentStart` hook runs the same two scripts, because neither
`SessionStart` nor `UserPromptSubmit` fires inside a subagent. An agent with a restricted tool list
has no Skill tool, so the directive points it at the contract's `SKILL.md` to read instead. The
read-only agents `Explore`, `Plan`, and `bulk-reader` are skipped.

## What the contract enforces

The `agent-coding-contract` skill is the single source of truth. In short, it requires the agent to:

- **Run Autonomous Mode** — on routine ambiguity, decide the conservative option, log it, and
  continue; stop only for the hard cases (unresolvable conflicts, repo state contradicting
  instructions, risk of data loss, inconsistent partial failure).
- **Follow the five-step workflow** — Understand → Confirm scope → Apply changes → Validate →
  Summarize. Quick checks scoped to the edit are always allowed; test suites, builds, and
  state-changing commands run only when explicitly requested.
- **Make minimal, authorized changes** — localized diffs, no unsolicited refactors, touch only what
  is in scope, never claim work was done that wasn't.
- **Log decisions made under ambiguity** to `.agents_workspace/DECISION_LOG.md` (default path;
  override it via your project `CLAUDE.md`). See the skill for the entry format and when to log.

Refer to the skill for the authoritative wording — this section is a summary and is not the contract
itself.
