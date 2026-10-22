# Blog voice schema

The voice profile `draft-post` saves to `.agents_workspace/blog-voice.md`, taken from three or more
of the blog's posts. A new profile is a copy of `../assets/blog-voice.template.md`, relative to
this file. The `schema: blog-voice/v1` line stays as written.

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
