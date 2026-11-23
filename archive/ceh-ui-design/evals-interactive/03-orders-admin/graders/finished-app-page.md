---
type: llm
focus: { source: file, path: orders.html }
weight: 1
---

Judge the page markup and its page-specific styles. Pass only if every claim holds:

1. A sidebar holds the nav, and exactly one item (Orders) is visibly marked active (an active class such as is-active, and/or aria-current).
2. Exactly one primary (filled) button is visible in any one state of the page; every other visible button is outline, ghost, or a link. A primary button inside an empty-state template that only shows when it replaces the table counts as a different state.
3. Each order's status is a coloured pill or badge, not plain text, and the four statuses use different colours.
4. The table sits inside a panel, with a section label and count (e.g. "ORDERS · 12") above the panel, not inside it.
5. Empty, loading (skeleton rows or blocks, not a full-page spinner), and error states exist in the markup, even if hidden by default.
6. Table cells can wrap: the delivery note column is not forced to a single line, and the table is not set to scroll sideways at desktop width.
7. No emoji icons, no gradient hero, and no large standalone "Orders" page title that only repeats the active nav item. A heading styled as a small section label with a caption or a count adds information and passes.
