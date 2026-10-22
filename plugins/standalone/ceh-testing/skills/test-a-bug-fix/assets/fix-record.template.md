---
schema: fix-record/v1
status: diagnosed # diagnosed | fixed | unreproduced
date: YYYY-MM-DD
issue: <link or ID> # omit when there is none
plan: product/plans/<slug>.md # omit when no built plan delivered the broken code
previous: product/fixes/<slug>.md # omit when no earlier record covers this behavior
---

# <The behavior that was wrong, in one line>

**Symptom:** `<command>` → <the failing output line>

## Diagnosis

| Hypothesis | Refuted by                       | Result                                        |
| ---------- | -------------------------------- | --------------------------------------------- |
| <claim>    | <observation that would kill it> | refuted / confirmed: <output that decided it> |

**Cause:** <file:line or condition>: <one sentence on the chain from cause to symptom>

**Prediction:** `<command>` → <result predicted and seen>

## Fix

<One or two sentences: what changed and why that removes the cause.>

**Tests:**

- `<test>` — protects: <behavior>; fails_when: <the defect returns>; why_new: <why no existing
  test caught it>

**Unverified:** <what stayed unrun and why, or none>
