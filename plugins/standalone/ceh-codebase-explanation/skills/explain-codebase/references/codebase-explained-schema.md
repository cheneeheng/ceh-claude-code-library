# Codebase explained schema

The orientation file `explain-codebase` writes, `.agents_workspace/CODEBASE_EXPLAINED.md`,
overwritten on every run. A new file is a copy of `../assets/codebase-explained.template.md`,
relative to this file: its frontmatter, then its sections in that order. The
`schema: codebase-explained/v1` line stays as written.

## Frontmatter

- `repo`: the repo name.
- `generated`: the run date.
- `commit`: the commit the run read.
- `kind`: `code repo` or `knowledge base`.
- `components`: the number of components described.
- `files_accounted`: files assigned to a component or covered by a group rule.
- `files_excluded`: files excluded from the inventory.

## Sections

- **What this repo is:** 2 to 4 sentences: what it does, who it is for, what kind of project it is,
  and what stack it runs on. For a knowledge base: what subjects it covers, who it is written for,
  and how it is organized.
- **How it fits together:** a Mermaid `flowchart LR` of the components, then one paragraph naming
  the moving parts and the direction things flow.
- **Components:** one `### \`<path>\` — <role>` per component, in the four-part shape below.
- **Key flows:** one `###` per flow, a numbered list of `<file> → <step>` lines.
- **Repo meta:** the support cast as group rules: CI workflows, packaging config, editor and lint
  config, license.
- **Gaps and oddities:** factual observations only: dead code, missing CI, a component whose
  purpose could not be determined and what was checked.
- **Accounting:** the file counts. Excluded covers `.agents_workspace/`, lockfiles, and binaries.

## Worked example

A component in the four-part shape, and a key flow:

```markdown
### `src/api/` — HTTP surface

**What it is.** Route handlers; no business logic.
**What's inside.** `auth.py` issues the JWT every other route verifies; `deps.py` holds the FastAPI
dependencies (DB session, current user). The remaining 9 modules are one resource each, all built on
the same `deps.py` pair.
**How it connects.** Registered by `main.py` on startup; calls `services/`. Owns no state.
**Before you change it.** Route paths are duplicated in `tests/conftest.py`.

### Authenticated request

1. `main.py` → routes registered at startup
2. `api/deps.py` verifies the token
3. `services/user.py` loads the record
4. `store/pg.py` runs the query
```
