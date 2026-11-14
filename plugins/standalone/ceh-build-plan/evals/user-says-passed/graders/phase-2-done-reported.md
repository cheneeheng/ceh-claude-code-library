---
type: regex
pattern: '### Phase 2: Length limit[\s\S]*?\*\*Status:\*\* done[^\n]*reported by the user, not run by the agent'
flags: m
target:
  source: file
  path: .agents_workspace/product/plans/slug.md
---
