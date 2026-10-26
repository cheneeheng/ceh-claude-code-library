---
type: regex
pattern: '### Phase 2: Length limit[\s\S]*?\*\*Status:\*\* todo'
flags: m
target:
  source: file
  path: product/plans/slug.md
---
