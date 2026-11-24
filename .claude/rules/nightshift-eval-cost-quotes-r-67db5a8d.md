---
schema: nightshift-rule/v1
decided: 2026-11-24
source: "nightshift rule r-67db5a8d"
---

# Eval cost quotes

Before quoting a paid eval, sum the last per-case `costUsd` from the result files for exactly the cases to run, add a margin and name the heaviest cases; for a plugin with no earlier reports give the estimate as a rough upper bound and let the probe correct it; derive cost figures written into skills from the latest saved `aggregate-result.json`; and leave headroom under a spend cap since in-flight runs still finish, because a USD 8 quote became USD 32.58, a USD 32 estimate borrowed from another plugin came to USD 10.66, a skill's per-run figure was far below the real USD 0.19 to 0.77, and a step reached USD 25.28 against its USD 25 cap.
