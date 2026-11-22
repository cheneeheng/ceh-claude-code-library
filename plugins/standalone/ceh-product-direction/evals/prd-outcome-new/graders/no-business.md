---
type: regex
pattern: 'EUR ?\d|2027-03-31|2026-12-15|@example\.com|waitlist|paying users'
flags: i
match: "not_contains"
target:
  source: file
  path: .agents_workspace/product/PRD.yaml
---
