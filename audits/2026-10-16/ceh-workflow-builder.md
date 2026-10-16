# Model audit: ceh-workflow-builder

- Date: 2026-10-16
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-workflow-builder.doctor.md](ceh-workflow-builder.doctor.md).

## Kept changes

### plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/SKILL.md:31
- **Rule:** 4 (a missing statement of when the task is done, added to the file's opening). It is also backed by the general page under rule 1.
- **Backing:** "Be specific about the desired output format and constraints." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, "Be clear and direct"). The same page's research section says "Provide clear success criteria". The opening gives two build modes but never says what finished looks like. That only appears in the Final checklist at line 338 and the Stop conditions at line 358.
- **Change:** insert after the "Two build modes" paragraph.
  - Before: *(nothing; the paragraph ends "The emitted workflow runs in both modes.")*
  - After: add a new paragraph: "The build is done when the user has agreed to the file list, the files are written under `.claude/skills/`, and the Final checklist items that apply to the output pass. A headless build is done when the draft and `QUESTIONS.md` are written to `<build-dir>/<name>-draft/`."

### plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/SKILL.md:26
- **Rule:** 4 (negative instruction rewritten as the positive it implies). It is also backed by the general page under rule 1.
- **Backing:** "Tell Claude what to do instead of what not to do" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, "Control the format of responses"). Sonnet 5 adds "Positive examples ... tend to be more effective than negative examples or instructions that tell the model what not to do." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5, "Response length and verbosity"). The positive form says the same thing, since the `fallback` rules at lines 129 and 270-273 cover availability, not portability.
- **Change:**
  - Before: "Target runtime is Claude Code only. Do not water the output down for portability."
  - After: "Target runtime is Claude Code only. Use its capabilities directly."

### plugins/standalone/ceh-workflow-builder/skills/interview-workflow-task/SKILL.md:122
- **Rule:** 4 (negative instruction rewritten as the positive it implies). It is also backed by the general page under rule 1.
- **Backing:** "Tell Claude what to do instead of what not to do" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, "Control the format of responses"). The reason ("The consumer gates on them by name") stays in place.
- **Change:**
  - Before: "Fixed headings, in this order, one per question. The consumer gates on them by name, so do not add, rename, reorder, or drop one — an unanswered question keeps its heading and says so underneath."
  - After: "Fixed headings, in this order, one per question. The consumer gates on them by name, so keep all nine as written and in this order — an unanswered question keeps its heading and says so underneath."

### plugins/standalone/ceh-workflow-builder/skills/interview-workflow-task/SKILL.md:18
- **Rule:** 4 (cuts a clause whose deletion changes nothing the model does).
- **Backing:** "Kept changes must cut prose that changes no behavior" is the rule's own wording. "The nine questions are not a formality" gives the model no action. The next sentence carries the reason that does: questions 8 and 9 are the ones people skip, and why. Fable 5 supports trimming this kind of text: "Review and consider removing older instructions if default performance is better." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5, "Recommended scaffolding changes"). Under rule 4 the cut stands without that quote, so no other model is affected.
- **Change:**
  - Before: "The nine questions are not a formality. Questions 8 and 9 are the two people skip, and they are the two whose absence corrupts data or sends mail twice."
  - After: "Questions 8 and 9 are the two people skip, and they are the two whose absence corrupts data or sends mail twice."

No other changes survived. The `/doctor` report's empty diff holds for everything else. I found no pressure language, no missing files, and no contradictions between the two skills. I left the unverified `/workflow-authoring` version claim at `SKILL.md:201` and the `enableWorkflows` key at `SKILL.md:223-224` alone, as the report did. None of the guides speaks to either one.
