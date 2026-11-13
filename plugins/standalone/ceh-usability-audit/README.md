# ceh-usability-audit

Measure whether a non-expert can actually use what you built — an app, a web UI, a CLI, or a
library.

Both a five-year-old and a ninety-five-year-old should get through it. That framing is not
sentiment; it is a pair of constraints. The five-year-old has **no vocabulary and no prior model**
of what this thing is. The ninety-five-year-old **will not act without knowing the consequence**,
and needs to see what happened after every step. Almost everything that makes software unusable
fails one of those two.

You cannot check this by reading your own product. You already know the answers, and every gap gets
silently bridged by what you know. So the method here is to constrain who does the looking:
**cold subagents, given only what a newcomer actually has, told to stop at the first thing they
cannot get past** — and to rank findings by what actually happened to a walker, never by how bad
something looks to the auditor.

## What this is not

`ceh-web-frontend:make-ui-accessible` owns the mechanical floor — keyboard reachability, contrast,
ARIA, focus. A perfectly WCAG-conformant product can still be incomprehensible; this plugin owns the
comprehension layer and delegates the floor rather than re-deriving it.
`ceh-ui-design:design-ui` owns build-time visual decisions. This plugin audits after the fact,
and is not web-only. Both hand-offs are conditional, so neither `ceh-web-frontend` nor
`ceh-ui-design` is a dependency.

## Honest limits

An LLM playing a novice is a **proxy for a user test, not a user test**. It reliably catches
undefined jargon, missing prerequisites, invisible affordances, dead ends, silent failures, and
unlabeled destructive actions. It cannot measure motor precision, reading fluency, patience, or
frustration. Every report this plugin writes says so, and none of them say "validated with users".

## Skills

| Skill                         | Invoke                                             | Triggers when                                                                                            |
| ----------------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `simulate-newcomer-first-run` | `/ceh-usability-audit:simulate-newcomer-first-run` | Can a stranger get from "just arrived" to first success: install, sign-up, setup, onboarding, first task |
| `audit-interface`             | `/ceh-usability-audit:audit-interface`             | They are already in: is the web UI, CLI, API, or screen comprehensible                                   |
| `audit-error-messages`        | Model-only, no slash command                       | Writing or reviewing anything a user reads when something goes wrong                                     |
| `write-plain-language`        | Model-only, no slash command                       | Writing or rewriting labels, help text, empty states, confirmation dialogs, onboarding copy              |

## Agents

| Agent                | Invoke                                              | When                                                                                                              |
| -------------------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `newcomer-simulator` | `@"ceh-usability-audit:newcomer-simulator (agent)"` | Walk a target cold under one persona toward one goal and report where it stalled (Sonnet, never edits the target) |

## Prerequisites

- **Whatever the target's own first-run steps need** (`uv`, `npm`, `docker`, a database):
  `simulate-newcomer-first-run` assumes none of them. A missing prerequisite is itself an audit finding.
- **git CLI or a container runtime**: only to give each walker its own copy of the target when a
  walk writes to the working tree and the personas run in parallel.
- **Claude in Chrome browser tools, or the CLI under audit installed**: only for `audit-interface`
  on a live web UI or a CLI. Without them it audits screenshots, page text and static artifacts.
- **uv**: to check and render each report's YAML. Without it the report is saved unchecked and its
  Markdown is not rendered.

## Hooks

| Hook                                                                    | Event                                        | Script                    | Default |
| ----------------------------------------------------------------------- | -------------------------------------------- | ------------------------- | ------- |
| [Report render](#report-render-and-generated-markdown-guard)            | `PostToolUse` (`Edit`, `Write`, `MultiEdit`) | `artifact-render-hook.py` | on      |
| [Generated Markdown guard](#report-render-and-generated-markdown-guard) | `PreToolUse` (`Edit`, `Write`, `MultiEdit`)  | `generated-md-guard.py`   | on      |

### Report render and generated Markdown guard

`simulate-newcomer-first-run` and `audit-interface` save `UX_AUDIT.yaml` (`first-run-audit/v2` and
`interface-audit/v2`), and `audit-error-messages` saves `ERROR_MESSAGES.yaml`
(`error-messages-audit/v2`). After every write to one, the render hook picks the model by the
file's `schema:` key, checks the YAML through `uv` and renders the Markdown beside it, or reports
each error back to the agent and leaves the Markdown as it was. The guard denies a direct edit to a
generated Markdown file and names its YAML. Both need `uv`: without it the agent is told once per
session that the file went unchecked. `CEH_ARTIFACT_CHECK=off`, or `CEH_DISABLED_HOOKS` with
`artifact-render-hook` or `generated-md-guard`, switches them off, and these are the only
environment variables the plugin reads.

## Output

`.agents_workspace/product/ux-audits/<target>/run-<NNN>/` — `UX_AUDIT.yaml` from the two walkthrough
skills, `ERROR_MESSAGES.yaml` from the error triage, each with its Markdown rendered beside it and
the commit the audit ran against, and walker transcripts and any screenshots beside them. A
zero-padded sequential run index means a re-run never overwrites prior evidence. A finding without
its transcript is an opinion.
