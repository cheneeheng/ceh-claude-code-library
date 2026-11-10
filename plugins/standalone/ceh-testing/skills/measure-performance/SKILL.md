---
name: measure-performance
description: >-
  Load this skill when speed, memory, or size is the task: something is slow, a benchmark is
  written or read, or a change may have regressed performance. Trigger on "make this faster", "is
  this a regression", "benchmark this", "why is this slow", "reduce memory".
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Checking and rendering <metric>.yaml needs uv; without it the file is saved unchecked and its
  Markdown is not rendered.
license: Apache-2.0
---

# Measure performance

A performance claim is only as good as the measurement behind it. Done means the target is met
with numbers that clear the noise, or the loop stopped for a reason stated under Stop conditions,
and either way the baseline and every attempt are recorded.

## Procedure

1. **Name one metric and its workload.** Median and p95 latency of one request, throughput, peak
   memory, build time, bundle size: one, with the exact input that produces it and the target
   ("under 200 ms" or "lower than baseline").
2. **Vet the measurement before trusting it.**
   - Discard warm-up runs, then take enough runs to see the spread (ten or more, or the tool's
     default). Report the median with the spread (min and max, or the interquartile range), never
     a single run.
   - Run the baseline twice. If the two runs differ by more than the improvement you hope to
     detect, the measurement cannot see it: reduce the noise first (a quieter machine, a fixed
     input, pinned CPU frequency, more runs).
   - Explain the number. Check it moves the way it should: double the input and the time should
     change in the way the algorithm predicts. A number that does not move is measuring something
     else: a cache hit, lazy initialisation, work the compiler removed.
3. **Record the baseline** in `.agents_workspace/product/perf/<metric>.yaml`, filling
   `assets/perf-report.template.yaml`: commit, command, machine, input, unit, spread, and the
   numbers. Every later number is compared against this attempt and nothing else. When only a
   `perf-report/v1` `<metric>.md` exists, move it first, as the schema's `perf-report/v2` section
   says, keeping its baseline. Run
   `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check <metric>.yaml` before each edit
   to an existing file and stop on exit 1 with its errors. After each edit, run it with `render`,
   which writes `<metric>.md`, and fix the YAML for each error it lists. Never edit the generated
   `.md`. On exit 2 or 3, or without uv, say in the reply that the file went unchecked and
   unrendered.
4. **Profile before changing anything.** Find where the time or memory goes with the stack's
   profiler. Change only what the profile points at. Guessing at a hotspot is how a day goes into
   a function that takes 2% of the time.
5. **One change per measurement.** Make one change, re-measure the same way, and keep it only if
   the gain clears the noise band from step 2. Keep the tests green after each change. Commit each
   kept win on its own, with before and after numbers in the commit message. Revert a change that
   does not clear the noise. Add each attempt to the file's `attempts`, kept or not.
6. **Check for regressions the same way**: same command, same input, same machine as the baseline.
   A difference inside the noise band is reported as "no measurable change", not as a regression or
   a win.

## Rules

- Never compare numbers taken on different machines, builds, or inputs.
- A micro-benchmark win counts only when the end-to-end metric from step 1 also moves. Otherwise
  report it as a micro-benchmark result.
- Optimised code that changes behaviour is a bug, not a speed-up: the tests decide.
- Keep the readable version when the faster one does not clear the noise.

## Output

`.agents_workspace/product/perf/<metric>.yaml` follows `assets/perf-report.template.yaml`, per the
`perf-report/v2` section of `references/perf-report-schema.md`, one item per attempt.
`<metric>.md` is rendered from it in the layout of `assets/perf-report.template.md`, and its
attempts table goes in the reply.

## Stop conditions

- The target is met → report the table and the commits.
- Three attempts in a row fail to clear the noise band, or the profile is flat (no function above
  about 5% of the total) → stop and report: further gains need a design change, which is the
  user's call.
- The noise cannot be brought below the target improvement → report the measurement as unable to
  answer the question, with the two baseline runs as evidence.
