---
type: regex
pattern: '^- \d{4}-\d{2}-\d{2} Reviewed: (Revise first|Rethink), [1-9]'
flags: mi
target:
  source: file
  path: .agents_workspace/product/plans/notes-api.md
---
