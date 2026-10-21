---
schema: refactor-report/v1
date: YYYY-MM-DD
commit: <sha the run started from>
---

# Refactor report

## <Cluster name>

**Applied:**

| Candidate | Before (`git diff --stat`) | After    |
| --------- | -------------------------- | -------- |
| <what>    | <totals>                   | <totals> |

**Skipped:**

| Candidate | Reason: coverage, size, or risk |
| --------- | ------------------------------- |
| <what>    | <reason>                        |

**Bugs found, not fixed:** <each as `path:line` and one line, or none>
