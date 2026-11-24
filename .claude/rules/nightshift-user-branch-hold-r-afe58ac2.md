---
schema: nightshift-rule/v1
decided: 2026-11-24
source: "nightshift rule r-afe58ac2"
---

# User branch hold

When the user supplies their own branch, especially one named for comparison or experiments such as `temp/evals-comparison`, treat it as hold-for-user and do not merge it until they say to land it, because PR #380 merged such a branch and revert PR #381 was needed.
