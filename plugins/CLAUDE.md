# Plugin Authoring Rules

Loaded when working under `plugins/`. Repo-wide rules stay in the root `CLAUDE.md`.

The authoring decisions live in `.claude/rules/`, scoped to `plugins/**` and `.claude/skills/**`:
`decision-component-templates.md`, `decision-skill-bundled-files.md`,
`decision-output-templates.md`, `decision-component-names.md`, `decision-frontmatter-scalars.md`,
and `decision-invocation-flags.md`. This file explains how they are checked and applied.

## Skills

`validate.py` (the `templates` check) rejects a template without its schema line or its schema
file, a template that carries explanation, a template or schema no file in its plugin cites, a copy
that differs from its twin in another plugin, and a skill whose `## Output` names a saved
`.agents_workspace/` or `product/` file but cites no template.

The two migrated catalog skills keep their bundled files for this reason.
`ceh-ui-design:design-ui` carries two themes and `examples.md` under `references/`, and
`ceh-web-frontend:visualize-graph-cytoscape` carries six reference files, an
`assets/template.html`, and a `scripts/to-elements.js` converter. The Cytoscape API and stylesheet
references were cut on 2026-10-08 as material the model already knows. On the same day
`design-ui`'s `examples.md` was cut to the finishing recipes, the markup the core rules' prose does
not already carry. Both stay because each is a catalog a run reads only part of: `design-ui`
installs one of its two themes, and `visualize-graph-cytoscape` opens the topic file its task
touches.

The allowed scaffold and script bundles are `ceh-ag-ui` (`build-ag-ui`, `build-ag-ui-agent`
`assets/`), `ceh-git-datastore` (`build-git-datastore`, `migrate-git-datastore` `references/` +
`scripts/`), and `ceh-business-plan` (the HTML generator in `scripts/`, with its page shell and
`brand.css` in `assets/`).

`validate.py` cannot check part of speech, so the naming rule is a review rule.

## Frontmatter

`validate.py` enforces the `>-` scalar and the 300-character limit. The skill listing has a budget
of 1% of the context window, and agent descriptions load into every session too.

```yaml
---
name: my-skill
description: >-
  Load this skill when doing X: the colon here is literal, as are "quotes",
  'apostrophes', backslashes and # hashes. Wrap at ~98 chars, 2-space indent.
---
```

`>-` is the only style with **no escaping burden**: every character is literal, and `-` strips the
trailing newline. A plain scalar cannot contain `: `, single-quoted needs `''` doubling,
double-quoted needs `\` and `"` escaping.

Two mechanical rules keep folding lossless: **uniform 2-space indent** on every continuation line (a
more-indented line becomes a literal newline instead) and **no blank lines** inside the block.

## Invocation

The validator checks that all three invocation keys are present, and that a skill a hook script
names sets `user-invocable: false`. The one exception is a script that names a skill only to detect
that it ran, listed by name in `NAMES_TO_DETECT` in `tools/validate-plugins/checks/repo_rules.py`
with its reason: today `build-record-guard.py`, which must accept `implement-from-plan`'s slash
command, and `skill-started-guard.py`, which must accept the slash command of every skill it
names. It also checks each user-only skill's row in `ceh-every-session:whats-next`.

Model only covers every skill a hook names (`agent-coding-contract`, `write-less-code`,
`usage-limit-handoff`, `delegate-bulk-reads`), the router-called `ceh-business-plan` specialists,
the path-scoped stack standards, and standards like `design-test-cases` and
`write-plain-language`. User only is rare because the library is agents-first: such a skill drops
out of the skill listing, so no natural-language request, agent, workflow stage, or
`Invoke the Skill tool` call can start it. Today it covers `refactor-repo` and the two
`ceh-orchestration-lab` skills. A standard that holds the whole session, such as
`write-less-code`, has no moment of its own, so the hook is its delivery and trigger phrases only
cost listing space.
