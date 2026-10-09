# Plan format

A build plan is one Markdown file. `ceh-build-planning` writes it, `ceh-build-from-plan` builds
from it and records evidence in it, and `ceh-check-build-against-plan` checks the code against it.
This file is copied word for word into all three plugins, so each works installed alone.

## Location

`docs/plans/<slug>.md` in the target repo, committed, unless the repo's `CLAUDE.md` names another
plans folder. A plan shapes the repo for whoever builds next, so it lives where a fresh clone and a
reviewer can read it. `<slug>` is kebab-case from the goal: `mvp`, `checkout-flow`.

## Frontmatter

```yaml
---
title: <what this plan builds, one line>
status: draft # draft | ready | building | built
created: YYYY-MM-DD
business_plan: <path to BUSINESS_PLAN.md> # omit when there is none
---
```

- `draft`: an Open question blocks building. `ready`: buildable as written. `building`: at least
  one phase is done. `built`: every phase is done, with evidence.

## Sections, in this order

```markdown
## Goal

One paragraph: what gets built, for whom, and the one user flow that matters most. With
`business_plan` set, one sentence plus a pointer to its product section instead.

## Scope

**In:** one bullet per capability a user or caller can observe. This list is what done means.

**Out:** one bullet per thing deliberately not built, with a one-line reason.

## Design

Only the decisions the phases need, each with its reason: stack, components (a Mermaid diagram when
there are more than two), data model (entities and key fields), and interface (routes with method
and path, CLI commands, or public functions). Each decision is written once here, and phases refer
to it.

## Phases

### Phase 1: <name>

- **Builds:** what this phase adds, named by its Scope and Design items.
- **Check:** the command that proves it and what passing looks like, e.g.
  `uv run pytest tests/test_signup.py` passes.
- **Status:** todo

## Open

Each unsettled question, with the assumption taken until it is answered. "None" when empty.
```

## Phase rules

- Phases run in order. Each is buildable from the phases before it and leaves the app runnable.
- Every phase has a runnable Check. A phase no command can prove is merged into the next one, or
  names its manual check and why no command can do it.
- **Status** is `todo`, `unplanned` (a one-line placeholder that must be planned before it is
  built), or `done` followed by its evidence: the commit, or the check's command, and one line of
  its passing output.

## Changing a plan

- A builder that departs from Design edits the Design line and gives the reason in that phase's
  Status, so the plan stays true to the code.
- A `built` plan is history. New work gets a new plan file.
