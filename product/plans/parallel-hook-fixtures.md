---
schema: plan/v2
generated_from: parallel-hook-fixtures.yaml
generated_note: "Do not edit. artifact.py renders this file from parallel-hook-fixtures.yaml: edit the YAML, then run artifact.py render."
title: Isolated parallel batches for hook fixtures
status: built
created: 2026-11-12
---

<!-- prettier-ignore-start -->

## Goal

Reduce the validator's hook bottleneck while executing every fixture and preserving stateful sequences.

## Scope

**In:**

- Four bounded hook fixture batches with private temporary directories and error lists.
- Stable fixture assignment by plugin or bare script name, preserving within-family order and original error numbering.
- Focused isolation, coverage and failure-order tests plus paired full-validator timing and report comparison.

**Out:**

- Hook implementation changes, skipped checks, caching or new dependencies: Improve the runner without reducing validation or changing plugin behavior.
- Merge, push or changes in the original checkout: Other work remains in progress there.

## Design

- **Isolation** hooks.run_batch(batch, batches, bash) returns a list of (fixture index, location, message) triples and creates its own fixture tree and environment. Group fixtures by the first slash-separated script component, a plugin or bare script name. Assign groups round-robin to batches. Run every selected group's fixtures in original order, including repeats and callbacks. Only batch zero records common coverage and missing-uv errors, with index -1. No thread calls common.fail; the coordinator merges errors after workers finish.
- **Concurrency** hooks.check uses ThreadPoolExecutor with at most four workers, bounded by CPU count, to overlap subprocess waits. Threads own no shared fixture state. Results sort by original fixture index before common.fail records them, preserving report order. Existing subprocess timeouts and exception propagation remain unchanged. The outer group process pool remains unchanged.
- **Proof** Save the previous hook runner under ignored .agents_workspace/baseline-hooks/hooks.py. A paired benchmark runs the full validator before and after by changing the hook module import path only. Compare stdout and exit status, record timings and retain only a measured improvement. Focused tests prove each fixture runs once, same-family order, independent roots, failure ordering and repeat behavior.

## Phases

### Phase 1: Batch hook fixtures safely

- **Builds:** Isolated threaded fixture batches, regression tests and runner documentation.
- **Check:** python -m unittest discover -s tools/validate-plugins/tests -v and python .agents_workspace/compare-hook-batches.py
- **Status:** done, Nine focused tests passed. Paired full-validator benchmark confirmed the saved serial hook runner was imported by baseline workers. Before 76.85s, after 43.32s, identical passing reports and exit code 0, speedup 1.77x.

## Open

None

## Record

- 2026-11-12 Planned: Bounded follow-up in the existing isolated worktree. Per-fixture profile passed all 219 fixtures in 52.18 seconds and found many independent subprocess waits.
- 2026-11-12 Reviewed: Independent review Ready to build, no blocking or advisory findings. Private roots and same-family ordering address existing shared state.
- 2026-11-12 Built Phase 1: Isolation regression first failed on shared roots, then all nine tests passed. Full before/after reports match with exit code 0, 76.85s versus 43.32s.
- 2026-11-12 Checked: Scope, design and phase checks match implementation. No fixture coverage removed, no hook implementation changes, and no merge or edits to the original checkout. Native Linux execution was not run.

<!-- prettier-ignore-end -->
