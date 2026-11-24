---
schema: nightshift-rule/v1
decided: 2026-11-24
source: "nightshift rule r-33a50353"
---

# Formatter vs rule

Before fixing a finding that cites a style rule such as `decision-frontmatter-scalars.md`, check that the repo's formatter or hook produces what the rule asks for, and raise any conflict with the user first, because the prettier hook rewrote single quotes back to double, the finding stayed unfixed and a third PR (#378) was needed.
