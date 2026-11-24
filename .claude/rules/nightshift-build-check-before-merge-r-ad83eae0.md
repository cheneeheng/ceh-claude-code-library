---
schema: nightshift-rule/v1
decided: 2026-11-24
source: "nightshift rule r-ad83eae0"
---

# Build check before merge

When stacked PRs are planned for landing and a build check is due, run it before the first merge so fixes go into the PRs they belong to, because fixes for #362 and #363 landed in #364 and the first two PRs sat on `main` with known defects.
