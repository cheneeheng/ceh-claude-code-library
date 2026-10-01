# ceh-lessons-learned

Claude Code plugin for extracting and recording session retrospectives. Reviews the conversation,
identifies mistakes and corrections, and appends structured lessons to `LESSONS_LEARNED.md`.

## Skill

| Skill             | Description                                                                                   |
| ----------------- | --------------------------------------------------------------------------------------------- |
| `lessons-learned` | Extract lessons from the current session and append to `.agents_workspace/LESSONS_LEARNED.md` |

Invoke manually:

```
/ceh-lessons-learned:lessons-learned
```

Or load automatically when you say:

- `"extract lessons learned"`
- `"do a retrospective"`
- `"capture what went wrong"`
- `"write up lessons learned"`

Also triggers proactively at the end of a session that involved notable errors or rework.

## What Gets Captured

| Category                   | Example                                            |
| -------------------------- | -------------------------------------------------- |
| Corrections                | User had to ask for a redo, rename, or restructure |
| Failed commands            | Tool call errored and required a follow-up fix     |
| Misunderstood requirements | Built in the wrong place, format, or scope         |
| Wrong assumptions          | Assumed something that turned out to be false      |
| Sequencing mistakes        | Steps done out of order or prerequisite skipped    |

**Not captured:** things that worked correctly, routine tool use, or preference changes that
weren't errors.

## Output

Each lesson appended to `.agents_workspace/LESSONS_LEARNED.md`:

```markdown
## YYYY-MM-DD — <short title describing the mistake>

**What happened:** Concrete mistake or misunderstanding.

**Lesson:** Actionable rule to apply next time.
```

The file is created with a header if it does not exist.
