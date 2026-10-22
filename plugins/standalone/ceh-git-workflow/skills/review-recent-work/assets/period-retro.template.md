---
schema: period-retro/v1
since: YYYY-MM-DD
until: YYYY-MM-DD
other_file: <path of the matching file in product/retros/ or .agents_workspace/retros/, or none>
---

# Retro <since> to <until>

## Shipped

- <type(scope)>: <one line> — #<PR>, #<PR>

## Flow

| Measure              | Value | From                       |
| -------------------- | ----- | -------------------------- |
| PRs merged           | <n>   | `gh pr list ...` or merges |
| Median time to merge | <d>   | PR createdAt to mergedAt   |
| Reverts              | <n>   | `git log --grep='^Revert'` |

Churn hotspots: `<path>` (<n> commits), ...

## Issues

### 1. <Kind>: <what went wrong>

- **Evidence:** <commits or PRs>
- **Route:** <skill, or "user: <where the fix lands>">
- **Status:** <handed off: <plan, fix record, or commit> / open: <why>>

## Questions the history cannot answer

- <Question>
