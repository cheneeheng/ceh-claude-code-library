# Plugin Authoring Rules

Loaded when working under `plugins/`. Repo-wide rules stay in the root `CLAUDE.md`.

## Skills

Every new `SKILL.md` and `agents/*.md` starts as a copy of the templates in
`.claude/skills/add-plugin-component/assets/`, so every component shares one frontmatter order,
one heading set, and one voice. Frontmatter uses only the fields in the official Claude Code
[skills](https://code.claude.com/docs/en/skills#frontmatter-reference) and
[subagents](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields) references.

Each skill is self-contained with inline content. `references/` is for two cases only. Output
templates (below) live in `assets/` instead:

- **A schema: the schema of an output template (below), or one used by several skills.** Skills
  of one plugin share a single copy in the
  plugin's own `references/`, cited as `${CLAUDE_PLUGIN_ROOT}/references/<file>`, so it needs no
  `docs/CROSS_REFERENCES.md` entry. A file used by one skill lives in that skill's `references/`.
  Only a file needed by skills of different plugins is copied word-for-word into each and
  registered in `docs/CROSS_REFERENCES.md` (see the Shared-Standards Duplication Policy in the
  root `CLAUDE.md`).
- **A standards set too large to inline.**

Never for general reference material a model already knows.

**Every file a skill saves has a versioned template**, `<schema>.template.md` in the skill's or
the plugin's `assets/` (cited as `assets/<file>` or `${CLAUDE_PLUGIN_ROOT}/assets/<file>`), its
frontmatter opening with `schema: <schema>/v<N>`. **Each template has a schema**,
`<schema>-schema.md` in the `references/` beside that `assets/` folder: it says where the file is
saved, names the template as `../assets/<schema>.template.md`, and explains every field and section.
The template is a bare skeleton, copied and filled as is: short placeholders (`<title>`) and
choices as `<a | b>`. Comments, explanation, and worked examples go in the schema. The skill body
cites both instead of spelling the format inline (`fills assets/x.template.md, per
references/x-schema.md`), so the format lives in one pair of files and the saved file names its
version. A reference file cites a sibling folder's file relative to itself (`../assets/<file>`),
never as "next to this file". Bump `v<N>` when a required field or heading is renamed or removed.
Out of scope: what the user ships (code, tests, docs pages, blog posts in a blog repo, `SKILL.md`
files a skill generates), `flow.yaml`, which carries its own `version: 1`, and a file a script
generates from a templated one, such as `BUSINESS_PLAN.html` built from `BUSINESS_PLAN.md`, which
carries the version for both. `validate.py` (the
`templates` check) rejects a template without its schema line or its schema file, a template that
carries explanation, a template or schema no file in its plugin cites, a copy that differs from
its twin in another plugin, and a skill whose `## Output` names a saved `.agents_workspace/` or
`product/` file but cites no template.

Two skills migrated whole and carry bundled files that predate this rule:
`ceh-ui-design:design-ui` (two themes and `examples.md` under `references/`) and
`ceh-web-frontend:visualize-graph-cytoscape` (six reference
files, an `assets/template.html`, and a `scripts/to-elements.js` converter). The Cytoscape API and
stylesheet references were cut on 2026-10-08 as material the model already knows. On the same day
`design-ui`'s `examples.md` was cut to the finishing recipes, the markup the core rules' prose does
not already carry. Both stay because each is a catalog a run reads only part of: `design-ui`
installs one of its two themes, and `visualize-graph-cytoscape` opens the topic file its task
touches. A rule that applies on every run stays inline, because a model can skip a link and never
see it. A new catalog skill argues its own exception in its PR.

Scaffold or script bundles a skill executes or copies are not reference material and are allowed:
`ceh-ag-ui` (`build-ag-ui`, `build-ag-ui-agent` `assets/`), `ceh-git-datastore`
(`build-git-datastore`, `migrate-git-datastore` `references/` + `scripts/`), and
`ceh-business-plan` (the HTML generator in `scripts/`, with its page shell and `brand.css` in
`assets/`).

**Name skills with a verb phrase and agents with a noun, and put the framework or library in the
name when a skill is specific to one** (`write-fastapi-endpoints`, `write-postgresql-code`,
`write-pytest-service-tests`), so the name says what the skill applies to. A skill is something you
do at a moment (`commit`, `shrink-diff`, `draft-post`, `make-page-crawlable`), an agent is something
you delegate to (`bulk-reader`). Pick the word you would say out loud, not a generic one like `optimize`. Two
exemptions: model-only standards named for what they carry (`agent-coding-contract`,
`usage-limit-handoff`), and established terms of art (`pull-request`, `release`).
`validate.py` cannot check part of speech, so this is a review rule.

These are the how of principle 10 in `docs/VISION.md`, "Names say what they do": anyone who has
seen only the name can say what the component does and when it is used. The same test covers
plugins and scripts. A plugin is named for its use case (`ceh-coding-conduct`, not
`ceh-coding-agent`), and a script for what it does (`inject-less-code-reminder.sh`, not
`less-code-payload.sh`). The `ceh-` prefix is a namespace, exempt from the test.

## Frontmatter Conventions

**`description` is always a folded block scalar (`>-`), never quoted and never plain.** Enforced by
`validate.py`.

**A skill or agent `description` is at most 300 characters**, also enforced by `validate.py`. The
skill listing has a budget of 1% of the context window, and once it overflows Claude Code drops
whole descriptions, so one long description costs another skill its trigger. Agent descriptions load
into every session too. For a skill, write the moment, two or three trigger phrases, and at most one
"Not for" pointer to the nearest look-alike. For an agent, write when to delegate (proactively, only
on request, or which skill dispatches it) and whether it is read-only. The body carries the rest.

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
their defaults, so the frontmatter says who invokes it. The validator checks that all three are
present, and that a skill a hook script names sets `user-invocable: false`. The other values are a
review rule, and every skill falls into one of three cases:

| Who starts it  | `disable-model-invocation` | `user-invocable` | Use it for                                                                                          |
| -------------- | -------------------------- | ---------------- | --------------------------------------------------------------------------------------------------- |
| Model only     | `false`                    | `false`          | Standards and gates the model applies at a moment, and skills a hook, router, agent, or skill calls |
| User only      | `true`                     | `true`           | Runs that are the human's decision to start: experiments, campaigns that wait on approval           |
| Model and user | `false`                    | `true`           | Everything else, the default: a task the user names that the model also starts at its moment        |

Model only is the usual choice when the user would never type the name. That covers every skill a
hook names (`agent-coding-contract`, `write-less-code`, `usage-limit-handoff`, `delegate-bulk-reads`),
the router-called `ceh-business-plan` specialists, the path-scoped stack standards, and
standards like `design-test-cases` and `write-plain-language`. Its `docs/CATALOG.md` Invoke cell
reads `Model-only, no slash command`.

User only is rare because the library is agents-first. Such a skill drops out of the skill listing
entirely, so a natural-language request no longer loads it, and no agent, workflow stage, or
`Invoke the Skill tool` call can start it. Today it covers `refactor-repo` and the two
`ceh-orchestration-lab` skills. A new one also gets a row in the User-only skills table of
`ceh-every-session:whats-next`, which cannot see it otherwise. `validate.py` checks that row.

When a hook names the skill on every firing, the description is **one line**: what the skill is,
with no trigger phrases and no mention of the hook. Keep the full description only when the model
also loads the skill unprompted at a moment of its own. A standard that holds the whole
session, such as `write-less-code`, has no such moment: no description fires it, so the hook is
its delivery and trigger phrases only cost listing space.
