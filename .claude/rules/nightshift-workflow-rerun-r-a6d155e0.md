---
schema: nightshift-rule/v1
decided: 2026-11-24
source: "nightshift rule r-a6d155e0"
---

# Workflow rerun

Before re-running or manually triggering a failed workflow while diagnosing it, check whether the retry can succeed and note any such runs in the report, because re-running the failed Pages deploy job added a second artifact so the lookup failed on two, and neither unasked run published.
