# Known weak points

Moved from the plugin README on 2026-11-13. Check these two first when evaluating the plugin.

Both are deliberate design choices, not oversights, and both are the most likely places this plugin
is wrong. Anyone evaluating it should attack them before anything else.

## 1. Severity is assignable only from an observed stall

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

## 2. `newcomer-simulator` cannot drive a browser

Background subagents keep a reduced tool set, so the Chrome tools are stripped. Live web-UI walks
therefore fall back to the main session, which **forfeits the cold-context guarantee** that makes
the whole method work — the main session already knows everything the walker is supposed not to.

**Why this matters more than it looks:** web UI is the surface where this plugin should be
strongest, and it is the surface where the instrument is weakest. The documented fallbacks —
holding one persona at a time yourself, or handing the agent screenshots and page text instead of a
URL — are both weaker than a genuinely cold walk.

**How to test it:** compare a main-session persona walk against a `newcomer-simulator` run over the same
target's static artifacts. If the main-session walk finds materially fewer stalls, the self-audit
bias is confirmed and the screenshot handoff is the better path.
