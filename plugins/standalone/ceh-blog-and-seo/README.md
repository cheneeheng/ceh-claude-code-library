# ceh-blog-and-seo

Tell people about what you built. Write compelling, publishable blog posts, whether you start from
a half-formed idea or already have raw material ready to shape. And make anything exposed to the
internet findable: SEO and GEO (generative engine optimization) for public web pages, repo
READMEs, package listings, and landing copy.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). The hooks need `python3` on `PATH`.
Checking and rendering the saved YAML needs [uv](https://docs.astral.sh/uv/), which installs
pydantic and PyYAML on first use. Without uv the YAML is saved and the agent says the Markdown was
not rendered, and a business plan or evidence file is read unchecked. A repo with none of these
files needs no uv. No other plugin depends on this one.

## Skills

| Skill                        | Say or type                                                                                                                                          | What it does                                                                                                                                      |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `draft-post`                 | "help me write a blog post about this repo", "turn these notes into a post", `/ceh-blog-and-seo:draft-post [topic, repo or notes file] [posts path]` | Drafts a new post. With only a topic, idea, repo or experience it interviews you first. With notes, bullets or an outline it drafts straight away |
| `edit-post`                  | "edit this draft", "polish this post", `/ceh-blog-and-seo:edit-post [draft file or pasted draft]`                                                    | Diagnoses a draft written in prose first, then gives a full revised version in your voice                                                         |
| `repurpose-post`             | "make a thread from this", `/ceh-blog-and-seo:repurpose-post [post file or URL] [thread \| linkedin \| tldr \| newsletter]`                          | Adapts a finished post into a Twitter/X thread, LinkedIn post, TL;DR, or newsletter blurb                                                         |
| `make-page-crawlable`        | "add SEO", "meta tags", "structured data", "sitemap", `/ceh-blog-and-seo:make-page-crawlable`                                                        | For a public web page: head checklist, sitemap and robots, JSON-LD structured data, server rendering or prerender needs, and GEO rules            |
| `write-llms-txt`             | "write an llms.txt", "llms-full.txt", `/ceh-blog-and-seo:write-llms-txt`                                                                             | Creates or updates the `llms.txt` reading list for AI agents: its format, which links to list, `## Optional`, and `llms-full.txt`                 |
| `write-project-listing-text` | "make this repo findable", "GitHub topics", `/ceh-blog-and-seo:write-project-listing-text`                                                           | Writes the README first screen, package description and keywords, GitHub topics, marketplace listings, or landing copy                            |

The skills also load by themselves when a request clearly matches, but invoking them by name is the
primary path.

## Agents

This plugin has no agents.

## Hooks

Two hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off.

| Hook                 | What it does for you                                                                                                                                                                                |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Artifact check       | Checks each voice profile, blog draft and repurposed post when it is written, and renders its Markdown. It does the same for `EVIDENCE.yaml` and `BUSINESS_PLAN.yaml`. Errors go back to the agent. |
| Generated-file guard | Stops a hand edit to a Markdown file generated from a YAML file, which the next render would overwrite.                                                                                             |

Without uv the agent is told once per session that a file went unchecked.

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable             | Default              | Effect                                                                           |
| -------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK` | unset (check on)     | `off` turns the artifact check and the generated-file guard off                  |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook names to skip: `artifact-render-hook`, `generated-md-guard` |

## How it works

### Voice

Posts come out in a **personal**, first-person voice, not influencer style. No CTA endings, no
tidy takeaway sign-offs, no aphoristic one-liners. Posts end on the honest open thread (what is
unresolved, what comes next), and a reserved verdict is a valid ending. When the blog runs as a
**series**, each post is an episode that picks up the previous episode's thread, keeps continuity
facts straight, and leaves a thread of its own. If the target repo's `CLAUDE.md` defines a blog
voice, it overrides the built-in templates.

On a blog with three or more posts, `draft-post` captures the author's voice once, into a voice
profile. Every new observation quotes a post word for word and names it. Later drafts and
`edit-post` read the profile instead of re-deriving it.

### Arguments

```
/ceh-blog-and-seo:draft-post https://github.com/me/tool content/posts
/ceh-blog-and-seo:draft-post notes/launch.md content/posts
/ceh-blog-and-seo:edit-post content/posts/2026-09-part-3.md
/ceh-blog-and-seo:repurpose-post content/posts/2026-09-part-3.md thread linkedin
```

Pass the arguments you have. Anything you leave out, the skill asks for or finds in the current
repo. The blog posts path is how the drafting skills find earlier episodes for series continuity,
and where they save the new post.

### Answering questions

Whenever a skill interviews you or asks for feedback, it sends every question at once, numbered,
each about one topic and each with lettered options. Answer them in one reply, for example
`1B, 2A, 3 Other: ...`.

### What a post contains

A complete, publication-ready blog post with:

- Title
- Structured body matched to post type (Lessons Learned, How-To, Opinion, Launch, Thought
  Leadership, Personal Story)
- Meta description for SEO and sharing

| Type               | When to use                                   |
| ------------------ | --------------------------------------------- |
| Lessons Learned    | "I tried X", "we built Y", "I made a mistake" |
| How-To / Tutorial  | "how to do X", "step-by-step"                 |
| Opinion / Take     | "I think X is wrong", "here's my hot take"    |
| Project / Launch   | "I shipped X", "we launched"                  |
| Thought Leadership | "my view on [trend/industry]"                 |
| Personal Story     | "something happened to me", "my journey"      |

### Findability

Two skills carry a GEO layer: content structured so AI engines can extract and cite it, with
answer-first sections, standalone quotable facts, and question-shaped headings. Accessibility
always wins conflicts with SEO.

## Not this plugin

- README **accuracy** after a code change: `ceh-git-workflow:update-readme`. These skills own
  README **findability**.
- Writing project documentation itself: `ceh-documentation`. These skills govern how that content
  is found and cited.

## Where its files live

Every post the blog skills save is YAML with its Markdown rendered beside it, wherever it goes: a
draft or revision, and each repurposed format. In a blog repo the rendered `.md` is the post, its
front matter the format's keys. A post with its YAML is revised through the YAML, and one saved as
plain Markdown before is still read as it is.

The voice profile goes to `.agents_workspace/product/blog/blog-voice.yaml`, with `blog-voice.md`
rendered beside it. A profile saved at the older `.agents_workspace/product/` root is still read
and amended there. A profile saved as `blog-voice.md` only, before the YAML form, is still read by
both skills.

A project with a root `product/` moves each file to the same sub-path under
`.agents_workspace/product/`, or names its location in `CLAUDE.md`.
