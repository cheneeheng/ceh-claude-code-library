---
type: regex
pattern: 'no PRD|PRD[^\n]{0,40}(?:missing|not found|does not exist|none)|no (?:product )?requirements'
flags: i
target: last_message
---
