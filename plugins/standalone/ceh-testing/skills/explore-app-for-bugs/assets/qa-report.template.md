---
schema: qa-report/v1
app: <app>
commit: <commit>
mode: <report | fix>
date: YYYY-MM-DD HH:MM
---

# QA report: <app> at <commit>

**Launched with:** `<command>` → <url or entry point>
**Mode:** <report | fix>

## Charters

| Charter                                        | Actions used | Bugs  |
| ---------------------------------------------- | ------------ | ----- |
| Explore <area> with <technique> to find <risk> | <n>/20       | <ids> |

## Bugs

### <ID>: <Critical | Major | Minor | Cosmetic>: <title>

- **Status:** <confirmed (reproduced twice) | unconfirmed>
- **Steps:** 1. <step>
- **Expected / actual:** <expected> / <actual>
- **Evidence:** <evidence>
- **Fix:** <commit>, <re-run result>

## Usability notes (not bugs)

- <note>

## Not explored

- <flow, role, or environment>: <why>
