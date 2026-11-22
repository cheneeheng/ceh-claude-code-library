---
type: regex
pattern: '- id: F02\n[\s\S]*?status: planned\n\s+plans:\n\s+- \.agents_workspace/product/plan/20261011-140000-search\.yaml'
target:
  source: file
  path: .agents_workspace/product/PRD.yaml
---
