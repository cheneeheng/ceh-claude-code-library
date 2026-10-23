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
