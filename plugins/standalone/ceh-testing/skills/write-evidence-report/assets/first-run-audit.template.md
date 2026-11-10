---
schema: first-run-audit/v1
target: <target>
run: <NNN>
date: YYYY-MM-DD
gate: <N>/5
---

# First-Run Walkthrough — <target>

**Goal:** <goal>
**Milestones & budget:** M1 ≤ <n> actions; M2 ≤ <n>; M3 ≤ <n>
**Audience baseline:** <baseline>
**Frozen set:** <frozen set>
**Walkers:** <personas run> (<skipped: why>) — run <in parallel | serially | in isolated copies>
**Method:** cold persona-constrained subagents — proxy for a user test, not a user test
**Gate:** <N>/5

## Results

| Persona   | Furthest milestone | Stop reason | Actions vs budget | External lookups | Machine wait | First stall |
| --------- | ------------------ | ----------- | ----------------- | ---------------- | ------------ | ----------- |
| <persona> | <M>                | <reason>    | <n>/<budget>      | <n>              | <n>s         | <ID>        |

**Estimated newcomer time to goal:** ~<N> min (cost model, not measured) + <N>s machine wait

## Findings

### <ID> — <Blocker | Detour | Friction | Polish> — <title>

- **Where:** <file:line, screen, or command>
- **Persona:** <persona>
- **Expected / got:** <expected> / <got>
- **Missing knowledge:** <fact>
- **Fix:** <fix>

## Hypotheses (no walker stalled — unranked)

- <hypothesis>

## Not covered

- <what>
