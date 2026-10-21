---
schema: perf-report/v1
metric: <metric>
commit: <baseline commit>
command: <the measuring command>
machine: <machine>
input: <input>
---

# Performance: <metric>

| Attempt  | Change         | Median (spread)   | vs baseline | Kept          |
| -------- | -------------- | ----------------- | ----------- | ------------- |
| baseline | <commit>       | <n> (<min>-<max>) | —           | —             |
| 1        | <what changed> | <n> (<min>-<max>) | <-x%>       | yes, <commit> |
