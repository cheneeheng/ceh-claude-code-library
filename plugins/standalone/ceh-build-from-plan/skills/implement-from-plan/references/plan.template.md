---
schema: plan/v1
title: <what this plan builds, one line>
status: draft # draft | ready | building | built
created: YYYY-MM-DD
business_plan: <path to product/BUSINESS_PLAN.md> # omit when there is none
---

## Goal

<One paragraph: what gets built, for whom, and the one user flow that matters most. With
`business_plan` set, one sentence plus a pointer to its product section instead.>

## Scope

**In:** <one bullet per capability a user or caller can observe. This list is what done means.>

**Out:** <one bullet per thing deliberately not built, with a one-line reason.>

## Design

<Only the decisions the phases need, each with its reason: stack, components (a Mermaid diagram
when there are more than two), data model (entities and key fields), and interface (routes with
method and path, CLI commands, or public functions). Each decision is written once here, and
phases refer to it.>

## Phases

### Phase 1: <name>

- **Builds:** <what this phase adds, named by its Scope and Design items.>
- **Check:** <the command that proves it and what passing looks like, e.g.
  `uv run pytest tests/test_signup.py` passes.>
- **Status:** todo

## Open

<Each unsettled question, with the assumption taken until it is answered. "None" when empty.>

## Record

<Append-only, oldest first: one dated line per lifecycle event. See Record rules in
plan-format.md.>
