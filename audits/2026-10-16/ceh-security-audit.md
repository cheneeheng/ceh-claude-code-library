# Model audit: ceh-security-audit

- Date: 2026-10-16
- claude-code 2.1.301
- Edits applied: no
- WARNING: 1 tool call(s) were denied, so the report may be incomplete.

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-security-audit.doctor.md](ceh-security-audit.doctor.md).

## Kept changes

### plugins/standalone/ceh-security-audit/skills/audit-codebase-security/SKILL.md:33

**Rule:** 1, and 2 for Fable 5.1.

**Backing quotes:**
- General page, "Optimize parallel tool calling" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices): "This behavior is steerable. While the model has a high success rate in parallel tool calling without prompting, you can boost this to ~100%". Step 2 makes many independent searches and file reads, one per entry point and category, so the file's task shows the need.
- Fable 5.1 guide (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1): "in coding and computer-use loops where the next independent calls are implied by the task rather than explicitly requested… it may issue them one per turn instead… each extra turn costs tokens, a round trip, and wall-clock time."

**Models:**
- Benefits: Fable 5.1.
- Unaffected: Fable 5, Opus 5, Opus 5.5, Sonnet 5 and Sonnet 5.5. Their guides are silent on batching, and the general page says parallel calling already works for all current models.

**Change:**
- Before: `2. **Trace each entry point to its sinks**: queries, shell commands, file paths, HTML and templates, outbound requests, deserializers, `eval`. Check each category, and name the ones that do not apply:`
- After: `2. **Trace each entry point to its sinks**: queries, shell commands, file paths, HTML and templates, outbound requests, deserializers, `eval`. Request every search and file read that does not depend on another's result in the same turn. Check each category, and name the ones that do not apply:`

### plugins/standalone/ceh-security-audit/skills/audit-codebase-security/SKILL.md:72

**Rule:** 4. The deletion changes nothing the model does.

**Backing quote:** None needed beyond rule 4. Step 5 already says the same thing, in the same file at lines 57 to 61: "quoting both ends… A finding you cannot trace goes under Possible, not in the table."

The `/doctor` report does not cover this bullet. It keeps only the Rules bullets that carry a reason, such as the "committed audit of an unfixed hole" one. This bullet has no reason, so the report doesn't conflict with cutting it.

**Change:**
- Before: `- **Quote or suppress.** A finding without quoted code at both ends goes under Possible.`
- After: (bullet deleted)

I did not keep these:
- **Reasoned prohibitions.** The "Never copy a secret's value" and "Prove locally, never live" bullets stay, per the report.
- **Subagent fan-out step.** It already limits delegation to large surfaces and gives each subagent its inputs, so the Opus 5 spawn-cap guidance is met. A "keep working while they run" line would benefit only Fable and would invent work for the lead agent.
- **Verification line.** The "re-read every quoted line" instruction stays. It is part of confirming a finding, and Sonnet 5.5 favors verification while Opus 5 only objects to generic double-check wording.
