# Plugin Authoring Rules

Loaded when working under `plugins/`. Repo-wide rules stay in the root `CLAUDE.md`.

The authoring decisions live in `.claude/rules/`, scoped to `plugins/**` and `.claude/skills/**`:
`decision-component-templates.md`, `decision-skill-bundled-files.md`,
`decision-output-templates.md`, `decision-component-names.md`, `decision-frontmatter-scalars.md`,
and `decision-invocation-flags.md`. This file explains how they are checked and applied.

## Skills

`validate.py` (the `templates` check) rejects a template without its schema line or its schema
file, a template that carries explanation, a template or schema no file in its plugin cites, and a
skill whose `## Output` names a saved `.agents_workspace/` file but cites no template. The
`artifact-paths` check rejects a root `product/` path, and a `.md` path of a format with a YAML
source, anywhere under `plugins/standalone/` outside its allowlist, because every product artifact
lives in `.agents_workspace/product/` and is named by its `.yaml`. The `copies` check rejects a whole-file copy registered in `docs/CROSS_REFERENCES.md` that
differs from its canonical file, an identical copy left unregistered, a plugin root holding
`assets/` or `references/`, and a citation of either through `${CLAUDE_PLUGIN_ROOT}`.

The two migrated catalog skills keep their bundled files for this reason.
`ceh-ui-design:design-ui` carries two themes and `examples.md` under `references/`, and
`ceh-web-frontend:visualize-graph-cytoscape` carries six reference files, an
`assets/template.html`, and a `scripts/to-elements.js` converter. The Cytoscape API and stylesheet
references were cut on 2026-10-08 as material the model already knows. On the same day
`design-ui`'s `examples.md` was cut to the finishing recipes, the markup the core rules' prose does
not already carry, and on 2026-11-02 it took the rules of the recipes that apply only when their
component is present. Both stay because each is a catalog a run reads only part of: `design-ui`
installs one of its two themes, and `visualize-graph-cytoscape` opens the topic file its task
touches.

The allowed scaffold and script bundles are `ceh-ag-ui` (`build-ag-ui`, `build-ag-ui-agent`
`assets/`), `ceh-product-direction` (`develop-business-plan`'s HTML generator in `scripts/`, with its
page shell and `brand.css` in `assets/`), and each skill carrying a YAML format's
`<schema>-model.py` (its `scripts/artifact.py`, which checks and renders that format).

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
`usage-limit-handoff`, `delegate-bulk-reads`), the router-called `ceh-product-direction` specialists,
the path-scoped stack standards, and standards like `design-test-cases` and
`write-plain-language`. User only is rare because the library is agents-first: such a skill drops
out of the skill listing, so no natural-language request, agent, workflow stage, or
`Invoke the Skill tool` call can start it. Today it covers only `refactor-repo`. A standard that holds the whole session, such as
`write-less-code`, has no moment of its own, so the hook is its delivery and trigger phrases only
cost listing space.
