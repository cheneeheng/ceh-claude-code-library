# Model audit: ceh-session-to-skill

- Date: 2026-10-16
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-session-to-skill.doctor.md](ceh-session-to-skill.doctor.md).

## Kept changes

### plugins/standalone/ceh-session-to-skill/skills/turn-session-into-skill/SKILL.md:56
**Rule 1** (general page).

Backing quote, from https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices: "**Tell Claude what to do instead of what not to do** … Instead of: 'Do not use markdown in your response' · Try: 'Your response should be composed of smoothly flowing prose paragraphs.'"

The rule opens with a prohibition ("Add no step, branch, or option…"). The positive form says the same thing, and the reason sentence after it stays as it is.

Before:
```
- **Only what ran.** Add no step, branch, or option this session never exercised. One observed run
  shows one path, and a branch nobody ran is a guess that will mislead the next run.
```
After:
```
- **Only what ran.** Include only steps, branches, and options this session exercised. One observed
  run shows one path, and a branch nobody ran is a guess that will mislead the next run.
```

### plugins/standalone/ceh-session-to-skill/skills/turn-session-into-skill/SKILL.md:16
**Rule 3** (model-independent contradiction), with rule 4 as a fallback.

The opening says "Done when the file exists under `.claude/skills/<name>/`". Step 5 (line 45) says to hand the steps to `ceh-workflow-builder:build-agentic-workflow` "instead of writing the file". The stop conditions (lines 100–103) end the run with no file. A run that follows Step 5 or a stop condition therefore never meets the stated done condition. Rule 4 also covers adding a done statement to the file's opening, and this change makes the existing one complete. No page backs it, so it rests on the contradiction itself.

Before:
```
`.claude/skills/<name>/`, every step in it traces to a step that succeeded in this session, and
the user has the list of what came from where.
```
After:
```
`.claude/skills/<name>/`, every step in it traces to a step that succeeded in this session, and
the user has the list of what came from where. A run that Step 5 hands off, or that a stop
condition ends, is done once the user has been told which and why.
```

---

I considered and left out the four-fold "no interview" repetition (lines 5, 16, 20–22, 63). The `/doctor` report flags it at low confidence and proposes no edit, and the repetition does no harm, so I followed the report. Nothing in the plugin asks the model to reproduce its reasoning, runs independent tool calls that need a parallel-calls rule, or uses pressure language, so none of the model-specific guides add a kept change.
