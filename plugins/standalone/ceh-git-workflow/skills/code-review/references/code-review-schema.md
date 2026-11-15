# Code review schema

The review `code-review` saves to
`.agents_workspace/product/code-reviews/<YYYYMMDD-HHMMSS>-<session-id>-<branch>.yaml`, with its
`.md` rendered beside it, when its comments are not posted on a PR. A reference to it names the
`.yaml`. Its layout is `../assets/code-review.template.md`, relative to this file. A new review is
written as `code-review/v2` YAML, per the section at the end, and an older `code-review/v1`
review, a `.md` with no YAML beside it, stays as written, its `schema:` line included.

## Frontmatter

- `branch`: the branch reviewed.
- `date`: the review date.
- `verdict`: `Approve`, `Request changes`, `Comment`, or `Cannot verify`, per the verdict table in
  the skill.

## Body

- **Verdict:** the same verdict, then what must change to flip it to approve, or what settles it.
- **Summary:** one or two sentences: what the change does and the overall read.
- **Line comments:** one bullet per comment: the `path:line`, the label `[blocking]`,
  `[advisory]`, or `[question]`, then the comment.

## code-review/v2: YAML with generated Markdown

A `code-review/v2` review is a copy of `../assets/code-review.template.yaml`, and the `.md` of the
same name is generated from it in the layout above, beside it. The YAML is the source: agents read
and edit it, and nobody edits the Markdown, which opens with `generated_from: <file>.yaml` and a
do-not-edit `generated_note`. The format in code is `code-review-model.py` beside this file, and
`scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `comments.0` is
the first comment.

**Keys**, each required, and no other key allowed:

- `schema`: `code-review/v2`. `branch`, `verdict`: as in `v1`. `date`: an unquoted date.
- `verdict_detail`: what flips or settles the verdict, one line.
- `summary`: the summary comment in a `|` block, with its Against the spec and Dismissed lists
  when the skill writes them.
- `comments`: `location` (a `path:line` with no spaces), `label` (`blocking`, `advisory` or
  `question`) and `comment`, one line. `Approve` allows no blocking comment, `Request changes`
  needs one, and there are at most five. An empty list is `[]` and renders as `None`.

**Quote a one-line value that holds `: ` or ` #`, or starts with a quote or a backtick**, because
YAML reads ` #` as a comment and refuses a plain value that starts with a backtick.
