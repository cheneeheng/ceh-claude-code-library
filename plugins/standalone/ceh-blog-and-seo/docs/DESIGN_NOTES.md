# ceh-blog-and-seo design notes

## Ask-the-author rules

The rules live in `references/ask-the-author.md`, copied into each of the three blog skills.

## Discoverability skill split

Discoverability is one activity applied to many surfaces. The skills split on surface mechanics,
which is also where their trigger moments and file types are disjoint.

## Saved formats

On a blog with three or more posts, `draft-post` captures the author's voice once, into
`.agents_workspace/product/blog/blog-voice.yaml` (`blog-voice/v2`, checked by a model), with
`blog-voice.md` rendered beside it. Every new observation quotes a post word for word and names
it; one carried from an older profile that never named its post keeps its quote with no source.
A profile saved before `v2` stays as `blog-voice.md`, which both skills still read.

Every post the blog skills save is YAML with its Markdown rendered beside it, wherever it goes: a
draft or revision (`blog-draft/v2`) and each repurposed format (`repurposed-post/v2`).

## Hooks

Two hooks on `Edit|Write|MultiEdit`, both Python scripts that need `python3` on `PATH`:

- `artifact-render-hook.py` (PostToolUse) checks a written voice profile, blog draft or
  repurposed post YAML against its model and renders its Markdown. Because `draft-post` and
  `write-project-listing-text` also carry the evidence and business plan models, it checks and
  renders `EVIDENCE.yaml` and `BUSINESS_PLAN.yaml` writes too. The check needs `uv`; without it
  the agent is told once per session that the file went unchecked.
- `generated-md-guard.py` (PreToolUse) denies a hand edit to the generated Markdown, which the
  next render would overwrite.

`CEH_ARTIFACT_CHECK=off` turns both off, and `CEH_DISABLED_HOOKS` turns off either by name.

## Product file location

Since 2026-11-14 this plugin saves and reads product files in `.agents_workspace/product/`.
