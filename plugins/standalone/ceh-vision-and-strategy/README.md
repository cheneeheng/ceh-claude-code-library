# ceh-vision-and-strategy

Write down a repo's direction so later decisions can be settled from it: `VISION.md`, why the repo
exists and which principles decide, and `STRATEGY.md`, how it gets there and how work is chosen. The
repo can hold code or only documents.

## Skills

| Skill                       | When it loads                                                              | What it does                                                                                                                                                                                                                                                                                               |
| --------------------------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `write-vision-and-strategy` | A repo's direction must be written down, or an existing doc needs revising | Drafts both docs from what the repo shows, interviews the owner only on what it cannot show, tests that the docs settle real decisions, and points `CLAUDE.md` at them once confirmed. It's working if the first run writes both files with `status: draft` and `[assumed]` marks before it asks anything. |

**Manual trigger:** `/ceh-vision-and-strategy:write-vision-and-strategy`, or say
`"write the vision doc"` / `"create a strategy doc"`.

## What it writes

`product/VISION.yaml` and `product/STRATEGY.yaml`, or wherever the repo already keeps the docs, with
`VISION.md` and `STRATEGY.md` rendered beside them. The skill writes the files, and you commit them.
Only an `adopted` doc gets a pointer from `CLAUDE.md`, so an assumption never binds a later
session.

## Hooks

After every write to either YAML, `artifact-render-hook.py` (`PostToolUse`) checks it against its
model through `uv` and renders the Markdown, or reports each error back to the agent and leaves the
Markdown as it was. An adopted doc that still holds `[assumed]` is one such error. The skill reads
no business plan: the vision feeds the business plan, never the reverse.
`generated-md-guard.py` (`PreToolUse`) denies a direct edit to a generated Markdown file and names
its YAML. Both need `uv`: without it the agent is told once per session that the file went
unchecked. `CEH_ARTIFACT_CHECK=off`, or `CEH_DISABLED_HOOKS` with `artifact-render-hook` or
`generated-md-guard`, switches them off.

## Not this plugin

- Whether a product is worth building, and who pays: use `ceh-business-plan`. Its material stays
  private, and these docs are committed, so they carry no pricing or unit economics.
- How to build one feature: use `ceh-build-plan`, which reads these docs when they exist.
- Docs for users of the product: use `ceh-documentation`.
