# Perf report schema

The file `measure-performance` keeps at `.agents_workspace/product/perf/<metric>.md`, one per metric. A new
file is a copy of `../assets/perf-report.template.md`, relative to this file. The
`schema: perf-report/v1` line stays as written.

## Frontmatter

The baseline's conditions. Every later number is compared against them and nothing else.

- `metric`: the end-to-end metric measured.
- `commit`: the baseline commit.
- `command`: the measuring command.
- `machine`: the machine it ran on.
- `input`: the input it ran on.

## Attempts table

One row per attempt, the baseline first. The same table goes in the reply.

- **Attempt:** `baseline`, then 1, 2, and so on.
- **Change:** the baseline's commit, or the one change this attempt made.
- **Median (spread):** the median, then the min and max or the interquartile range. Never a
  single run.
- **vs baseline:** the change against the baseline median, as a percentage, or
  `no measurable change` when it is inside the noise band.
- **Kept:** `yes` and the commit of the kept win, or `no` when the change was reverted.
