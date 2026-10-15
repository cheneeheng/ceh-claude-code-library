# Model audit: ceh-build-planning

- Date: 2026-10-15
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-build-planning.doctor.md](ceh-build-planning.doctor.md).

## Kept changes

### plugins/standalone/ceh-build-planning/skills/write-build-plan/SKILL.md:84
Rule 1 (general page).

Backing quote: "Tell Claude what to do instead of what not to do" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices). Rule 4 also covers it, because the positive form says the same thing.

- Before: `- Write no file besides the plan.`
- After: `- Write only the plan file.`

### plugins/standalone/ceh-build-planning/skills/write-build-plan/SKILL.md:83
Rule 1 (general page), the same backing as above. Rule 4 also covers it.

Backing quote: "Tell Claude what to do instead of what not to do" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).

- Before: `- One plan per request. Never rewrite a \`built\` plan: new work gets a new plan file.`
- After: `- One plan per request. Leave a \`built\` plan as written: new work gets a new plan file.`

### plugins/standalone/ceh-build-planning/skills/review-build-plan/SKILL.md:66
Rule 1 (general page). Rule 4 also covers it, because the second sentence already carries the positive instruction.

Backing quote: "Tell Claude what to do instead of what not to do" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).

- Before:
  ```
  - Ask the user nothing during the review. A question only the plan's owner can answer becomes a
    finding with a recommended answer.
  ```
- After:
  ```
  - During the review, turn a question only the plan's owner can answer into a finding with a
    recommended answer.
  ```
