# Personas and severity

Shared by `simulate-newcomer-first-run` and `audit-interface`. Both dispatch walkers under these personas and
rank what the walkers report on this scale.

## The personas

Five constraints, each catching a distinct failure class. Pass the constraint to the walker
verbatim.

| Persona               | Holds this constraint the whole way                                                                                                                                                                                           | Catches                                                                                                  |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Blank Slate**       | Knows the audience baseline and nothing beyond it — no domain vocabulary, no prior knowledge of this product. Reads only what is on the screen or page. Assumes nothing is safe to click until told. _(the 5-year-old proxy)_ | Undefined jargon, invisible affordances, "obvious" next steps that are not, assumed prerequisites        |
| **Cautious Returner** | Will not take any action whose outcome is not stated in advance. Needs to see what happened after every action. Afraid of losing work. _(the 95-year-old proxy)_                                                              | Missing confirmation, silent success, irreversible actions, no undo, no way to check state               |
| **Interrupted**       | Leaves for ten minutes mid-task and may close the tab or terminal. Comes back and must resume.                                                                                                                                | Lost state, expired sessions/tokens, multi-step flows with no progress marker or resume path             |
| **Wrong Turn**        | Does the wrong thing first — wrong button, wrong value, skips a required step — then tries to recover.                                                                                                                        | Dead ends, unrecoverable errors, blame copy, no back, validation that fires too late                     |
| **Small Screen**      | 360px viewport, slow link, or an 80-column terminal. Keyboard only.                                                                                                                                                           | Offscreen primary action, layout collapse, hover-only affordances, no loading feedback, truncated output |

`Small Screen` covers the _environment_, not conformance. WCAG mechanics — contrast ratios, ARIA,
focus traps — belong to `ceh-web-frontend:make-ui-accessible`; delegate rather than re-deriving
them, and say in the report that you did.

## Severity

Severity comes from what actually happened to a walker, never from how bad something looks to the
auditor.

| Severity     | Assigned when                                                                                                |
| ------------ | ------------------------------------------------------------------------------------------------------------ |
| **Blocker**  | A persona could not complete the goal — or completed it wrongly believing it was right                       |
| **Detour**   | Completed it, but only after backtracking, guessing between options, or looking outside what they were given |
| **Friction** | Completed it, but with avoidable doubt — "did that work?"                                                    |
| **Polish**   | No effect on any walker's completion                                                                         |
