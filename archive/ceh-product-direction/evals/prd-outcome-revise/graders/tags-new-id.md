---
type: regex
pattern: '- id: F0[5-9]\n\s+name: [^\n]*tag'
flags: i
target:
  source: file
  path: .agents_workspace/product/PRD.yaml
---
