# Period retro schema

The retro `write-period-retro` saves:
`.agents_workspace/product/retro/<YYYYMMDD-HHMMSS>-<session-id>-period.yaml`, with its `.md`
rendered beside it, unless the repo's `CLAUDE.md` names another location. A reference to it names
the `.yaml`. One file holds the retro and every issue, whether its fix lands in this repo or
outside it, because the two files of `v1` would share one name in one folder. Its layout is
`../assets/period-retro.template.md`, relative to this file. A new file is written as
`period-retro/v3` YAML, per the section at the end.

An older retro is still read: a `period-retro/v2` file, a `-period.md` with no YAML beside it,
as written, and a `period-retro/v1` file, an in-repo file and a local file that link each other
through `other_file`, whose issues are the issues of both files.

## Frontmatter

- `since`, `until`: the first and last day of the period.

## Sections

- **Shipped:** one bullet per change, as `<type(scope)>: <one line>`, then its PR numbers.
- **Flow:** the three measures, each with where the value came from: PRs merged (`gh pr list` or
  the merges), median time to merge (PR `createdAt` to `mergedAt`), and reverts
  (`git log --grep='^Revert'`). Then the churn hotspots: each path with its commit count,
  separated by commas.
- **Issues:** one numbered `### <n>. <Kind>: <what went wrong>` per issue. **Evidence** names the
  commits or PRs. **Route** names the skill, or `user: <where the fix lands>` for a fix outside
  this repo. **Status** is `handed off: <plan, fix record, or commit>` or `open: <why>`.
- **Questions the history cannot answer:** one bullet per question.

## period-retro/v3: YAML with generated Markdown

A `period-retro/v3` retro is a copy of `../assets/period-retro.template.yaml`, and the `.md` of the
same name is generated from it in the layout above, beside it. The YAML is the source: agents read
and edit it, and nobody edits the Markdown, which opens with `generated_from: <file>.yaml` and a
do-not-edit `generated_note`. The format in code is `period-retro-model.py` beside this file, and
`scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `issues.0` is
issue 1.

**Keys**, each required, and no other key allowed, every value one line:

- `schema`: `period-retro/v3`. `since` and `until`: unquoted dates, `since` no later than `until`.
- `shipped`: `group` (the `type(scope)` or top-level directory), `change`, and `refs`, at least
  one PR number or commit, each quoted when it starts with `#`.
- `flow`: `prs_merged`, `median_time_to_merge` and `reverts`, each a `value` and its `source`, the
  command it came from.
- `hotspots`: `path` and `commits`, an integer.
- `issues`: at most three, each with `kind` (`Bug`, `Design`, `Project rule` or `Agent mistake`),
  `issue`, `evidence`, `route`, `status` (`handed off`, `open` or `dropped`) and `status_detail`,
  the artifact handed off to, the user decision an `open` issue waits on, or why it was dropped. The renderer numbers them from 1.
- `questions`: one line per question.
- An empty list is `[]` and renders as `None`, or `none` for `hotspots`.

**Quote a value that holds `: ` or ` #`, or starts with a quote or `#`**, because YAML reads `#`
as a comment: `route: 'user: the dotfiles repo'`.
