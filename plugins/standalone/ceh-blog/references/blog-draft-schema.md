# Blog draft schema

A post `draft-post` or `edit-post` saves outside a blog repo, under `.agents_workspace/blog/`. A
post written into a blog repo follows that repo's own front matter instead. A new draft is a copy
of `../assets/blog-draft.template.md`, relative to this file. The `schema: blog-draft/v1` line
stays as written.

## Frontmatter

- `title`: the post title. It replaces the title line of the chat draft.
- `description`: the one-line meta description, about 150 characters: the post's specific angle,
  readable without the title. It replaces the `> **Meta:**` line of the chat draft.
- `type`: one of `Lessons Learned`, `How-To`, `Opinion`, `Project / Launch`,
  `Thought Leadership`, `Personal Story`.
- `status`: `draft`.
- `date`: the date the draft was saved.

## Body

The complete post, ready to copy and paste. Subheadings only if the length warrants them.
