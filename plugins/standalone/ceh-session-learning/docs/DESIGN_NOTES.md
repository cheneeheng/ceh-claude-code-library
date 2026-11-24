# ceh-session-learning design notes

Maintainer detail moved out of the plugin README, word for word.

## Hook wiring

Two hooks on `Edit|Write|MultiEdit`, both Python scripts:

- `artifact-render-hook.py` (PostToolUse) checks a written session diagnosis YAML against its
  model and renders its Markdown. Without `uv` the agent is told once per session that the file
  went unchecked.
- `generated-md-guard.py` (PreToolUse) denies a hand edit to the generated Markdown, which the
  next render would overwrite. The `-shareable.md` copy carries no `generated_from` key, so its
  scrub edits pass.

The saved diagnosis is a `session-retro/v3` YAML.

## Product folder history

Since 2026-11-14 this plugin saves and reads product files in `.agents_workspace/product/`.
