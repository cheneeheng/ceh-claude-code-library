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

`product/VISION.md` and `product/STRATEGY.md`, or wherever the repo already keeps them. The skill
writes the files, and you commit them. Only an `adopted` doc gets a pointer from `CLAUDE.md`, so an
assumption never binds a later session.

## Not this plugin

- Whether a product is worth building, and who pays: use `ceh-business-plan`. Its material stays
  private, and these docs are committed, so they carry no pricing or unit economics.
- How to build one feature: use `ceh-build-planning`, which reads these docs when they exist.
- Docs for users of the product: use `ceh-documentation`.
