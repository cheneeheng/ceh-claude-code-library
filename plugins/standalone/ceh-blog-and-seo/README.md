# ceh-blog-and-seo

Tell people about what you built. Write compelling, publishable blog posts, whether you start from
a half-formed idea or already have raw material ready to shape. And make anything exposed to the
internet findable: SEO and GEO (generative engine optimization) for public web pages, repo
READMEs, package listings, and landing copy.

## Voice

Posts come out in a **personal**, first-person voice, not influencer style. No CTA endings, no
tidy takeaway sign-offs, no aphoristic one-liners. Posts end on the honest open thread (what is
unresolved, what comes next), and a reserved verdict is a valid ending. When the blog runs as a
**series**, each post is an episode that picks up the previous episode's thread, keeps continuity
facts straight, and leaves a thread of its own. If the target repo's
`CLAUDE.md` defines a blog voice, it overrides the built-in templates.

## Blog skills

| Skill            | Invoke                             | Arguments                                                       | Use when                                                                                                                                 |
| ---------------- | ---------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `draft-post`     | `/ceh-blog-and-seo:draft-post`     | `[topic, repo URL or path, or notes file] [blog posts path]`    | Nothing is written yet (topic, idea, repo, experience: interviews you first) or you have notes, bullets, or an outline (drafts directly) |
| `edit-post`      | `/ceh-blog-and-seo:edit-post`      | `[draft file or pasted draft]`                                  | A draft in prose needs diagnosis first, then a full revised version                                                                      |
| `repurpose-post` | `/ceh-blog-and-seo:repurpose-post` | `[post file or URL] [thread \| linkedin \| tldr \| newsletter]` | A finished post needs adapting into a Twitter/X thread, LinkedIn post, TL;DR, or newsletter blurb                                        |

Examples:

```
/ceh-blog-and-seo:draft-post https://github.com/me/tool content/posts
/ceh-blog-and-seo:draft-post notes/launch.md content/posts
/ceh-blog-and-seo:edit-post content/posts/2026-09-part-3.md
/ceh-blog-and-seo:repurpose-post content/posts/2026-09-part-3.md thread linkedin
```

Pass the arguments you have. Anything you leave out, the skill asks for or finds in the current
repo. The blog posts path is how the drafting skills find earlier episodes for series continuity,
and where they save the new post.

Whenever a skill interviews you or asks for feedback, it sends every question at once, numbered,
each about one topic and each with lettered options. Answer them in one reply, for example
`1B, 2A, 3 Other: ...`. The rules live in `references/ask-the-author.md`, copied into each of the three blog skills.

The skills also load automatically when a request clearly matches ("help me write a blog post about
this repo", "turn these notes into a post", "edit this draft", "make a thread from this"), but
invoking them by name is the primary path.

`draft-post` checks `BUSINESS_PLAN.yaml` or `EVIDENCE.yaml` against its model before reading it,
which needs [uv](https://docs.astral.sh/uv/), installing pydantic and PyYAML on first use. Without
uv the file is read unchecked, and a repo with none of these files needs no uv.

On a blog with three or more posts, `draft-post` captures the author's voice once, into
`.agents_workspace/product/blog-voice.yaml` (`blog-voice/v2`, checked by a model), with
`blog-voice.md` rendered beside it. Every new observation quotes a post word for word and names
it; one carried from an older profile that never named its post keeps its quote with no source.
Later drafts and `edit-post` read the profile instead of re-deriving it. A profile saved before
`v2` stays as `blog-voice.md`, which both skills still read.

## Discoverability skills

Discoverability is one activity applied to many surfaces. The skills split on surface mechanics,
which is also where their trigger moments and file types are disjoint:

| Skill                        | Invoke                                         | Triggers when                                                                                                                                            |
| ---------------------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `make-page-crawlable`        | `/ceh-blog-and-seo:make-page-crawlable`        | Shipping or creating a public web page: per-page head checklist, sitemap/robots, JSON-LD structured data, SSR/prerender requirements, GEO rules          |
| `write-llms-txt`             | `/ceh-blog-and-seo:write-llms-txt`             | Creating or updating the `llms.txt` reading list for AI agents: the positional format, link curation, `## Optional`, markdown over HTML, `llms-full.txt` |
| `write-project-listing-text` | `/ceh-blog-and-seo:write-project-listing-text` | Writing the README first screen, package description and keywords, GitHub topics, marketplace listings, or landing copy: the excerpt rule and one-liner  |

Two skills carry a GEO layer: content structured so AI engines can extract and cite it —
answer-first sections, standalone quotable facts, question-shaped headings.

`write-project-listing-text` checks `BUSINESS_PLAN.yaml` or `EVIDENCE.yaml` against its model
before reading it, which needs [uv](https://docs.astral.sh/uv/), installing pydantic and PyYAML on
first use. Without uv the file is read unchecked, and a repo with none of these files needs no uv.

### Boundaries

- README **accuracy** after a code change belongs to `ceh-git-workflow:update-readme`. These
  skills own README **findability**.
- Writing the content itself belongs to the blog skills above and to `ceh-documentation`. These
  skills govern how that content is found and cited.
- Accessibility always wins conflicts with SEO.

## Hooks

Two hooks on `Edit|Write|MultiEdit`, both Python scripts that need `python3` on `PATH`:

- `artifact-render-hook.py` (PostToolUse) checks a written voice profile YAML against its model
  and renders its Markdown. Because `draft-post` and `write-project-listing-text` also carry the evidence and business plan
  models, it checks and renders `EVIDENCE.yaml` and `BUSINESS_PLAN.yaml` writes too. The check
  needs `uv`; without it the agent is told once per session that the file went unchecked.
- `generated-md-guard.py` (PreToolUse) denies a hand edit to the generated Markdown, which the
  next render would overwrite.

`CEH_ARTIFACT_CHECK=off` turns both off, and `CEH_DISABLED_HOOKS` turns off either by name.

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

## Where its files live

Since 2026-11-14 this plugin saves and reads product files in `.agents_workspace/product/`. A project with a root `product/` moves each file to the same sub-path there, or names its location in `CLAUDE.md`.
