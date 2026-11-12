---
schema: plan/v2
generated_from: parallel-plugin-validation.yaml
generated_note: "Do not edit. artifact.py renders this file from parallel-plugin-validation.yaml: edit the YAML, then run artifact.py render."
title: Git Bash selection and parallel plugin validation
status: built
created: 2026-11-12
---

<!-- prettier-ignore-start -->

## Goal

Run shell checks with Git Bash on Windows and overlap independent check groups without changing findings.

## Scope

**In:**

- Shared Bash selection for hook and script checks, with local skips and CI failures when unavailable.
- Bounded process pool for check groups, preserving report order and exit status.
- Focused regression tests, documentation and sequential versus parallel comparison.

**Out:**

- Changes in the original checkout, merge, push or plugin changes: The user requires isolation while other work continues.
- Parallel hook fixtures or subprocess loops inside groups: Hook fixtures share state and group concurrency is the smallest first step.

## Design

- **Shell selection** common.find_bash() returns str or None. On Windows locate git.exe and probe bin/bash.exe and usr/bin/bash.exe relative to its installation. Never use Windows bash.exe. Else use shutil.which. common.check_bash() returns the resolved path and prints it, or prints a local skip or records a CI failure when missing. Both callers use that wrapper.
- **Processes** validate.run_group(name) imports the group and returns its error list in a worker. main uses ProcessPoolExecutor with at most four workers and no more than CPU count or group count, and ordered map. Worker exceptions propagate. Keep global collectors isolated and hook fixtures sequential. Do not add a public jobs option.
- **Validation** Use stdlib unittest and real spawned workers for isolation checks. Compare ordered findings and exit codes for a sequential and parallel full validator run on this worktree. Timings are observational, not a flaky test threshold.

## Phases

### Phase 1: Select Git Bash

- **Builds:** Shared resolver, both callers, missing-shell behavior and resolver/hook regression checks.
- **Check:** python -m unittest discover -s tools/validate-plugins/tests -v
- **Status:** done, Focused unittest suite passed 8 tests, including both real hook disable cases, custom Git installation, local skip and CI failure.

### Phase 2: Parallelize groups

- **Builds:** Bounded process pool, ordered results, process isolation tests, README and benchmark comparison.
- **Check:** python -m unittest discover -s tools/validate-plugins/tests -v and python .agents_workspace/compare-validator.py, requiring identical reports and exit codes.
- **Status:** done, Focused unittest suite passed 8 tests. compare-validator.py reported identical reports and exit code 0, sequential 116.84s and parallel 74.47s, speedup 1.57x.

## Open

None

## Record

- 2026-11-12 Planned: Bounded change in an isolated worktree based on committed HEAD. No uncommitted source changes transferred.
- 2026-11-12 Reviewed: Independent fresh-context review Ready to build, zero blocking findings. Advisory addressed with named comparison harness and nonempty failure tests.
- 2026-11-12 Built Phase 1: Eight focused unittest checks passed, including real Git Bash enabled and disabled hook executions.
- 2026-11-12 Built Phase 2: Full sequential and multiprocessing runs passed with identical reports and exit code 0. Timings 116.84s and 74.47s.
- 2026-11-12 Checked: All scope, design and phase items match the code and completed checks. No gaps or extras. Native Linux execution remains untested. No merge, push or changes to the original checkout.

<!-- prettier-ignore-end -->
