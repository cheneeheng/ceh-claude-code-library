---
type: llm
focus: trace
weight: 1
---

Judge the assistant's final answer plus any file it wrote (the content of its Write or Edit tool calls). Ignore the session's start-up listing of tools and skills. Pass only if every claim holds:

1. The answer identifies that `() => save` returns the function without calling it, so nothing runs on click.
2. The fix is `onClick={save}` or `onClick={() => save()}` (either is fine).
3. The answer does not restyle the button or give layout, theme, or visual-design advice.
