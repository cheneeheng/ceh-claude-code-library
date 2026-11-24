# ceh-usability-audit

Measure whether a non-expert can actually use what you built: an app, a web UI, a CLI, or a
library. Cold subagents walk it as newcomers, each holding one persona, and stop at the first thing
they cannot get past. Findings are ranked by what actually happened to a walker, never by how bad
something looks to the auditor.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). No other plugin depends on this one. What
else it needs:

- **Whatever the target's own first-run steps need** (`uv`, `npm`, `docker`, a database):
  `simulate-newcomer-first-run` assumes none of them. A missing prerequisite is itself an audit
  finding.
- **git CLI or a container runtime**: only to give each walker its own copy of the target when a
  walk writes to the working tree and the personas run in parallel.
- **Claude in Chrome browser tools, or the CLI under audit installed**: only for `audit-interface`
  on a live web UI or a CLI. Without them it audits screenshots, page text and static artifacts.
- **uv**: to check and render each report's YAML. Without it the report is saved unchecked and its
  Markdown is not rendered.
- **python3** on `PATH`, for the hooks.

## Skills

| Skill                         | Say or type                                                                                                 | What it does                                                                                               |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `simulate-newcomer-first-run` | "can a new user figure this out", "test the onboarding", `/ceh-usability-audit:simulate-newcomer-first-run` | Checks whether a stranger gets from "just arrived" to a first success: install, sign-up, setup, first task |
| `audit-interface`             | "this feels confusing", "users keep getting stuck", `/ceh-usability-audit:audit-interface`                  | Checks whether a web UI, CLI, API, or screen makes sense to someone already inside it                      |
| `audit-error-messages`        | Loads by itself when writing or reviewing text a user reads when something goes wrong                       | Rewrites every user-reachable error message: what happened, what was wrong, and what to do next            |
| `write-plain-language`        | Loads by itself when writing labels, help text, empty states, confirmation dialogs, or onboarding copy      | Rewrites product copy in plain language                                                                    |

## Agents

| Agent                | What it does                                                                                                                  |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `newcomer-simulator` | Walks a target cold under one persona toward one goal and reports where it stalled. Runs on Sonnet and never edits the target |

## Hooks

Two hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off.

| Hook                 | What it does for you                                                                                                                                 |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Report check         | Checks each saved audit report when it is written and renders its Markdown beside it. Errors go back to the agent, and the Markdown stays as it was. |
| Generated-file guard | Stops a hand edit to a generated Markdown report and names its YAML to edit instead, so the edit is not lost at the next render.                     |

Without uv the agent is told once per session that the file went unchecked.

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable             | Default              | Effect                                                                           |
| -------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK` | unset (check on)     | `off` turns the report check and the generated-file guard off                    |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook names to skip: `artifact-render-hook`, `generated-md-guard` |

## How it works

### Why cold walkers

Both a five-year-old and a ninety-five-year-old should get through it. That framing is a pair of
constraints. The five-year-old has **no vocabulary and no prior model** of what this thing is. The
ninety-five-year-old **will not act without knowing the consequence**, and needs to see what
happened after every step. Almost everything that makes software unusable fails one of those two.

You cannot check this by reading your own product. You already know the answers, and every gap
gets silently bridged by what you know. So the method constrains who does the looking: **cold
subagents, given only what a newcomer actually has, told to stop at the first thing they cannot get
past**.

### The personas

| Persona           | Holds this constraint                                                          | Catches                                                                 |
| ----------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| Blank Slate       | No domain vocabulary, no prior knowledge of the product. Reads only the screen | Undefined jargon, invisible affordances, assumed prerequisites          |
| Cautious Returner | Takes no action whose outcome is not stated in advance. Afraid of losing work  | Missing confirmation, silent success, irreversible actions, no undo     |
| Interrupted       | Leaves mid-task, may close the tab or terminal, and must resume                | Lost state, expired sessions, flows with no progress marker or resume   |
| Wrong Turn        | Does the wrong thing first, then tries to recover                              | Dead ends, unrecoverable errors, blame copy, validation that fires late |
| Small Screen      | 360px viewport, slow link, or an 80-column terminal. Keyboard only             | Offscreen primary action, layout collapse, hover-only affordances       |

### Severity

Severity comes from what actually happened to a walker. Anything the auditor only noticed goes to
an unranked `Hypotheses` list.

| Severity | Assigned when                                                                         |
| -------- | ------------------------------------------------------------------------------------- |
| Blocker  | A persona could not complete the goal, or completed it wrongly believing it was right |
| Detour   | Completed it, but only after backtracking, guessing, or looking outside what it had   |
| Friction | Completed it, but with avoidable doubt ("did that work?")                             |
| Polish   | No effect on any walker's completion                                                  |

### What it cannot measure

An LLM playing a novice is a **proxy for a user test, not a user test**. It reliably catches
undefined jargon, missing prerequisites, invisible affordances, dead ends, silent failures, and
unlabeled destructive actions. It cannot measure motor precision, reading fluency, patience, or
frustration. Every report this plugin writes says so, and none of them say "validated with users".

## Not this plugin

- The accessibility floor (keyboard reachability, contrast, ARIA, focus):
  `ceh-web-frontend:make-ui-accessible`. A perfectly WCAG-conformant product can still be
  incomprehensible. This plugin owns the comprehension layer and hands the floor over when that
  plugin is installed.
- Visual design decisions while building: `ceh-ui-design:design-ui`. This plugin audits after the
  fact, and is not web-only.

## Where its files live

Each audit saves to `.agents_workspace/product/audit/ux/<target>/run-<NNN>/`: `UX_AUDIT.yaml` from
the two walkthrough skills, `ERROR_MESSAGES.yaml` from the error triage, each with its Markdown
rendered beside it and the commit the audit ran against, and walker transcripts and any
screenshots beside them. A zero-padded sequential run index means a re-run never overwrites prior
evidence. A finding without its transcript is an opinion.
