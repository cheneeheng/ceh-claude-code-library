---
type: llm
focus: { source: file, path: report.html }
weight: 1
---

Judge the page markup and its page-specific styles (ignore the large inlined theme stylesheet itself). Pass only if every claim holds:

1. The page reads as a document: there is no hero banner, no call-to-action button, and no marketing-style section.
2. There is a contents list (rail or list) linking every h2 and h3 heading that exists on the page, with h3 entries indented further than h2 entries. Content restructured into a table or list instead of headings is fine; only headings that exist need links.
3. The section in view is marked in the contents list by script: an IntersectionObserver (or equivalent scroll logic) sets an active class and/or aria-current on the matching link.
4. If the page has a sticky header (a bar across the top), scroll-padding-top or an equivalent offset is set. A sticky contents rail beside the text is not a header and needs no offset.
5. Body text is left-aligned, not centered.
6. No emoji are used as icons or bullets.
7. Sections are not each wrapped in their own card or bordered box; structure comes from headings and whitespace.
8. All report content is present: the five h2 sections, the budget figures, and both decisions needed.
