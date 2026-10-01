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
`ceh-web-frontend:design-ui` owns build-time visual decisions. This plugin audits after the fact,
and is not web-only. Both hand-offs are conditional, so `ceh-web-frontend` is not a dependency.

## Honest limits

An LLM playing a novice is a **proxy for a user test, not a user test**. It reliably catches
undefined jargon, missing prerequisites, invisible affordances, dead ends, silent failures, and
unlabeled destructive actions. It cannot measure motor precision, reading fluency, patience, or
frustration. Every report this plugin writes says so, and none of them say "validated with users".

## Skills

| Skill                  | Invoke                                      | Triggers when                                                                                            |
| ---------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `walk-first-run`       | `/ceh-usability-audit:walk-first-run`       | Can a stranger get from "just arrived" to first success: install, sign-up, setup, onboarding, first task |
| `audit-interface`      | `/ceh-usability-audit:audit-interface`      | They are already in: is the web UI, CLI, API, or screen comprehensible                                   |
| `audit-error-messages` | `/ceh-usability-audit:audit-error-messages` | Writing or reviewing anything a user reads when something goes wrong                                     |
| `write-plain-language` | `/ceh-usability-audit:write-plain-language` | Writing or rewriting labels, help text, empty states, confirmation dialogs, onboarding copy              |

### `walk-first-run`

**Auto-triggers on:** "can a new user figure this out", "is the setup clear", "test the onboarding",
"try this with fresh eyes", "would a beginner get stuck", "nobody can install this", or before
shipping a README, install guide, or sign-up flow.

Freezes the artifact set a newcomer actually receives, dispatches one cold `novice-walker` per
persona, and records where each stopped. Three measurements make the ranking reproducible:
**actions per milestone against a budget declared before the walk**, **external lookups** (anything
above zero is a Detour by definition, and the missing information names its own fix), and **machine
wait** — the real seconds a human spends watching an install. Loops fix → re-run until a 5-point
gate passes.

**The budget is what stops "technically possible" from passing.** Without it a README that takes
forty steps scores as clean, because nobody stalled outright — and length is the most common
usability failure after an outright blocker. So the goal is split into two to four milestones, each
gets a maximum action count written down _before_ dispatch, and an overrun is a Detour (a Blocker
past 2×). When there is no basis for a number, the budget is the step count the documentation itself
prescribes: a walker needing materially more means the doc omits steps reality requires.

**On time specifically:** walker wall-clock is a fact about model throughput, not about your
product, and the skill refuses to record it. What it reports instead is the action count
(reproducible, a property of the design) translated through a **fixed, published cost model** —
15s to read a line, 30s to choose between two options, 90s to create an account — and printed as
`estimated ~6 min (model, not measured)`. Machine wait is the one genuine clock and is measured for
real. Never "users take N minutes".

### `audit-interface`

**Auto-triggers on:** "this feels confusing", "users keep getting stuck", "review this UI for
usability", "why does nobody find this button", "our API is hard to use", "the CLI is confusing", or
before shipping a screen, command, or public API.

Branches on surface first — a web UI, a CLI, a library API, and an app screen are probed differently
— then runs the **five questions** every surface must answer unasked (where am I; what is this for;
what can I do, and which is _the_ thing; what just happened; how do I get out), a twelve-item
reject-on-sight anti-pattern sweep, the naming test, and the persona battery.

### `audit-error-messages`

**Auto-triggers on:** "improve the error messages", "this error is useless", "users do not
understand this error", "what should this exception say", "review the validation messages", or when
adding a `raise`/`throw`/toast a user will read.

Harvests every user-reachable string, triages each against the **three-part rule** — what happened,
what specifically was wrong (the offending value, quoted), what to do next — and produces a rewrite
table. Part 3 is the one that gets dropped and the one that decides whether the user recovers or
files a ticket; **"see the docs" does not satisfy it**. Applies to libraries as much as UIs: a
`ValueError` with no offending value is the same defect as a toast saying "failed".

### `write-plain-language`

**Auto-triggers on:** "make this clearer", "simplify this wording", "rewrite this for non-technical
users", "plain English", "our copy is too technical", "write the empty state", or when naming a
button, field, setting, or command.

