# ceh-documentation

User-facing documentation for a project: a full docs set under `docs/`, task-oriented guides and
operator runbooks, an exhaustive reference, concept pages with sourced design rationale, and
runnable examples. Every command, flag, default, and rationale comes from the code or its history.
Anything unverified is marked `[VERIFY: …]`, never invented.

## Skills

| Skill                       | Invoke                                         | Triggers when                                                                                                                                                                                              |
| --------------------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `write-project-docs`        | `/ceh-documentation:write-project-docs`        | Writing a full docs set for the workspace or a given project path: index, why, quickstart, guides, concepts, reference, examples, migration, one job per page. Sequences the three skills below and itself |
| `write-guides-and-runbooks` | `/ceh-documentation:write-guides-and-runbooks` | Writing or revising user guides (`docs/guide/`) and operator runbooks (`docs/operations/`): one section per audience, the right document type, task-oriented verifiable procedures                         |
| `write-api-reference`       | `/ceh-documentation:write-api-reference`       | Writing the exhaustive layer: every public item, counted against the surface, alphabetical within kind, "Added in" markers for the last three releases, rationale behind "Why" links                       |
| `write-concept-docs`        | `/ceh-documentation:write-concept-docs`        | Writing the "why" layer: a mental model per concept, design rationale sourced from ADRs, commits, and the changelog, never invented                                                                        |
| `write-examples`            | `/ceh-documentation:write-examples`            | Writing new runnable programs under `examples/` in two tracks: a numbered `tour/` showing new users the top features, and `recipes/` a user copies into their own project, each run before it is kept      |

Pass a path to work on another project: `/ceh-documentation:write-project-docs ../my-lib` or
`/ceh-documentation:write-examples ../my-lib`.

## Prerequisites

None of these is required. Each skill degrades instead of failing:

- **git CLI on PATH**: "Added in" markers and commit-sourced design rationale. Without it the
  markers come from `CHANGELOG.md` alone and commit rationale is skipped.
- **The target project's own runtime** (Python and venv or uv, Node or Bun, cargo, go): running
  samples and examples. Without it they are written and reported as not run.
- **Network access**: only for `write-examples` recipes that declare their own dependencies,
  fetched into a throwaway environment.

The plugin reads no environment variables and installs no docs framework.

## What it produces

Markdown under `docs/` in one fixed format, whichever skill writes the page. The format lives in
`references/docs-standard.md`, which lives once at the plugin root and is read by the four writing
skills through `${CLAUDE_PLUGIN_ROOT}`:

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
the rest of that folder, and every link to a renamed file is updated in the same pass. The
alternative, append-only numbers with gaps, was rejected because it turns the number into an
arbitrary ID, at which point numbering earns nothing. Revisit only if these filenames become
externally referenced (published URLs, tickets, support macros): stable IDs then beat reading
order.

**The scheme beats the docs system.** Docusaurus, MkDocs and mdBook derive nav order from
filenames, which would otherwise compete with the prefix. It does not get to: nav order and page
metadata are expressed in frontmatter or nav config, never by renaming a file out of the scheme.

## Document types supported

| Type                        | Reader's goal                    |
| --------------------------- | -------------------------------- |
| Getting Started             | Go from zero to first success    |
| How-To Guide                | Accomplish one specific task     |
| User Manual                 | Reference for the whole product  |
| Operator Runbook            | Operate and recover a system     |
| Installation / Config Guide | Stand the system up correctly    |
| Troubleshooting Reference   | Diagnose and fix a known failure |

## Boundaries

- README maintenance belongs to `ceh-git-workflow:update-readme`: every repo has a README, but only
  a software project needs a `docs/` set.
- Changelog maintenance belongs to `ceh-git-workflow:update-changelog`: every input it reads is
  git, so it fires on a git moment, not a documentation one.
- A maintainer architecture document belongs to `ceh-codebase-explanation:document-architecture`, and a
  per-module codebase walkthrough to `ceh-codebase-explanation:explain-codebase`.
