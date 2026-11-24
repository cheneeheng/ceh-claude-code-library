# ceh-documentation

User-facing documentation for a project: a full docs set under `docs/`, task-oriented guides and
operator runbooks, an exhaustive reference, concept pages with sourced design rationale, and
runnable examples. Every command, flag, default, and rationale comes from the code or its history.
Anything unverified is marked `[VERIFY: …]`, never invented.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). Nothing else is required. Each skill
degrades instead of failing:

| Needs                                                                            | For                                                                                                                               | Without it                                                                  |
| -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| git CLI on PATH                                                                  | "Added in" markers and commit-sourced design rationale                                                                            | The markers come from `CHANGELOG.md` alone, and commit rationale is skipped |
| The target project's own runtime (Python and venv or uv, Node or Bun, cargo, go) | Running samples and examples                                                                                                      | They are written and reported as not run                                    |
| [uv](https://docs.astral.sh/uv/)                                                 | `write-concept-docs` checks `ARCHITECTURE.yaml` against its format before reading it, installing pydantic and PyYAML on first use | The file is read unchecked                                                  |
| Network access                                                                   | Only `write-examples` recipes that declare their own dependencies, fetched into a throwaway environment                           | Everything else works                                                       |

The plugin installs no docs framework.

## Skills

| Skill                       | Say or type                                                                                                  | What it does                                                                                                                                                                                          |
| --------------------------- | ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `write-project-docs`        | "document this project", "build out the docs folder", `/ceh-documentation:write-project-docs [project-path]` | Writes a full docs set: index, why, quickstart, guides, concepts, reference, examples, migration, one job per page. It runs the three skills below and itself in order.                               |
| `write-guides-and-runbooks` | "write a user guide", "ops runbook", "getting-started guide", `/ceh-documentation:write-guides-and-runbooks` | Writes or revises user guides (`docs/guide/`) and operator runbooks (`docs/operations/`): one section per audience, the right document type, task-oriented procedures you can verify.                 |
| `write-api-reference`       | "write the API reference", "document every endpoint", `/ceh-documentation:write-api-reference`               | Writes the exhaustive layer: every public item, counted against the surface, alphabetical within kind, "Added in" markers for the last three releases, rationale behind "Why" links.                  |
| `write-concept-docs`        | "explain how this works in the docs", "write a concepts section", `/ceh-documentation:write-concept-docs`    | Writes the "why" layer: a mental model per concept, design rationale sourced from ADRs, commits, and the changelog, never invented.                                                                   |
| `write-examples`            | "write examples for this project", "add usage examples", `/ceh-documentation:write-examples [project-path]`  | Writes new runnable programs under `examples/` in two tracks: a numbered `tour/` showing new users the top features, and `recipes/` a user copies into their own project, each run before it is kept. |

Pass a path to work on another project: `/ceh-documentation:write-project-docs ../my-lib` or
`/ceh-documentation:write-examples ../my-lib`.

## Agents

This plugin has no agents.

## Hooks

This plugin has no hooks.

## Settings

This plugin reads no settings.

## How it works

### One format for every page

Every skill writes Markdown under `docs/` in one fixed format:

- **Layout**: `docs/index.md` front page, site-level `why.md` / `migration.md`, and the sections
  `guide/` (the user's tasks), `operations/` (the operator's runbook), `concepts/`, `reference/`,
  `examples/`, each with an `index.md` hub
- **One mode per page**: tutorial, how-to, concept, reference, or example. A page needing two is
  two pages
- **File naming**: numbered folders use `<PREFIX>-<NN>-<name>.md` with fixed prefixes (`HT`, `OP`,
  `TS`, `CO`, `EX`), contiguous from `01`. Reference pages are named after the code, never numbered
- **Page anatomy**: one H1 (repeating the ID on numbered pages), a breadcrumb to the nearest hub, a
  one-to-two-sentence summary, and a prev · hub · next footer on numbered pages
- **Markdown that survives a renderer**: blank lines around every block, a language tag on every
  fence, Mermaid for diagrams, relative `.md` links with verified anchors
- **Fixed markers**: `[VERIFY: …]`, `_Added in vX.Y._`, the deprecation, warning, and note
  blockquotes
- **One report shape**: a page table plus **Open items** listing every unverified claim

### File naming: two rules worth knowing

**Numbers stay contiguous.** The number carries reading order, so there are never gaps. Appending a
page at the end takes the next number and renumbers nothing. Inserting or deleting one renumbers
the rest of that folder, and every link to a renamed file is updated in the same pass.

**The scheme beats the docs system.** Docusaurus, MkDocs and mdBook derive nav order from
filenames, which would otherwise compete with the prefix. It does not get to: nav order and page
metadata are expressed in frontmatter or nav config, never by renaming a file out of the scheme.

### Document types supported

| Type                        | Reader's goal                    |
| --------------------------- | -------------------------------- |
| Getting Started             | Go from zero to first success    |
| How-To Guide                | Accomplish one specific task     |
| User Manual                 | Reference for the whole product  |
| Operator Runbook            | Operate and recover a system     |
| Installation / Config Guide | Stand the system up correctly    |
| Troubleshooting Reference   | Diagnose and fix a known failure |

## Not this plugin

- The README: `ceh-git-workflow:update-readme`.
- The changelog: `ceh-git-workflow:update-changelog`.
- A maintainer architecture document: `ceh-codebase-explanation:document-architecture`. A
  per-module codebase walkthrough: `ceh-codebase-explanation:explain-codebase`.

## Where its files live

The docs go to the project's `docs/` and the examples to its `examples/`. The plugin saves and reads
product files in `.agents_workspace/product/`. A project with a root `product/` folder moves each
file to the same sub-path under `.agents_workspace/product/`, or names its own location in
`CLAUDE.md`.
