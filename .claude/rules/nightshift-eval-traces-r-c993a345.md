---
schema: nightshift-rule/v1
decided: 2026-11-24
source: "nightshift rule r-c993a345"
---

# Eval traces

Copy each eval run's trace files next to its results right after the run, before temp cleanup, because the traces of errored and expensive runs were deleted from `%TEMP%` and why a case still missed could not be diagnosed.
