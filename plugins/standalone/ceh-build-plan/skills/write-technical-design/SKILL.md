---
name: write-technical-design
description: >-
  Load this skill when settling the technical design several features share, before any is
  planned: stack, components and data model, in ARCHITECTURE.yaml. Trigger on "write the
  technical design", "pick the stack". Not for what is already built (use
  ceh-codebase-explanation:document-architecture).
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Checking and rendering ARCHITECTURE.yaml needs uv; without it the file is saved unchecked and
  its Markdown is not rendered.
license: Apache-2.0
---

# Write the technical design

Settle the technical decisions that several features share, before the first of them is planned,
and write them into `.agents_workspace/product/ARCHITECTURE.yaml`: each decision as a Key
Decisions entry, and each diagram of what is not built yet marked `planned: true`. A build plan
then follows these decisions and never decides them again for one feature. Done means the file
passes its check and the tests below, and the reply lists every decision, diagram and answer
assumed.

## What belongs here

A decision belongs in the technical design when two or more features depend on it, or when
reversing it would cost a migration or a refactor:

- the stack and runtime
- persistence and the core data model
- the components and their boundaries
- the interface between components
- who owns each resource, and how a caller is authenticated
- the deployment target
- how configuration and errors are handled across components

A decision one feature alone needs stays for that feature's build plan.

## Procedure

1. **Check and read what exists.** For each of `ARCHITECTURE.yaml`, `PRD.yaml`, `VISION.yaml` and
   `STRATEGY.yaml` in `.agents_workspace/product/` that exists, run
   `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check <file>.yaml` before reading it
   (formats in `${CLAUDE_SKILL_DIR}/references/architecture-schema.md`, `prd-schema.md`,
   `vision-schema.md` and `strategy-schema.md`). On exit 1, stop and report its errors, because
   a design built on a broken source carries the error into every plan. On exit 2 or 3, or
   without uv, say in the reply that the file went unchecked, and go on. A vision or strategy
   kept as `.md` in `docs/`, the root, or where the repo's `CLAUDE.md` says is read as it is.
   Then read the `design` of each plan in `.agents_workspace/product/plan/`, the README, and the
   code. Read no business plan. With no PRD, take the features from the request and the vision,
   and say so.
2. **List the decisions the features need,** per What belongs here. For each, write down the
   options and the one chosen with its reason. A decision the log already holds as `Accepted`
   is kept: to change it, write a new entry and mark the old one `Superseded by <date> <title>`.
3. **Ask the owner one round of questions,** each with a recommended answer, for what only they
   know: a stack they require, a hosting account, a budget. Decide everything else yourself.
4. **Append each decision to `key_decisions`** with `status: Accepted`. `context` holds the
   options considered and the features that need the decision, `decision` what was chosen, and
   `consequences` the trade-off.
5. **Draw the diagrams the decisions imply,** each with `planned: true`: Components, and Data
   model and Key flows when the product has them. A new file also gets its Overview. Leave a
   diagram that shows built code as it is. When the design changes what such a diagram shows,
   add a second entry of the same `name` right after it, marked `planned: true` and showing the
   whole target. It replaces the built entry once the code matches it.
6. **Run the tests below,** and rewrite or cut what fails.
7. **Render.** Run `artifact.py render` on the file and fix the YAML for each error it lists.
   When the Mermaid CLI can run, render each new Mermaid block with
   `npx -p @mermaid-js/mermaid-cli mmdc -i <file>.md -o <out>.md` and look at the images.
   Otherwise say in the reply that the diagrams were not rendered.

## The tests

| Test       | Ask                                                                  | Fails when                                          |
| ---------- | -------------------------------------------------------------------- | --------------------------------------------------- |
| Shared     | Which two features need each decision, or what would reversing cost? | One feature, cheap to reverse: it belongs in a plan |
| Options    | Does each `context` name an option rejected and why?                 | Only the chosen option appears                      |
| Covers     | Which component serves each feature in the PRD?                      | A feature has none                                  |
| Qualities  | Which decision answers each `non_functional` item in the PRD?        | An item has none and is not listed as open          |
| Consistent | Does every diagram show only what the decisions say?                 | A node or entity has no decision behind it          |

With no PRD, run Covers against the features taken in step 1 and mark Qualities
`not run: no PRD`.

## Rules

- Never delete or edit an `Accepted` decision. A changed decision is a new entry, and the old
  one is marked `Superseded`, so the trail stays whole.
- Mark every diagram of what is not built `planned: true`, and never mark one that shows built
  code. `ceh-build-plan:implement-from-plan` and `ceh-codebase-explanation:document-architecture`
  remove the mark once the code matches the diagram.
- Write the YAML only. `ARCHITECTURE.md` is rendered from it.
- The file carries no pricing, unit economics, or any test, stage or date from a business plan.

## Output

`.agents_workspace/product/ARCHITECTURE.yaml`, unless the repo's `CLAUDE.md` names another path,
in the shape of `${CLAUDE_SKILL_DIR}/assets/architecture.template.yaml`, per the
`architecture/v3` section of `${CLAUDE_SKILL_DIR}/references/architecture-schema.md`. A missing
file starts as a copy of the template, and an `ARCHITECTURE.md` with no YAML is moved first, as
that section says. `ARCHITECTURE.md` is rendered beside it and never edited by hand.

Close the reply with the path, each decision by its title, each diagram drawn, the result of each
test, and every answer assumed.

## Stop conditions

- **No human to answer** (a headless run, or called by another agent): ask nothing. Take each
  recommended answer, write the decisions, and end with each question and the answer assumed, so
  the owner can supersede a decision they disagree with.

## Hands off to

- To plan the first feature on this design, suggest `ceh-build-plan:write-build-plan`.
