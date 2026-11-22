---
type: regex
pattern: 'title: ["'']?Persistence: [^\n]*postgres[^\n]*\n\s+status: ["'']?Accepted'
flags: i
target:
  source: file
  path: .agents_workspace/product/ARCHITECTURE.yaml
---
