# Repurposed post schema

One file per format that `repurpose-post` saves, `<slug>-<format>.yaml` with its `.md` rendered
beside it: next to the post when it is on disk, otherwise in `.agents_workspace/product/blog/`. A
reference to it names the `.yaml`. Its layout is `../assets/repurposed-post.template.md`, relative
to this file. A new file is written as `repurposed-post/v2` YAML, per the section at the end, and
an older `repurposed-post/v1` file, a `.md` with no YAML beside it, stays as written, its
`schema:` line included.

## Frontmatter

- `source`: the path or URL of the post this was adapted from.
- `format`: `thread`, `linkedin`, `tldr`, or `newsletter`, matching the file name.
- `date`: the date the file was written.

## Body

The adapted text, ready to paste, in the shape `repurpose-post` gives this format.

## repurposed-post/v2: YAML with generated Markdown

A `repurposed-post/v2` file is a copy of `../assets/repurposed-post.template.yaml`, and the `.md`
of the same name is generated from it in the layout above, beside it. The YAML is the source:
agents read and edit it, and nobody edits the Markdown, which opens with
`generated_from: <file>.yaml` and a do-not-edit `generated_note`. The adapted text sits unchanged
between the prettier-ignore markers, so copy it from there. The format in code is
`repurposed-post-model.py` beside this file, and `scripts/artifact.py` in the skill checks and
renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version.

**Keys**, each required, and no other key allowed:

- `schema`: `repurposed-post/v2`. `source`: one line. `format`: `thread`, `linkedin`, `tldr` or
  `newsletter`. `date`: an unquoted date.
- `text`: the adapted text in a `|` block, kept as written.

**Quote a one-line value that holds `: ` or ` #`, or starts with a quote**, because YAML reads
` #` as a comment.
