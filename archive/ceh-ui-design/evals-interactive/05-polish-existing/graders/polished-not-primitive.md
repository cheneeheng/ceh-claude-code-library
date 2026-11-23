---
type: llm
focus: { source: file, path: dashboard.html }
weight: 1
---

The input page had: a purple gradient background, centered body text, everything in translucent boxes, emoji nav icons, two equal blue buttons, a redundant "Dashboard" h1, and a raw bordered table with a "#" column, plain-text status, and a "Failed" column showing zeros. Judge the polished page markup and its page-specific styles. Pass only if every claim holds:

1. All four projects (Website redesign, Billing migration, Mobile app v2, Data warehouse) with their owners are still present.
2. Exactly one primary (filled) button; the other action is outline, ghost, or a link.
3. Body text and the table are left-aligned; the page body is not centered.
4. No gradient background and no translucent/glass boxes.
5. Status is shown as coloured pills or badges, not plain text, and the "#" integer column is gone or turned into words.
6. Zero failure counts are not shown as "0" (omitted or shown as a dash); nonzero failures are worded and coloured as failures.
7. The lone "Dashboard" h1 is either removed (replaced by a section label above the table) or given added information (a count, date, or scope).
8. The nav marks the current item (Dashboard) as active.
