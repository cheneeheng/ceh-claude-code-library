---
type: regex
pattern: ':\s*#[0-9a-f]{3,8}\b'
flags: i
match: not_contains
target: { source: file, path: orders.html }
---
