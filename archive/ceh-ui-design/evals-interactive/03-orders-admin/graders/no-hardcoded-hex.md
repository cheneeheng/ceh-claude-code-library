---
type: regex
target: { source: file, path: orders.html }
match: not_contains
weight: 0.5
---

:\s*#[0-9a-fA-F]{3,8}\b
