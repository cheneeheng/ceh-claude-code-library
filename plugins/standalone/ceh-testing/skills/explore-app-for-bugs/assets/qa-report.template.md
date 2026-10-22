---
schema: qa-report/v1
app: <app>
commit: <commit>
mode: <report | fix>
date: YYYY-MM-DD HH:MM
---

# QA report: <app> at <commit>

**Launched with:** `<command>` → <url or entry point>
**Mode:** report | fix

## Charters

| Charter                                        | Actions used | Bugs  |
| ---------------------------------------------- | ------------ | ----- |
| Explore <area> with <technique> to find <risk> | <n>/20       | <ids> |

## Bugs

### <ID>: <Critical|Major|Minor|Cosmetic>: <one-line title>

- **Status:** confirmed (reproduced twice) | unconfirmed
- **Steps:** 1. ... 2. ... 3. ...
- **Expected / actual:** <...> / <...>
- **Evidence:** <screenshot path, console line, response body>
- **Fix (fix mode):** <commit and the re-run result>

## Usability notes (not bugs)

## Not explored

<flows, roles, or environments no charter covered, and why>
