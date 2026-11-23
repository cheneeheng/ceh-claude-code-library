---
type: llm
focus: { source: file, path: index.html }
weight: 1
---

Judge the page markup and its page-specific styles. Pass only if every claim holds:

1. A horizontal top nav with at most 5 links; no sidebar.
2. Full-width sections below the nav covering about, menu highlights, opening hours, location, and order online.
3. Ordering is the one primary (filled) action: every filled button on the page leads to or completes ordering (e.g. a hero "Order" button plus the order form's submit button), with at most one per section. All other links and buttons are outline, ghost, or plain links.
4. No glassmorphism, and no gradient or brand-colour background wash on every section (a single hero treatment at most).
5. No emoji used as icons or bullets.
6. Body text is left-aligned (centering only in the hero, if any), and prose is capped to a readable width.
