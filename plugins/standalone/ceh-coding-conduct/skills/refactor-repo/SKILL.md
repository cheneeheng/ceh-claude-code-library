---
name: refactor-repo
description: >-
  Audit a whole codebase (or one named module) for accumulated complexity and shrink it through a
  propose-then-apply refactor campaign: a read-only inventory of candidates (duplication, dead code,
  over-abstraction), a ranked proposal with payoff, risk, and diff size, then, only after explicit
  approval of specific clusters, apply them on refactor/ branches under a behavior-preservation
  gate. Not for simplifying one branch's diff before a PR (use shrink-diff) or write-time minimalism
  (use write-less-code).
argument-hint: "[module-or-path]"
disable-model-invocation: true
user-invocable: true
compatibility: >-
  Requires the git CLI on PATH and a git working tree, for the before/after `git diff --stat`
  totals the report is built on. Applying and verifying a refactor additionally needs whatever
  runtime, package manager, and test runner the target repo already uses - none is assumed.
license: Apache-2.0
---

# Refactor repo

The whole-codebase counterpart of `shrink-diff`: the same standard, but with no diff to scope
it, so scope discipline comes from process instead. This is the high-risk mode — a repo-wide
refactor applied in one pass produces an unreviewable diff and regressions in code that had no
motivating change. Never apply anything in the same breath as finding it: **inventory → propose
→ approval → apply**.

## Procedure

### Phase 1 — Inventory (read-only)

Scope is the whole repo, or the module/directory the user names. No edits in this phase.

Hunt the same categories as `shrink-diff`, plus the ones only time produces:

- **Duplication anywhere** — parallel implementations that have drifted apart count double;
  they are a live bug source, not just bloat.
- **Dead code** — unreachable branches, unused exports and symbols, obsolete compatibility
  shims, feature flags fully rolled out.
- **Over-abstraction** — single-implementation interfaces, single-caller wrappers, config for
  constants, layers that only forward.
- **Information leakage** — one design decision (a file format, a status string, an ordering
  rule) known by two or more modules, so changing it means editing each. Unlike duplication the
  code may look different everywhere. The fix moves the decision behind one module.
- **Retroactive ladder violations** (below).

For each area, also record its **test coverage status** — it decides in Phase 3 what may be
applied there.

### The retroactive ladder

Walk each piece of code in scope down the write-less-code ladder, in hindsight:

1. **Does it need to exist at all?** Dead code, an unused parameter or flag, a speculative hook
   nothing calls → delete it.
2. **Stdlib does it?** Replace the custom version.
3. **Native platform feature covers it?** Replace the custom version.
4. **An already-installed dependency solves it?** Replace the custom version. Never add a new
   dependency to shrink code: its install, supply-chain, and upgrade cost outlasts the lines saved.
5. **Can it be one line?** Make it one line.
6. **Only then:** keep it, as the minimum that works — collapse single-implementation
   abstractions, inline single-caller wrappers, turn config-for-a-constant back into a constant.

### Phase 2 — Propose, then stop

Deliver a ranked candidate table:

| #   | What / where | Payoff (est. lines removed, readability) | Risk | Est. diff size | Coverage |
| --- | ------------ | ---------------------------------------- | ---- | -------------- | -------- |

Group candidates into clusters sized so each cluster makes one reviewable PR (the size limits in
`ceh-git-workflow:pull-request`). Then **stop and wait for the user to select clusters**. Invoking
this skill approved the campaign, not any specific candidate — never proceed past this point
unprompted. With no human to select (a headless run), the ranked table is the deliverable: end the
run there and apply nothing, because no cluster was approved.

### Phase 3 — Apply approved clusters

- One `refactor/<cluster>` branch per approved cluster, branched from `main`
  (`ceh-git-workflow:branch`); many small PRs beat one big one.
- Behavior preservation (below) gates every edit. In areas with no coverage the rule is
  skip-and-report, not apply-carefully — careful is not a gate.
- A cluster that grows past its estimated diff size mid-apply gets split or stopped, not pushed
  through.

## Rules

### Behavior preservation

A refactor changes shape, never behavior:

- Never mix a behavior change into a refactor. If shrinking reveals a bug, report it — fixing it
  is separate work.
- Where tests cover the touched code, run them before and after; both runs must be green. A red
  before-run is a finding to report, not a license to proceed.
- Where no tests cover it, apply only mechanical transforms (delete provably-dead code, inline,
  rename, extract) and flag anything riskier instead of applying it.
- For anything past a mechanical transform — an extraction across files, an implementation swap, a
  dependency or runtime upgrade — pin current behavior first with
  `ceh-testing:verify-behavior-preserved` (characterization tests, golden files, differential run)
  and commit those pins on their own before touching the code. A green existing suite is the weaker
  check: it only proves what it already covered.
- Commit refactors with the `refactor:` type, separate from any other change.

## Output

### Phase 4 — Report

Per cluster: candidates applied with before/after `git diff --stat` totals, candidates skipped
with reasons (coverage, size, risk), and any bug found while refactoring — reported, not fixed.
