---
schema: first-run-audit/v1
target: <target>
run: <NNN>
date: YYYY-MM-DD
gate: <N>/5
---

# First-Run Walkthrough — <target>

**Goal:** <the one sentence from step 1>
**Milestones & budget:** <M1 ≤ n actions; M2 ≤ n; M3 ≤ n>
**Audience baseline:** <verbatim from step 2>
**Frozen set:** <verbatim list>
**Walkers:** <personas run> (<personas skipped, and why>) — run <in parallel | serially | in isolated copies>
**Method:** cold persona-constrained subagents — proxy for a user test, not a user test
**Gate:** <N>/5

## Results

| Persona | Furthest milestone | Stop reason | Actions vs budget | External lookups | Machine wait | First stall |
| ------- | ------------------ | ----------- | ----------------- | ---------------- | ------------ | ----------- |

**Estimated newcomer time to goal:** ~<N> min (cost model, not measured) + <N>s machine wait

## Findings

### <ID> — <Blocker|Detour|Friction|Polish> — <one-line title>

- **Where:** <file:line, screen, or command>
- **Persona:** <who stalled>
- **Expected / got:** <what they thought would happen / what happened>
- **Missing knowledge:** <the fact they needed and did not have>
- **Fix:** <the concrete change>

## Hypotheses (no walker stalled — unranked)

## Not covered

<what this method cannot measure; what was delegated to accessibility>
