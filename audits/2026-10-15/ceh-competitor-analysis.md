# Model audit: ceh-competitor-analysis

- Date: 2026-10-15
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-competitor-analysis.doctor.md](ceh-competitor-analysis.doctor.md).

## Kept changes

### plugins/standalone/ceh-competitor-analysis/agents/competitor-analyst.md:48
- **Rule:** 2. The report also flags this line as a numeric output ceiling.
- **Backing quote:** "Match the length of written documents to what the task needs: cover the substance, but do not pad with filler sections, redundant summaries, or boilerplate." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5). The Fable 5 guide adds: "The way to keep output short is to be selective about what you include (drop details that don't change what the reader would do next)" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5).
- **Models benefited:** Opus 5 and Fable 5. The fact sheet is a written deliverable that tends to run long, and a selection rule steers it better than a line count.
- **Why the others are unaffected:** The Opus 5.5, Sonnet 5, Sonnet 5.5 and Fable 5.1 guides say nothing about line caps or this kind of selection instruction. The Sonnet 5 guide says only that length is calibrated to task complexity. The "never paste file contents back" rule and the per-component coverage rows stay.
- **Change:**
  - Before:
    ```
    Lead with the identity table. Stay under about 150 lines plus one coverage row per component. Never
    paste file contents back. Point at them instead. This agent exists to keep a large competitor out of
    the caller's context, so a long reply defeats it.
    ```
  - After:
    ```
    Lead with the identity table, then one coverage row per component. Never paste file contents back.
    Point at them instead. This agent exists to keep a large competitor out of the caller's context, so
    keep every other section to what the parent needs to rate and verify.
    ```

### plugins/standalone/ceh-competitor-analysis/agents/competitor-analyst.md:23
- **Rule:** 3. This fixes two instructions that contradict each other.
- **Backing:** No quote is needed for a model-independent defect. Line 23 says to flag missing inputs "in your first line". Line 48 says to "Lead with the identity table". Both cannot be the first line.
- **Change:**
  - Before: `If any of these is missing, say so in your first line and work with what you have.`
  - After: `If any of these is missing, say so under "Not read / gaps" and work with what you have.`

### plugins/standalone/ceh-competitor-analysis/agents/competitor-analyst.md:12
- **Rule:** 4. This adds a missing statement of when the task is done, placed in the file's opening.
- **Backing:** None is needed under rule 4. The agent's opening gives no completion condition, while both skills state "Done means …" in theirs. The condition comes from the agent's own Process step 5 and Hard rules.
- **Change:**
  - Before:
    ```
    Everything you return must point at the file, URL, or command it came from.
    ```
  - After:
    ```
    Everything you return must point at the file, URL, or command it came from. You are done when every
    component you listed has a coverage rating and every row carries a path, URL, or command.
    ```

### plugins/standalone/ceh-competitor-analysis/agents/competitor-analyst.md:27
- **Rule:** 1. This agent makes many independent Read, Grep, Glob and Bash calls while mapping a repo, so a parallel-calls rule fits its task.
- **Backing quote:** "Claude's latest models run independent tool calls in parallel... Read several files at once to build context faster" and "If you intend to call multiple tools and there are no dependencies between the tool calls, make all of the independent tool calls in parallel." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, "Optimize parallel tool calling").
- **Fable 5.1 note:** The Fable 5.1 guide (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1) says it may issue independent calls "one per turn" in coding loops, so the line helps there. No guide says it hurts any model.
- **Change:**
  - Before: `1. **Map the structure.** For a repo, read the README, the manifests (...`
  - After: add one sentence at the start of Process: `Issue independent reads, greps, and counts in the same turn, and call sequentially only when a call needs a previous result.` Step 1 stays as is.

### plugins/standalone/ceh-competitor-analysis/README.md:21
- **Rule:** 3. This fixes a stale claim that contradicts the skill descriptions. It also covers the same fix at lines 40-41, as the report proposes.
- **Backing:** None is needed. The README lists auto-trigger phrases ("how does X compare to us", "study this competitor", "a pasted GitHub URL with 'investigate'", "comparison report", "master report", "side by side with our work") that appear in neither skill's `description`. The description is what the router reads.
- **Change (line 21):**
  - Before:
    ```
    **Auto-triggers on:** "competitor analysis", "analyze this repo", "what can we learn from X", "how
    does X compare to us", "study this competitor", or a pasted GitHub URL with "investigate".
    ```
  - After:
    ```
    **Auto-triggers on:** "competitor analysis", "analyze this repo", "what can we learn from X".
    ```
- **Change (line 40):**
  - Before:
    ```
    **Auto-triggers on:** "compare them with us", "comparison report", "master report", "how do we
    stack up", "side by side with our work".
    ```
  - After:
    ```
    **Auto-triggers on:** "compare them with us", "how do we stack up", or after several competitors
    were analysed.
    ```
