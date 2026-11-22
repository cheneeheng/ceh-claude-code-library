---
type: regex
pattern: 'topic: Persistence\n\s+choice: \|\n(?:(?!\n    reason:)[\s\S])*postgres'
flags: i
target:
  source: file
  path: .agents_workspace/product/ARCHITECTURE.yaml
---
