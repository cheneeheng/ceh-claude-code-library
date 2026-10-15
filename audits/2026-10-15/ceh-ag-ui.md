# Model audit: ceh-ag-ui

- Date: 2026-10-15
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-ag-ui.doctor.md](ceh-ag-ui.doctor.md).

## Kept changes

### plugins/standalone/ceh-ag-ui/skills/build-ag-ui-agent/SKILL.md:19
Rule 4. A done statement was missing from the opening.
Backing: "End your turn only when the task is complete or you are blocked on input only the user can provide." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1). This is the rule 4 cue, not a rule 2 claim.
- Before: the opening paragraph ends "...or running a tool that belongs to the canvas." and nothing says when the skill is finished.
- After: add "The work is done when every check in Procedure step 3 passes." as the closing sentence of that paragraph.

### plugins/standalone/ceh-ag-ui/skills/add-human-approval/SKILL.md:17
Rule 4. A done statement was missing from the opening.
Backing: "When the work the user asked for is done and checked, stop and report." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5)
- Before: the opening paragraph ends "...and the agent acts only on that." and nothing says when the skill is finished.
- After: add "The work is done when the five checks in step 3 pass." as the closing sentence of that paragraph.

### plugins/standalone/ceh-ag-ui/skills/add-live-state-panel/SKILL.md:17
Rule 4. A done statement was missing from the opening.
Backing: "When the work the user asked for is done and checked, stop and report." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5)
- Before: the opening paragraph ends "...and one fixed panel on the canvas renders it." and nothing says when the skill is finished.
- After: add "The work is done when the three checks in step 5 pass." as the closing sentence of that paragraph.

### plugins/standalone/ceh-ag-ui/skills/add-canvas-component/SKILL.md:17
Rule 4. A done statement was missing from the opening.
Backing: "When the work the user asked for is done and checked, stop and report." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5)
- Before: the opening paragraph ends "...or ends up controlling how it looks." and nothing says when the skill is finished.
- After: add "The work is done when the five checks in step 3 pass and `bun run typecheck` is clean." as the closing sentence of that paragraph.

### plugins/standalone/ceh-ag-ui/skills/build-ag-ui-agent/SKILL.md:105
Rule 1, and rule 4 as well (negative rewritten as its positive).
Backing: "Tell Claude what to do instead of what not to do" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Before: "Track which kind of block each index is. Never guess it from an id prefix."
- After: "Take each index's block kind from its `content_block_start` event."

### plugins/standalone/ceh-ag-ui/skills/add-live-state-panel/SKILL.md:154
Rule 1, and rule 4 as well (negative rewritten as its positive).
Backing: "Tell Claude what to do instead of what not to do" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Before: "Do not put a fast-changing panel inside an `aria-live` region."
- After: "Keep a fast-changing panel outside any `aria-live` region."

### plugins/standalone/ceh-ag-ui/skills/add-human-approval/SKILL.md:221
Rule 1, and rule 4 as well (negative rewritten as its positive).
Backing: "Tell Claude what to do instead of what not to do" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Before: "Do not make it `role=\"alert\"` unless the run truly cannot continue without it."
- After: "Use `role=\"alert\"` only when the run truly cannot continue without it."

I made no edits. Nothing else survived the filter, and I did not open the `main.py` and `pyproject.toml` the report covers, so these changes rest on the report for them.
- **Report's low-confidence flags:** I left all four out. The `main.py` output ceiling is a product requirement. The "Current Claude models reject `any` and `tool`" wording is wording only. The `anthropic>=1.9` pins are unverified. The per-run `tools` rebuild is by design.
- **Model-specific prompt additions:** I added none. The skills are reference procedures with no tool loop of their own, so the parallel-calls, progress-update, and over-verification sections do not apply.
