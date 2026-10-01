# ceh-summarize-chat

Claude Code plugin for producing structured session summaries for LLM handoff. Compresses the
current conversation into a concise markdown document a future session can act on immediately.

## Skill

| Skill            | Description                                                               |
| ---------------- | ------------------------------------------------------------------------- |
| `summarize-chat` | Summarize the current session into a structured markdown handoff document |

Invoke manually:

```
/ceh-summarize-chat:summarize-chat
```

Or load automatically when you say:

- `"summarize the chat"`
- `"summarize the conversation"`
- `"create a session summary"`
- `"summarize what we did"`

## Output Structure

The summary is a markdown document covering only the sections that apply:

| Section                    | Contents                                      |
| -------------------------- | --------------------------------------------- |
| Goal                       | What the user was trying to accomplish        |
| What Was Done              | Ordered list of actions taken                 |
| Decisions Made             | Naming, locations, approaches chosen          |
| Problems and Solutions     | Non-obvious issues and how they were resolved |
| Current State              | Files created, modified, or deleted           |
| Pending / Next Steps       | Work discussed but not completed              |
| Key Facts for Next Session | Gotchas to avoid repeating                    |

**Current State** and **Key Facts** are the most important sections — a future LLM needs to know
exactly what exists and what tripped up the current session.
