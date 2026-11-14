---
schema: fix-record/v1
status: <diagnosed | fixed | unreproduced>
date: YYYY-MM-DD
issue: <link or ID>
plan: .agents_workspace/product/plans/<slug>.yaml
previous: .agents_workspace/product/fixes/<slug>.yaml
---

# <behavior that was wrong>

**Symptom:** `<command>` → <failing output line>

## Diagnosis

| Hypothesis | Refuted by    | Result                          |
| ---------- | ------------- | ------------------------------- |
| <claim>    | <observation> | <refuted / confirmed>: <output> |

**Cause:** <file:line or condition>: <cause to symptom>

**Prediction:** `<command>` → <result>

## Fix

<change and why>

**Tests:**

- `<test>` — protects: <behavior>; fails_when: <defect returns>; why_new: <reason>

**Unverified:** <what stayed unrun, or none>
