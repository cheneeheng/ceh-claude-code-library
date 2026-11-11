# Repeat mistake schema

The file `prevent-repeat-mistake` saves: `product/retros/<YYYY-MM-DD>-repeat-mistake.md` for fixes
that land in the current repository, `.agents_workspace/product/retros/<YYYY-MM-DD>-repeat-mistake.md` for
fixes only the user acts on. A new file is a copy of `../assets/repeat-mistake.template.md`,
relative to this file. The `schema: repeat-mistake/v1` line stays as written. Appending to an
existing file adds rows and drafts, and leaves its frontmatter as it is.

## Frontmatter

- `date`: the date the file was created.
- `other_file`: the path of the matching file in the other folder, or `none`. When both files
  exist, each links the other.

## Body

- **Table:** one row per mistake. Mistake is one line. Evidence is a `path:line` or a quoted tool
  call. Rung is 1 to 5. Fix is what was added or drafted. Proof is `yes` when the fix fails on the
  real mistake, or `not provable`. Status is `applied`, `awaiting approval`, or `rejected`, and is
  updated in place when a draft is applied or rejected.
- **Why this rung:** one line per rung chosen, on why the rungs above it did not fit.
- **Pending drafts:** one `###` per fix `awaiting approval`, holding the full draft, so a later
  session can apply it from this file alone.

## repeat-mistake/v2: YAML with generated Markdown

A `repeat-mistake/v2` report is `product/retros/<YYYY-MM-DD>-repeat-mistake.yaml` for fixes that
land in the current repository, or `.agents_workspace/product/retros/<YYYY-MM-DD>-repeat-mistake.yaml`
for fixes only the user acts on, a copy of `../assets/repeat-mistake.template.yaml`. The `.md` of
the same stem is generated from it in the `v1` layout above, beside it. Only the dated name is a
report: a labelled name such as `<YYYY-MM-DD>-<label>-repeat-mistake.md` is not, and stays as it
is. The YAML is the source: agents read and edit it, and nobody edits the Markdown, which opens
with `generated_from: <file>.yaml` and a do-not-edit `generated_note`. A `v1` `.md` with no YAML
beside it is still read as `v1`, and converted before anything amends it. The format in code is
`repeat-mistake-model.py` beside this file, and `scripts/artifact.py` in the skill checks and
renders it through uv:

```bash
uv run --script scripts/artifact.py check <file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `repeat-mistake/v2`. `date`: the date the file was created, `YYYY-MM-DD`, which the
  title renders from. `other_file`: the repo-relative path of the matching YAML in the other
  folder, or `null`. It renders as that file's `.md`, and `none` for `null`.
- `fixes`: at least one, each `id` (a positive integer, unique in the file, shown in the `#`
  column), `mistake` (one line), `evidence` (a `path:line` or a quoted tool call), `rung` (1 to
  5), `fix` (what was added or drafted), `proof` (`"yes"`, quoted so YAML keeps it text, when the
  fix fails on the real mistake, or `not provable`), `status` (`applied`, `awaiting approval` or
  `rejected`), `why_rung` (why the rungs above it did not fit) and `draft` (optional, the full
  draft). Every text value except `mistake` may be a `|` block of Markdown.
- `notes` (optional): a `|` block of Markdown for context that belongs to no one fix, rendered as
  `## Context` before the table.

**Rules.** A fix `awaiting approval` has its `draft`. A rung 5 fix is written guidance, so its
`proof` is `not provable`. Text is kept exactly as written, code fences included. Pending drafts
renders only fixes `awaiting approval`, each as `### <id>: <mistake>`, or `None.`, and an applied
or rejected fix keeps its draft as history under `## Previous drafts`, labelled with its status.
Table cells escape `|` and turn line breaks into `<br>`, without changing the stored values. No
count of pending fixes is stored: it is read from `status`.

**Appending and updating.** A new fix takes the largest `id` in the file plus one. Before adding
one, compare its mistake and evidence with the fixes already there, so a retry updates the same
`id` instead of adding a second. Applying or rejecting a draft changes that fix's `status` only,
keeping its draft and evidence. When both files exist, each `other_file` names the other: check
both links after both saves, since the first save cannot name a file not yet written.

**Converting a `v1` report.** Before amending a `v1` report, carry every row into `fixes` with
`id`s in row order, each `### ` draft, pending or not, into its fix's `draft`, the rung reasons
into each fix's `why_rung` (a reason shared by several fixes goes into each), and every other
section into `notes`. Match a draft to its row by the mistake and files it names, not by an
identical heading. A `v1` status that is or begins with `applied`, `awaiting approval` or
`rejected` maps to that value, and a `v1` proof that is or begins with `yes` or `not provable`, or
says `fails on the real mistake: yes`, maps to that value. When either carried more text, keep the
full text in `notes` under the fix's `id`. Stop and report, leaving the `v1` file untouched, when a
status or proof matches none of these, when a draft's row is ambiguous, or when a pending row has
no full draft. Never infer a status or a proof from whether a draft exists.

**Quoting:** single-quote any one-line value that starts with `*`, `{`, `[` or `` ` ``, contains
`: ` or ` #`, or holds a backslash. Write evidence, fixes, reasons and drafts as `|` blocks, which
keep backticks, quotes and code fences as they are. Mask every secret as `<secret>` in a committed
report: the check cannot see secrets.
