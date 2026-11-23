---
type: regex
pattern: 'topic: ["'']?Interfaces["'']?\n\s+choice: [|>][-+]?\n(?:(?!\n  - topic:)[\s\S])*\b4(?:00|01|03|04|09|13|22)\b'
target:
  source: file
  path: .agents_workspace/product/ARCHITECTURE.yaml
---
