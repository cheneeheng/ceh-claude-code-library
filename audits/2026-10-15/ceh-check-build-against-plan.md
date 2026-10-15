# Model audit: ceh-check-build-against-plan

- Date: 2026-10-15
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-check-build-against-plan.doctor.md](ceh-check-build-against-plan.doctor.md).

## Kept changes

### plugins/standalone/ceh-check-build-against-plan/skills/check-build-against-plan/SKILL.md:39

- **Rule:** 1, and also 2.
- **Backing quote (rule 1):** "Claude's latest models run independent tool calls in parallel. … While the model has a high success rate in parallel tool calling without prompting, you can boost this to ~100% or adjust the aggression level" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).
- **Why it fits this file:** Step 3 runs one command per phase Check and reads code for many independent plan items. The task shows the need for the technique.
- **Backing quote (rule 2):** "The exception is coding and computer-use loops where the next independent calls are implied by the task rather than explicitly requested … there it may issue them one per turn instead. This doesn't affect answer quality, but each extra turn costs tokens, a round trip, and wall-clock time. A one-sentence nudge … addresses it" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1).
- **Models benefited:** Fable 5.1. The skill's checks are implied by the plan rather than named in the request, which is the case that guide describes.
- **Models unaffected:** The Fable 5, Opus 5, Opus 5.5, Sonnet 5 and Sonnet 5.5 guides say nothing against batching independent calls. The general page says current models already do it, so the line is harmless there.
- **Wording:** The "share no state" clause comes from the general page's warning that parallel bash commands "can even bottleneck system performance". It keeps checks that touch the same database or port running one after another.
- **Before:**
  > Run every phase Check that can run. A phase marked `done` is evidence of when it passed, not that it passes now.
- **After:**
  > Run every phase Check that can run. Start the Checks that depend on no other's result and share no state (a database, a port) in one response, and read the code for independent items the same way. A phase marked `done` is evidence of when it passed, not that it passes now.

No other change survived. I checked each of these against the four rules:

- **Opening "done" statement:** Line 18 already says "Done means every plan item has a status and the report is delivered."
- **Pressure language:** `SKILL.md` has no CAPS, "MUST", or "be thorough" filler to cut.
- **Reviewer step:** The guides give no reason to remove step 5. It runs only on request and its fresh-context reviewers match Fable 5's recommendation.
- **Code-review filtering:** The Opus 5 and Sonnet 5 warnings about "only report high-severity" prompts do not apply. The rule "Judge from the code, not the brief" already reports every finding.
- **Other files:** `README.md` and `references/plan-format.md` need no change. The `/doctor` report found their cited names and the three `plan-format.md` copies consistent.