A vocabulary floor you can check a word against, a swap table, seven sentence rules,
define-on-first-use for surviving domain terms, and label/button/number conventions. Carries an
explicit **never simplify** list — legal wording, destructive-action consequences, auth failure
detail, exact identifiers and limits — because simplification that removes precision is a
regression. Say less, not vaguer.

## Agents

| Agent           | Invoke                                         | When                                                                                                 |
| --------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `novice-walker` | `@"ceh-usability-audit:novice-walker (agent)"` | Walk a target cold under one persona toward one goal and report where it stalled (Sonnet, read-only) |

### `novice-walker`

The instrument the two audit skills are built on. Walks a target cold under one persona toward one
goal, and reports where it stalled. Read-only — it never edits, fixes, or suggests.

**Auto-triggers on:** "try this with fresh eyes", "where would a beginner get stuck", "walk the
setup cold", "pretend you know nothing about this project".

Its one load-bearing rule: **it may not use anything it already knows about how tools like this
usually work.** A model will happily infer `pip install -e .` from a `pyproject.toml` the README
never mentioned — and that inference is exactly the gap a newcomer falls into. When the next step is
not in the allowlist, that is a stall, not something to work out. Runs on Sonnet deliberately: a
weaker reader is a more honest novice proxy, and cheaper to run five of.

The rule has exactly one exception, the **audience baseline** — one line naming what the intended
audience already knows, passed in at dispatch. Without it the rule eats itself: a walker told to
assume nothing stalls on "terminal", "clone", and "browser tab", so it returns a Blocker on every
target and the gate can never pass. The baseline covers general background only, never the product
itself. It is recorded verbatim in the report, because two audits under different baselines are not
comparable.

It also distinguishes three ways a walk can end — reached the goal, hit a stall, **ran out of
turns** — and the third is an instrument failure, never a finding. Scoring turn exhaustion as "could
not complete the goal" manufactures a Blocker out of the agent's own limits.

**Parallelism depends on what the walk touches.** Five read-only walkers run at once safely. Five
walkers each running `npm install` in the same checkout corrupt each other's transcripts, so a walk
that writes to the working tree runs one persona at a time or gives each its own copy.

**Browser limit:** subagents lose the Chrome tools, so it cannot drive a live web UI. Web walks stay
in the main session, or the agent is handed screenshots and page text instead of a URL.

## Prerequisites

- **Whatever the target's own first-run steps need** (`uv`, `npm`, `docker`, a database):
  `walk-first-run` assumes none of them. A missing prerequisite is itself an audit finding.
- **git CLI or a container runtime**: only to give each walker its own copy of the target when a
  walk writes to the working tree and the personas run in parallel.
- **Claude in Chrome browser tools, or the CLI under audit installed**: only for `audit-interface`
  on a live web UI or a CLI. Without them it audits screenshots, page text and static artifacts.

The plugin reads no environment variables.

## The personas

Five constraints, each catching a distinct failure class. Shared by both audit skills.

| Persona               | Constraint                                                                                            | Catches                                                             |
| --------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| **Blank Slate**       | Knows the declared audience baseline and nothing past it _(the 5-year-old proxy)_                     | Undefined jargon, invisible affordances, assumed prerequisites      |
| **Cautious Returner** | Will not act without knowing the outcome; needs feedback after every action _(the 95-year-old proxy)_ | Missing confirmation, silent success, irreversible actions, no undo |
| **Interrupted**       | Leaves mid-task, comes back                                                                           | Lost state, expired sessions, no progress marker or resume path     |
| **Wrong Turn**        | Does the wrong thing first, then tries to recover                                                     | Dead ends, unrecoverable errors, blame copy, late validation        |
| **Small Screen**      | 360px, slow link, or 80 columns; keyboard only                                                        | Offscreen primary action, hover-only affordances, truncated output  |

## Severity — assigned by outcome, not by appearance

This is the rule that keeps a report from becoming a list of preferences.

