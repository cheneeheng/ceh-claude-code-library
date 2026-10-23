# Model audit: ceh-build-planning

- Date: 2026-10-23
- claude-code 2.1.309
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, haiku-5-5, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-build-planning.doctor.md](ceh-build-planning.doctor.md).

## Kept changes

### plugins/standalone/ceh-build-planning/README.md:16

- **Rule:** 3, a model-independent defect: the README and the skill contradict each other.
- **Backing:** No guide page applies, so there is no URL. The `/doctor` report found it at `audits/2026-10-23/ceh-build-planning.doctor.md:20-23`. The README says "It's working if the reply opens with `Plan review:` and a verdict, and names any lens it skipped." `review-build-plan/SKILL.md:81` says "Reply with the verdict, the blocking findings, and the path." `Plan review:` appears only as the heading inside the saved file (`plan-review.template.md:8`). The lens-skip note goes into the saved review, not the reply.
- **Change:** follow the report. The skill defines the behavior, so the README changes to match it.
- **Before:** `... Report-only unless asked to fix. It's working if the reply opens with `Plan review:` and a verdict, and names any lens it skipped.`
- **After:** `... Report-only unless asked to fix. It's working if it saves `.agents_workspace/plan-reviews/<slug>-<date>.md` and the reply gives the verdict, the blocking findings, and that path.`

### plugins/standalone/ceh-build-planning/skills/review-build-plan/SKILL.md:51

- **Rule:** 3, a model-independent defect: two instructions in one step contradict each other. The report missed this.
- **Backing:** No guide page applies, so there is no URL. Line 51 says the review "always appends one Reviewed line to the plan's `## Record`". Lines 52-53 say "A spec that is not a plan gets no Record line." A spec review is a path the skill itself defines at step 1.
- **Change:** drop "always" so the exception no longer contradicts the rule.
- **Before:** `It always appends one Reviewed line to the plan's `## Record` (format in the plan format file), so the review stays part of the plan's trail.`
- **After:** `It appends one Reviewed line to the plan's `## Record` (format in the plan format file), so the review stays part of the plan's trail.`
