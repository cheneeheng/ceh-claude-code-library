---
type: regex
pattern: '### Phase 3: Separator[\s\S]*?\*\*Status:\*\* todo'
flags: m
target:
  source: file
  path: .agents_workspace/product/plans/slug.md
---
