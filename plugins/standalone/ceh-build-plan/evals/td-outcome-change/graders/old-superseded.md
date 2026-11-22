---
type: regex
pattern: 'title: Store pages in SQLite\n\s+status: ["'']?Superseded by \d{4}-\d{2}-\d{2} Persistence:'
target:
  source: file
  path: .agents_workspace/product/ARCHITECTURE.yaml
---
