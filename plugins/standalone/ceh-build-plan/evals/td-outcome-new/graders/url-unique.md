---
type: regex
pattern: 'topic: ["'']?Persistence["'']?\n\s+choice: [|>][-+]?\n(?:(?!\n  - topic:)[\s\S])*unique'
flags: i
target:
  source: file
  path: .agents_workspace/product/ARCHITECTURE.yaml
---
