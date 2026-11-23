---
type: regex
pattern: 'topic: ["'']?Persistence["'']?$'
flags: mi
match: "count:1"
target:
  source: file
  path: .agents_workspace/product/ARCHITECTURE.yaml
---
