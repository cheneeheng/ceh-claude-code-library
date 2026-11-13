---
type: regex
pattern: '^- \d{4}-\d{2}-\d{2} Built Phase 2[^\n]*reported by the user, not run by the agent'
flags: m
target:
  source: file
  path: product/plans/slug.md
---
