# Blog voice schema

The voice profile `draft-post` saves to `.agents_workspace/product/`, taken from three or more of
the blog's posts. A new profile is a `blog-voice/v2` YAML (see the last section), and its
`blog-voice.md` is rendered in the `v1` layout of `../assets/blog-voice.template.md`, relative to
this file, described below. A `v1` profile's `schema: blog-voice/v1` line stays as written.

## Frontmatter

- `blog`: the path or URL of the blog the profile was taken from.
- `posts_read`: how many posts the profile is based on.
- `date`: the date the profile was written.

## Sections

Every point is backed by a line quoted from a post, except under Never used, where the evidence is
the absence.

- **Rhythm:** sentence length and rhythm.
- **Register:** how formal or casual the posts are.
- **Recurring words and phrases:** words and phrases the author keeps using.
- **Never used:** words and constructions the author never uses.
- **Openings and closings:** how posts open and how they close.

## blog-voice/v2: YAML with generated Markdown

A `blog-voice/v2` profile is `.agents_workspace/product/blog-voice.yaml`, a copy of
`../assets/blog-voice.template.yaml`, and `blog-voice.md` beside it is generated from it in the
`v1` layout above. The YAML is the source: agents read and edit it, and nobody edits the Markdown,
which opens with `generated_from: blog-voice.yaml` and a do-not-edit `generated_note`. A `v1`
`blog-voice.md` with no YAML beside it is still read as `v1`, and converted before anything amends
it. The format in code is `blog-voice-model.py` beside this file, and `scripts/artifact.py` in the
skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check blog-voice.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render blog-voice.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `blog-voice/v2`. `blog`: the path or URL of the blog, one line. `posts_read`: how
  many posts the profile is based on, an integer of 3 or more. `date`: the date it was written,
  `YYYY-MM-DD`.
- `rhythm`, `register`, `recurring_words` and `openings_closings`: the four sections whose points
  are backed by a quote. Each is a list, `[]` when no observation was established, each item
  `point` (the observation), `quote` (a `|` block, the line quoted from a post, word for word) and
  `source` (the post's path or URL, one line, or `null` only for a quote carried from a `v1`
  profile that never named its post). A new profile names the post every quote came from.
- `never_used`: a list of words and constructions the author never uses, `[]` when no absence was
  established. Each item is the point alone: the evidence is the absence, so it carries no quote.
- `notes` (optional): a `|` block of Markdown for paragraphs a `v1` profile held outside its
  sections, rendered last as `## Notes`.

**Rules.** `point`, `quote`, every `never_used` item and `notes` are checked for content but kept
exactly as written, never stripped or reworded. The five sections render under their `v1`
headings, in the order above, and an empty one renders `None established.` under its heading. An
observation renders `- <point>: "<quote>"`, followed by `(<source>)` when the source is known. The
check proves only the shape: it cannot prove a quote is in a post or an absence is real, so never
write a quote or a source that was not read.

**Converting a `v1` profile.** Before amending a `blog-voice.md` that has no YAML, first copy it
outside the repository, to the session's scratch or temp directory: the render hook writes the new
Markdown over it as soon as the YAML is saved. Then carry every point and quotation into its
section word for word, every paragraph outside the five sections into `notes`, and an unknown
source as `null`, keeping its `blog`, `posts_read` and `date`, and compare the rendered Markdown
with the copy. When any point, quotation or paragraph of the copy is missing, restore the copy,
delete the YAML, and report what was lost. A `v1` profile
that does not fit `v2`, such as one read from two posts, is reported, never repaired by inventing a
post, a quotation or a larger `posts_read`.

**Quoting:** single-quote any one-line value that starts with `*`, `{`, `[` or `` ` ``, contains
`: ` or ` #`, or holds a backslash. Write every quote as a `|` block, which keeps its punctuation
and quotation marks as they are, and write `source: null` for an unknown source.
