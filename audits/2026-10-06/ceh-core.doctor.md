| Topic         | Outcome                                                                                                | Status                                                           |
| ------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Audit result  | No high or medium findings in `plugins/standalone/ceh-core`. The surface is clean against its targets. | inferred, from reading and `git blame`, no behavioral probes run |
| Flags         | Four low-confidence items, listed below, none worth an edit.                                           | inferred                                                         |
| Proposed diff | Empty. The guide says an audit that finds nothing should change nothing.                               | done                                                             |

**Assumptions**

- **Scope:** `skills/delegate-bulk-reads/SKILL.md`, `skills/usage-limit-handoff/SKILL.md`, `agents/bulk-reader.md`, `README.md`, and the message text in the three hook scripts. I did not read `hooks/hooks.json` or `plugin.json`, because the guide says hook definitions can hold secrets. I did not read the `__pycache__` files.
- **Targets:** The skills, the README and the script messages are audited against Sonnet 5.5, the model running this audit. `bulk-reader.md` pins `model: haiku`, so it is audited against Haiku 4.5.
- **Provenance:** Every audited line was written between 2026-09-30 and 2026-10-01 (`git blame`). Nothing there is left over from an earlier model generation.

**Audit result**

- **Pressure language (1a):** none. The only emphasis is `do NOT write a handoff file` in `usage-limit-watch.py:181`, and the skill states the same rule with its reason at `usage-limit-handoff/SKILL.md:23-24`.
- **Scaffolds replaced by API features (1b):** none. There is no think-step-by-step text, no prefill, no numeric output caps and no progress-update choreography.
- **Prohibitions (1e):** the bulk-reader's prohibitions mostly carry a reason or encode a contract. Examples are the anchor rules, `Do not infer beyond the text`, and the read-only rule that `tools: Read, Grep, Glob` backs up.
- **Group 3:** not applicable, there are no tool definitions.
- **Group 4:** not applicable, there is no request-building code.
- **Counts:** Group 1 has 0 findings, Group 2 has 4 low flags, Groups 3 and 4 are not applicable.
- **Facts checked against the repo:**
  - The 350-line threshold and the `CEH_USAGE_LIMIT_THRESHOLD` default of 90 match the scripts.
  - The 5-point re-fire and the stale-reading default of 15 minutes match.
  - Every script path the README names exists.
  - The skill names it uses (`ceh-core:delegate-bulk-reads`, `ceh-core:usage-limit-handoff`) are the ones in the plugin.

**Flags**

1. `README.md:84` against `delegate-bulk-reads/SKILL.md:25-30` — Group 2 conflict, low confidence. The README says delegation costs more than it saves "below roughly 200" lines. The skill says the same about "under roughly 400". The README is newer, but it is human-facing docs, not an instruction file. The user has to pick the break-even figure, so no edit is proposed.
2. `README.md:15` — Group 2 stale fact, low confidence. It says the skill covers "never ask it to edit", but the skill has no such sentence. The read-only rule lives in `bulk-reader.md:89-90`. A README fix would be a one-phrase rewrite, left out because the README is not read by the model.
3. `delegate-bulk-reads/SKILL.md:16-21` — History narrative, low confidence. "Measured over six runs against the agent-skills repo... roughly 60% to 25%" is an undated measurement tied to `haiku`. It is also the reason for the rule `Do not override the worker's model`, so keeping it is defensible. Consider adding a date so it can be re-checked when the `haiku` alias moves.
4. `bulk-reader.md:85-86` — Style prohibition without a stated reason, low confidence. `Do not editorialize` overlaps Process step 2, "Answer only the question asked". No transcript shows Haiku 4.5 violating it, so I have no failure evidence either way. Removing it would be a guess, not a finding.

Dependency risk: none found. The README and skills cite each other consistently. The one external dependency is the unprobed `agent-skills` eval link.
