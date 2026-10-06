# Plugin Authoring Rules

Loaded when working under `plugins/`. Repo-wide rules stay in the root `CLAUDE.md`.

## Skills

Every new `SKILL.md` and `agents/*.md` starts as a copy of the templates in
`.claude/skills/add-plugin-component/assets/`, so every component shares one frontmatter order,
one heading set, and one voice. Frontmatter uses only the fields in the official Claude Code
[skills](https://code.claude.com/docs/en/skills#frontmatter-reference) and
[subagents](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields) references.

Each skill is self-contained with inline content. `references/` is for two cases only:

- **A schema or template used by several skills.** Skills of one plugin share a single copy in the
  plugin's own `references/`, cited as `${CLAUDE_PLUGIN_ROOT}/references/<file>`, so it needs no
  `docs/CROSS_REFERENCES.md` entry. A file used by one skill lives in that skill's `references/`.
  Only a file needed by skills of different plugins is copied word-for-word into each and
  registered in `docs/CROSS_REFERENCES.md` (see the Shared-Standards Duplication Policy in the
  root `CLAUDE.md`).
- **A standards set too large to inline.**

Never for general reference material a model already knows.

Two `ceh-web-frontend` skills migrated whole and carry bundled files that predate this rule:
`design-ui` (two themes and `examples.md` under `references/`) and `visualize-graph-cytoscape` (eight reference
files, an `assets/template.html`, and a `scripts/to-elements.js` converter). Trim the Cytoscape
references to the repo-opinionated delta before adding more.

Scaffold or script bundles a skill executes or copies are not reference material and are allowed:
`ceh-ag-ui` (`build-ag-ui`, `build-ag-ui-agent` `assets/`) and `ceh-git-datastore`
(`build-git-datastore`, `migrate-git-datastore` `references/` + `scripts/`).

**Name skills with a verb phrase and agents with a noun, and put the framework or library in the
name when a skill is specific to one** (`write-fastapi-endpoints`, `write-postgresql-code`,
`write-pytest-service-tests`), so the name says what the skill applies to. A skill is something you
do at a moment (`commit`, `shrink-diff`, `draft-post`, `make-page-crawlable`), an agent is something
you delegate to (`bulk-reader`). Pick the word you would say out loud, not a generic one like `optimize`. Two
exemptions: model-only standards named for what they carry (`agent-coding-contract`,
`usage-limit-handoff`, `branch`), and established terms of art (`pull-request`, `release`).
`validate.py` cannot check part of speech, so this is a review rule.

## Frontmatter Conventions

**`description` is always a folded block scalar (`>-`), never quoted and never plain.** Enforced by
`validate.py`.

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

Every **other** frontmatter key containing `: ` must be quoted — single quotes by default
(`argument-hint: '[plan-file]'`). Short values that need no quoting stay bare (`effort: max`).

### `compatibility`

Optional, max 500 chars, same `>-` scalar as `description`. Present **only when running the skill
needs software the machine may not have** — a script interpreter, a CLI (`git`, `gh`, `uv`, `bun`,
`docker`), a reachable server, or network access. Name the runtime _and_ its minimum version and
what fails without it. A skill that only reads files and emits Markdown gets no `compatibility`.

### `user-invocable` and hook-loaded skills

Every skill states `disable-model-invocation`, `user-invocable`, and `license` explicitly, even at
their defaults, so the frontmatter says who invokes it. This is a review rule, not a validator check.

`user-invocable: false` on any skill the user will not call by name, which includes every skill a
hook names (`agent-coding-contract`, `write-less-code`, `usage-limit-handoff`,
`delegate-bulk-reads`, `branch`). Its root `README.md` Invoke cell reads
`Model-only, no slash command`.

When a hook names the skill on every firing, the description is **one line**: what the skill is,
with no trigger phrases and no mention of the hook. Keep the full description when the model also
loads the skill unprompted (`write-less-code`, `branch`).
