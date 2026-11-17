---
schema: fix-record/v3
status: <diagnosed | fixed | unreproduced | declined>
date: YYYY-MM-DD
issue: <link or ID>
plan: .agents_workspace/product/plan/<file>.yaml
previous: .agents_workspace/product/fix/<file>.yaml
---

# <functionality>

## 1. <behavior that was wrong>

**Status:** <diagnosed | fixed | unreproduced | declined>

**Symptom:** `<command>` → <failing output line>

### Diagnosis

| Hypothesis | Refuted by    | Result                          |
| ---------- | ------------- | ------------------------------- |
| <claim>    | <observation> | <refuted / confirmed>: <output> |

**Cause:** <file:line or condition>: <cause to symptom>

**Prediction:** `<command>` → <result>

### Fix

<change and why>

**Tests:**

- `<test>` — protects: <behavior>; fails_when: <defect returns>; why_new: <reason>

**Unverified:** <what stayed unrun, or none>
