---
type: llm
focus: trace
weight: 1
---

Judge the assistant's final answer plus any file it wrote (the content of its Write or Edit tool calls). Ignore the session's start-up listing of tools and skills. Pass only if every claim holds:

1. The answer gives a FastAPI GET endpoint that returns a list of orders.
2. It takes pagination parameters (limit/offset, page/size, or a cursor) with defaults.
3. The page size has an upper bound (e.g. Query(le=100)) or the answer explicitly caps it.
4. The answer contains no UI, layout, theme, colour, or visual-design advice.
