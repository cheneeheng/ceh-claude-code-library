---
schema: test-audit/v1
date: YYYY-MM-DD
commit: <short sha>
mode: <fix | report-only>
---

# Test suite audit

## Findings

<Worst-first, each quoting the code it is about as `path:line` plus the line.>

```
CRITICAL  tests/unit/test_billing.py:41  no assertion — only checks no exception raised
HIGH      src/discount.py               3 surviving mutants (boundary `>=` → `>` unnoticed)
```

## Fixed

<What this run fixed, each with the finding it closes. Report-only mode: omit.>

## Needs a decision

<Each finding left for the user, with the options.>

## Unverified

<Findings that could not be anchored to quoted code. "None" when empty.>

## Commands run

<Each command and its verdict, including checks skipped and why.>
