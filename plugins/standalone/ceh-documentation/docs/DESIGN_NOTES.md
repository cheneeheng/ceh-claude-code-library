# ceh-documentation design notes

## Where the docs format lives

The format lives in `references/docs-standard.md`, copied into each of the four writing skills,
which read their own copy through `${CLAUDE_SKILL_DIR}`.

## Why page numbers stay contiguous

The alternative, append-only numbers with gaps, was rejected because it turns the number into an
arbitrary ID, at which point numbering earns nothing. Revisit only if these filenames become
externally referenced (published URLs, tickets, support macros): stable IDs then beat reading
order.

## Boundaries

- README maintenance belongs to `ceh-git-workflow:update-readme`: every repo has a README, but only
  a software project needs a `docs/` set.
- Changelog maintenance belongs to `ceh-git-workflow:update-changelog`: every input it reads is
  git, so it fires on a git moment, not a documentation one.
