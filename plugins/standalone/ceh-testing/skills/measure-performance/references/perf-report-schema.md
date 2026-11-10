# Perf report schema

The file `measure-performance` keeps at `.agents_workspace/product/perf/<metric>.md`, one per
metric. Its layout is `../assets/perf-report.template.md`, relative to this file. The file is
written as `perf-report/v2` YAML, per the section at the end, and a `perf-report/v1` file is moved
to it on its next attempt.

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

## perf-report/v2: YAML with generated Markdown

A `perf-report/v2` file is `<metric>.yaml`, a copy of `../assets/perf-report.template.yaml`, and
`<metric>.md` is generated from it in the `v1` layout above, beside it. The YAML is the source:
agents read and edit it, and nobody edits the Markdown, which opens with
`generated_from: <metric>.yaml` and a do-not-edit `generated_note`. The format in code is
`perf-report-model.py` beside this file, and `scripts/artifact.py` in the skill checks and renders
it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<metric>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<metric>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `attempts.0` is the
baseline.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `perf-report/v2`. `metric`, `command`, `machine`, `input`: as in `v1`. `commit`: the
  baseline commit, 7 to 40 lowercase hex characters, never a name such as `HEAD`, because
  `write-evidence-report` runs `git log <commit>..HEAD` on it.
- `unit`: the unit of every number, such as `ms` or `MB`, rendered after each median.
- `spread`: `range` when `low` and `high` are the min and max, `iqr` when they are the
  interquartile range.
- `attempts`: at least one, the first `attempt: baseline` and only the first, the rest numbered 1,
  2, and so on. Each has `change` (the baseline's commit, or the one change made), `median`, `low`
  and `high` (numbers, `low <= median <= high`), `within_noise` (true when the change is inside the
  noise band, never on the baseline), `kept`, and `kept_commit` (optional), given exactly when
  `kept` is true and in the same hex form as `commit`. The baseline is never kept, and its median
  is above 0.
- The renderer writes **vs baseline**: `no measurable change` when `within_noise` is true, and
  otherwise the signed change of the median from the baseline's, to one decimal (`-25.0%`), so no
  model does that arithmetic.

**Free text goes in `|` blocks or double quotes**, because ` #` starts a YAML comment, and every
value is strict, so quote a value such as `1.10` that must stay text. Never escape a quote inside
single quotes: YAML keeps the backslash there, so `'say \"hi\"'` renders as `say \"hi\"`.

**Moving a `v1` file.** A `perf-report/v1` `<metric>.md` with no YAML beside it is moved on the
next attempt: copy it to `<metric>.v1.md` first, because `.agents_workspace/` is not in git, write
`<metric>.yaml` from its frontmatter and table, render, and only then add the new attempt. A spread
the file does not name is `range`, a `vs baseline` cell reading `no measurable change` sets
`within_noise`, and `unit` comes from the numbers or the metric. The reply names the move and the
backup.
