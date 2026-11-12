---
type: regex
pattern: '^- \d{4}-\d{2}-\d{2} Built Phase 2'
flags: m
match: not_contains
target:
  source: file
  path: product/plans/slug.md
---
