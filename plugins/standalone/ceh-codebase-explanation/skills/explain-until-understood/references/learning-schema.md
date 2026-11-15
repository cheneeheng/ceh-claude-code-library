# Learning schema

The opt-in learning workspace of `explain-until-understood`, one file per subject at
`.agents_workspace/product/learning/<subject>.yaml`, with its `.md` rendered beside it. A
reference to it names the `.yaml`. Its layout is `../assets/learning.template.md`, relative to
this file. A new file is written as `learning/v2` YAML, per the section at the end. A file saved
as `learning/v1`, a `<subject>.md` with no YAML beside it, is still edited in place when the skill
next updates it, its `schema:` line included.

## Frontmatter

- `subject`: the subject being learned, matching the file name.

## Body

- **Goal:** what the reader wants to be able to do, in their words.
- **Next:** the one thing the next session explains first.
- **Terms:** one row per term, with the definition as the reader put it back. A term is recorded
  only once the reader has said it back in their own words.
- **Rules of thumb:** each transferable rule an explanation closed on.
- **Self-test:** one row per question. Last answer is `unaided`, `missed`, or `—` when not yet
  asked, and Date is when it was last asked.
- **Open questions:** questions the reader raised that no explanation has settled yet.

## learning/v2: YAML with generated Markdown

A `learning/v2` record is `<subject>.yaml`, a copy of `../assets/learning.template.yaml`, and
`<subject>.md` is generated from it in the layout above, beside it. The YAML is the source:
agents read and edit it, and nobody edits the Markdown, which opens with
`generated_from: <subject>.yaml` and a do-not-edit `generated_note`. The format in code is
`learning-model.py` beside this file, and `scripts/artifact.py` in the skill checks and renders it
through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<subject>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<subject>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `self_test.0` is
the first question.

**Keys**, each required, and no other key allowed, every value one line:

- `schema`: `learning/v2`. `subject`: lowercase words joined by hyphens, as in the file name.
- `goal` and `next`: as in `v1`.
- `terms`: `term` and `definition`. `rules`: one line per rule of thumb.
- `self_test`: `question`, `last_answer` (`unaided`, `missed` or `not asked`, which renders as
  `—`) and `date`, an unquoted date, or `null` exactly when the question is not yet asked.
- `open_questions`: one line per question.
- An empty list is `[]` and renders as `None`.

**Quote a value that holds `: ` or ` #`, or starts with a quote**, because YAML reads ` #` as a
comment.
