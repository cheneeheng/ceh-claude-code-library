---
schema: run/v1
---

# <task in a few words>

| Field                        | Value                                 |
| ---------------------------- | ------------------------------------- |
| Started                      | <started>                             |
| Finished                     |                                       |
| Session                      | <session id>                          |
| Transcript                   | <transcript path>                     |
| Project                      | <repo name> (<project root>)          |
| Strategy                     | <plan-then-implement or orchestrate>  |
| Main model                   | <model id this session runs on>       |
| Worker model                 | <haiku, sonnet, opus or fable>        |
| `CLAUDE_CODE_SUBAGENT_MODEL` | <unset or its value>                  |
| Base                         | <sha>, clean or dirty (see base.diff) |
| End                          |                                       |
| Outcome                      |                                       |
| Dispatches                   |                                       |
| User interventions           |                                       |
| Verdict                      |                                       |

## Task

<the user's request, verbatim>

## Plan or briefs

<the skill fills this section>

## Ledger

<filled at close by dispatch_ledger.py>

## Token usage

## Notes
