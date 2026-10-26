---
type: regex
pattern: '### Phase 3: Separator[\s\S]*?\*\*Status:\*\* todo'
flags: m
target:
  source: file
  path: product/plans/slug.md
---
