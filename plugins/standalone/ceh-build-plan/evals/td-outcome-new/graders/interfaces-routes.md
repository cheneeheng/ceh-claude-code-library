---
type: regex
pattern: 'topic: ["'']?Interfaces["'']?\n\s+choice: [|>][-+]?\n(?:(?:(?!\n  - topic:)[\s\S])*?\b(?:GET|POST|PUT|PATCH|DELETE)\s+`?/){6}'
target:
  source: file
  path: .agents_workspace/product/ARCHITECTURE.yaml
---
