# Repurposed post schema

One file per format that `repurpose-post` saves, `<slug>-<format>.md`: next to the post when it is
on disk, otherwise in `.agents_workspace/blog/`. A new file is a copy of
`../assets/repurposed-post.template.md`, relative to this file. The `schema: repurposed-post/v1`
line stays as written.

## Frontmatter

- `source`: the path or URL of the post this was adapted from.
- `format`: `thread`, `linkedin`, `tldr`, or `newsletter`, matching the file name.
- `date`: the date the file was written.

## Body

The adapted text, ready to paste, in the shape `repurpose-post` gives this format.
