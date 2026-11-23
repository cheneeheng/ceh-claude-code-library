---
type: regex
pattern: 'class(?:Name)?\s*=\s*["''`][^"''`]*\bbadge\b|["''`]badge\b'
target: { source: file, path: orders.html }
---
