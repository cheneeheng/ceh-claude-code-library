# ceh-blog

Write compelling, publishable blog posts, whether you start from a half-formed idea or already have
raw material ready to shape.

## Voice

Posts come out in a **personal**, first-person voice, not influencer style. No CTA endings, no
tidy takeaway sign-offs, no aphoristic one-liners. Posts end on the honest open thread (what is
unresolved, what comes next), and a reserved verdict is a valid ending. The blog is treated as
**serials**: each project is a series, each post an episode that picks up the previous episode's
thread, keeps continuity facts straight, and leaves a thread of its own. If the target repo's
`CLAUDE.md` defines a blog voice, it overrides the built-in templates.

## Skills

| Skill            | Invoke                     | Arguments                                                       | Use when                                                                                                                                 |
| ---------------- | -------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `draft-post`     | `/ceh-blog:draft-post`     | `[topic, repo URL or path, or notes file] [blog posts path]`    | Nothing is written yet (topic, idea, repo, experience: interviews you first) or you have notes, bullets, or an outline (drafts directly) |
| `edit-post`      | `/ceh-blog:edit-post`      | `[draft file or pasted draft]`                                  | A draft in prose needs diagnosis first, then a full revised version                                                                      |
| `repurpose-post` | `/ceh-blog:repurpose-post` | `[post file or URL] [thread \| linkedin \| tldr \| newsletter]` | A finished post needs adapting into a Twitter/X thread, LinkedIn post, TL;DR, or newsletter blurb                                        |

Examples:

```
/ceh-blog:draft-post https://github.com/me/tool content/posts
/ceh-blog:draft-post notes/launch.md content/posts
/ceh-blog:edit-post content/posts/2026-09-part-3.md
/ceh-blog:repurpose-post content/posts/2026-09-part-3.md thread linkedin
```

Pass the arguments you have. Anything you leave out, the skill asks for or finds in the current
repo. The blog posts path is how the drafting skills find earlier episodes for series continuity,
and where they save the new post.

The skills also load automatically when a request clearly matches ("help me write a blog post about
this repo", "turn these notes into a post", "edit this draft", "make a thread from this"), but
invoking them by name is the primary path.

## What it produces

A complete, publication-ready blog post with:

- Title
- Structured body matched to post type (Lessons Learned, How-To, Opinion, Launch, Thought Leadership, Personal Story)
- Meta description for SEO and sharing

## Post types supported

| Type               | When to use                                   |
| ------------------ | --------------------------------------------- |
| Lessons Learned    | "I tried X", "we built Y", "I made a mistake" |
| How-To / Tutorial  | "how to do X", "step-by-step"                 |
| Opinion / Take     | "I think X is wrong", "here's my hot take"    |
| Project / Launch   | "I shipped X", "we launched"                  |
| Thought Leadership | "my view on [trend/industry]"                 |
| Personal Story     | "something happened to me", "my journey"      |
