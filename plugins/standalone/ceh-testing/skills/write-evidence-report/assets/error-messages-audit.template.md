---
schema: error-messages-audit/v1
target: <target>
run: <NNN>
date: YYYY-MM-DD
harvested: <n>
already_complete: <n>
---

# Error messages — <target>, run <NNN>

**Messages harvested:** <n>
**Complete before rewriting:** <n> of <n>

## Triage

| #   | Location        | Current text | 1        | 2        | 3        | Severity                                  | Rewrite | Applied               |
| --- | --------------- | ------------ | -------- | -------- | -------- | ----------------------------------------- | ------- | --------------------- |
| 1   | `<path>:<line>` | `<text>`     | <✓ \| ✗> | <✓ \| ✗> | <✓ \| ✗> | <Blocker \| Detour \| Friction \| Polish> | `<new>` | <yes \| no: <reason>> |

## Systemic causes

- <handler or wrapper>: <rows>, <fixed once \| not fixed>