| Severity     | Assigned when                                                                           |
| ------------ | --------------------------------------------------------------------------------------- |
| **Blocker**  | A persona could not complete the goal — or completed it wrongly believing it was right  |
| **Detour**   | Completed it, but after backtracking, guessing, or looking outside what they were given |
| **Friction** | Completed it, but with avoidable doubt — "did that work?"                               |
| **Polish**   | No effect on any walker's completion                                                    |

Something you noticed that no walker stalled on is a **Hypothesis**, not a finding: listed
separately, unranked, and it does not count against the gate. This feels too strict on a real
violation — the alternative is a report where the loud items are whatever the auditor happened to
care about.

## Output

`.agents_workspace/ux-audits/<target>/run-<NNN>/` — `UX_AUDIT.md` from the two walkthrough skills,
`ERROR_MESSAGES.md` from the error triage, with walker transcripts and any screenshots beside them.
A zero-padded sequential run index means a re-run never overwrites prior evidence. A finding without
its transcript is an opinion.

## Known weak points — check these two first when evaluating

Both are deliberate design choices, not oversights, and both are the most likely places this plugin
is wrong. Anyone evaluating it should attack them before anything else.

### 1. Severity is assignable only from an observed stall

Anything the auditor merely noticed — a real anti-pattern, an obviously bad label — is demoted to
the unranked `Hypotheses` list and **cannot affect the gate**.

**Why it might be wrong:** it under-reports. A genuine violation that no walker happened to hit is
suppressed, and the fewer personas you run the more it suppresses. On a surface where you ran three
personas instead of five, a report can read 5/5 while a real Blocker sits in `Hypotheses`.

**Why it is there anyway:** the alternative is a report ranked by whatever the auditor cared about,
which is the failure mode of every usability checklist — and the one thing this plugin exists to
avoid.

**How to test it:** run an audit on a surface with a known, deliberately planted usability defect,
using a goal that does not route through it. If it lands in `Hypotheses` and the gate still passes,
decide whether that trade is acceptable to you. The tunable is the number of personas and the number
of distinct goals walked, not the rule.

**Partly mitigated by the action budget:** it catches a class this rule would miss entirely — a
flow nobody stalls on but everybody suffers through. Overrun is scored from measured actions, so it
feeds the gate without reintroducing auditor taste. It does nothing for a defect that is off the
walked path, which remains the open half of this weakness.

### 2. `novice-walker` cannot drive a browser

Background subagents keep a reduced tool set, so the Chrome tools are stripped. Live web-UI walks
therefore fall back to the main session, which **forfeits the cold-context guarantee** that makes
the whole method work — the main session already knows everything the walker is supposed not to.

**Why this matters more than it looks:** web UI is the surface where this plugin should be
strongest, and it is the surface where the instrument is weakest. The documented fallbacks —
holding one persona at a time yourself, or handing the agent screenshots and page text instead of a
URL — are both weaker than a genuinely cold walk.

**How to test it:** compare a main-session persona walk against a `novice-walker` run over the same
target's static artifacts. If the main-session walk finds materially fewer stalls, the self-audit
bias is confirmed and the screenshot handoff is the better path.

## Deliberately out of scope

| Not here                                                     | Why                                                                                                                                            |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Real user testing, interviews, diary studies, usability labs | This plugin is a proxy for those, not a replacement. It says so in every report                                                                |
| WCAG conformance, contrast ratios, ARIA, focus management    | `ceh-web-frontend:make-ui-accessible` owns the mechanical floor                                                                                |
| Layout, hierarchy, spacing, theme, visual polish             | `ceh-web-frontend:design-ui`, at build time                                                                                                    |
| A/B tests, funnel analytics, session replay, heatmaps        | Needs production traffic and instrumentation, not a coding-session moment                                                                      |
| Localization and internationalization review                 | A tooling and translation-pipeline investment; no in-session trigger                                                                           |
| Information architecture for a whole product                 | A design exercise, not an audit. `ceh-coding-agent:document-architecture` for structure, `ceh-web-frontend:design-ui` for navigation placement |
| Marketing copy, landing-page conversion, SEO wording         | `ceh-seo:pitch-project`                                                                                                                        |
