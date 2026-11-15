# Blog draft schema

A post `draft-post` or `edit-post` saves, wherever it goes: under `.agents_workspace/product/blog/`,
beside a draft on disk, or into a blog repo. Each is a `.yaml`, with its `.md` rendered beside it,
and a reference to it names the `.yaml`. Its layout is `../assets/blog-draft.template.md`,
relative to this file. A new post is written as `blog-draft/v2` YAML, per the section at the end,
and an older `blog-draft/v1` draft, a `.md` with no YAML beside it, stays as written, its
`schema:` line included.

## Frontmatter

- `title`: the post title. It replaces the title line of the chat draft.
- `description`: the one-line meta description, about 150 characters: the post's specific angle,
  readable without the title. It replaces the `> **Meta:**` line of the chat draft.
- `type`: one of `Lessons Learned`, `How-To`, `Opinion`, `Project / Launch`,
  `Thought Leadership`, `Personal Story`.
- `status`: `draft`, or `published` for a post already live that `edit-post` revises.
- `date`: the date the draft was saved, or the post's own date when it is already published.

## Body

The complete post, ready to copy and paste. Subheadings only if the length warrants them.

## blog-draft/v2: YAML with generated Markdown

A `blog-draft/v2` post is a copy of `../assets/blog-draft.template.yaml`, and the `.md` of the
same name is generated from it in the layout above, beside it. The YAML is the source: agents read
and edit it, and nobody edits the Markdown, which opens with `generated_from: <file>.yaml` and a
do-not-edit `generated_note`. A post with a YAML beside its `.md` is revised through the YAML,
never the `.md`. In a blog repo the rendered `.md` is the post, its front matter the format's
keys, and the body sits unchanged between the prettier-ignore markers. The format in code is
`blog-draft-model.py` beside this file, and `scripts/artifact.py` in the skill checks and renders
it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version.

**Keys**, each required, and no other key allowed:

- `schema`: `blog-draft/v2`. `title`, `description`, `type`: as in `v1`, each one line.
- `status`: `draft` or `published`. `date`: an unquoted date.
- `body`: the whole post in a `|` block, kept as written.

**Quote a one-line value that holds `: ` or ` #`, or starts with a quote**, because YAML reads
` #` as a comment: `title: 'Part 3: the parser'`.
