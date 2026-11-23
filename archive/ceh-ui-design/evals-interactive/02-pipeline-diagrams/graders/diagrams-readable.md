---
type: llm
focus: { source: file, path: pipeline.html }
weight: 1
---

Judge the page markup, its page-specific styles and scripts. Pass only if every claim holds:

1. Diagrams are Mermaid, and each sits in its own panel next to the text that explains it.
2. Text and diagram panels share one column with one right edge: the prose is NOT held to a narrower cap (such as 65ch) than the diagram panels beneath or beside it.
3. No single diagram has more than about 9 nodes or 12 edges; a larger flow is split into an overview plus detail diagrams.
4. A diagram too wide for its panel scrolls inside the panel; there is no rule that scales diagrams down without a minimum (no fixed transform: scale or width: 100% forcing tiny text).
5. All four stages and their failure paths (test failure stops, staging rollback, 24-hour approval cancel, canary rollback) appear in the text or diagrams.
6. No hero banner, call-to-action button, or emoji icons.
