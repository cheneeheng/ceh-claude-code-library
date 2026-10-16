# Model audit: ceh-workflow-runner

- Date: 2026-10-16
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-workflow-runner.doctor.md](ceh-workflow-runner.doctor.md).

## Kept changes

### plugins/standalone/ceh-workflow-runner/skills/run-agentic-workflow/SKILL.md:184-185
**Rule 3.** This is a model-independent contradiction. The `/doctor` report also proposes it (finding 2).

**Backing quote:** None needed. The file contradicts itself. Step 1 is the config check, step 2 is the input check and step 3 is the capability check. A stop that ends "before step 1" cannot cover failures raised inside those steps. The schema doc agrees, saying "A failure before any stage runs (config, preflight, inputs) uses `-` for the stage id" (`references/flow-config-schema.md:225`).

**Before:**
```
- The config fails a validation rule, an input is missing or a capability is absent → end before
  step 1 with `FLOW STATUS: failed - <reason>`.
```
**After:**
```
- The config fails a validation rule, an input is missing or a capability is absent → end before
  any stage runs with `FLOW STATUS: failed - <reason>`.
```
The report's diff drops "before" and reads "end any stage runs". Keep "before", as shown above.

### plugins/standalone/ceh-workflow-runner/skills/run-agentic-workflow/SKILL.md:71-72
**Rule 3.** This is a model-independent contradiction, and the report flagged it without fixing it (flagged item 1). Line 72 calls the world check "the stage's first action". Steps 5.1 (`reads` check) and 5.2 (approval) come before it in the same list. The rewrite removes the contradiction and keeps the step order as written. It does not pick a new order, so it does not settle the question the report left to the user.

**Backing quote:** None needed. "First action" and the numbered order of 5.1, 5.2 and 5.3 cannot both hold.

**Before:**
```
3. **World check.** If `unsafe_to_rerun`, evaluate `world_check` now, on every attempt and every
   resume. It is the stage's first action, ahead of the run state, because state is only a record.
```
**After:**
```
3. **World check.** If `unsafe_to_rerun`, evaluate `world_check` now, on every attempt and every
   resume. It runs before dispatch and ahead of the run state, because state is only a record.
```

### plugins/standalone/ceh-workflow-runner/skills/run-agentic-workflow/SKILL.md:168
**Rule 4.** A negative instruction is rewritten as the positive one it implies. Both say the same thing, since asking is allowed only through the approval path.

**Backing quote:** "Tell Claude what to do instead of what not to do" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices). That passage is about output formatting, but it states the general principle.

**Before:**
```
- **Do not stop to ask in headless mode,** except through the approval path above.
```
**After:**
```
- **In headless mode, ask only through the approval path above.**
```

---

Nothing else survived:

- **No new model-guide change.** The Fable 5, Fable 5.1, Opus 5, Opus 5.5, Sonnet 5 and Sonnet 5.5 guides add nothing that fits this skill. It is a deterministic runner with explicit, reasoned rules, with no verification or double-check instructions to remove and no capitalised emphasis.
- **The report's other flagged item.** The broken code span at `SKILL.md:51-53` is a formatting artifact, not a missing reference or a contradiction, so no rule covers it.
- **The duplicated "Never imitate" rule** (`:52`, `:113-115`, `:165`). The report keeps it as working redundancy, and I follow the report.

I did not read `fable-5-1` in full (the fetch was truncated). Its listed sections are progress updates, batching, task completion, scope and subagents, which don't apply to this skill.
