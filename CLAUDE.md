# CEH Claude Code Library

Plugin repo for the `ceh-*` Claude Code plugins — engineering standards delivered as skills.
Each plugin is a standalone, self-contained **use case**. Migration from
[agent-skills](https://github.com/cheneeheng/agent-skills) is in progress: plugins land here one at
a time, and the tables below grow as they do.

## Organizing Principle

Plugins split on one axis: **use case**. Two consequences drive how skills are written and where
they live:

- **Skills trigger on moments, not topics.** A skill fires on a verb ("I'm opening a PR"), not a
  noun ("PostgreSQL"). Topic-named skills either never auto-trigger or restate what the model
  already knows, so each skill is cut to the repo-opinionated delta.
- **Plugin names declare their scope.** `ceh-python-service` vs `ceh-python-library` — the name
  states the use case and makes gaps obvious.

Plugins fall into four tiers:

| Tier                  | Loaded            | Plugins                                            |
| --------------------- | ----------------- | -------------------------------------------------- |
| **Scenario bundle**   | one per situation | —                                                  |
| **Cross-cutting**     | most sessions     | `ceh-core`, `ceh-coding-agent`, `ceh-git-workflow` |
| **Use-case workflow** | per activity      | `ceh-architecture`                                 |
| **Stack / build**     | per project type  | —                                                  |

The scenario tier is the install entry point, not a fourth axis: a bundle is a manifest with
`dependencies` and nothing else — no skills, agents, or hooks. `-greenfield` depends on its own
`-iterate` twin plus the planning delta, so the phase transition is a no-op. Every other bundle
depends on `ceh-scenario-core` instead of listing the cross-cutting base itself. Experimental
plugins never enter a bundle. **Name the phase halves `-greenfield` / `-iterate`, never
`-maintenance`** — "maintenance" reads as bugfix-only.

Categorization rules of thumb:

- **Framework variants do not split into separate plugins** when their skills trigger on disjoint
  file types. Splitting duplicates the shared standards and reintroduces drift.
- **A foundational standard needed by more than one use-case plugin is duplicated into each**, not
  extracted into a shared base plugin — see the Shared-Standards Duplication Policy below.
- **Scenario bundles live in `plugins/`** like everything else. The `ceh-scenario-` prefix carries
  the distinction and `validate.py` enforces the structural invariant (manifest + README only).
- **App-specific patterns are not standards.** Anything bound to one application's schema or design
  is removed rather than kept as a niche plugin.
- **`ceh-core` admits only what holds however Claude Code is used** — coding, writing, research,
  or ops. If a component assumes a repository, code, or a specific activity, it belongs elsewhere.
  "Useful almost everywhere" is not the test; that is how a core plugin becomes a dumping ground.
- **The cross-cutting tier is orthogonal by construction.** It holds a discipline that applies
  whatever you are building, so it loads _alongside_ a use-case plugin, never instead of one.
- **Technique splits from tooling when the technique is genuinely stack-agnostic.** The test:
  would the content be byte-identical across stacks? If a technique skill grows stack-specific
  branches, it was tooling all along.

## Structure

```
.agents_workspace/            # Session artifacts, git-ignored in full: DECISION_LOG.md, skill-evals/
.claude/skills/               # Repo-local skills — add-plugin-component and its templates (assets/)
.claude-plugin/               # Marketplace manifest (marketplace.json)
archive/                      # Retired plugins or plugin contents — unpublished, not validated
.github/workflows/            # validate.yml — runs validate.py on push and PR
docs/                         # Maintainer docs — CROSS_REFERENCES.md, PLUGIN_DEPENDENCIES.md, ENVIRONMENT_VARIABLES.md
plugins/                      # All plugins — flat, one directory per plugin, no tier subfolders
├── ceh-scenario-<name>/      # Scenario bundle — .claude-plugin/plugin.json + README.md ONLY
└── ceh-<plugin-name>/
    ├── .claude-plugin/           # plugin.json — version and dependencies live here
    ├── agents/                   # Optional — subagents, one <name>.md each
    ├── hooks/                    # Optional — hooks.json wiring scripts via ${CLAUDE_PLUGIN_ROOT}
    ├── output-styles/            # Optional — output style .md files
    ├── scripts/                  # Optional — hook scripts and shell helpers
    └── skills/
        └── <skill-name>/
            ├── SKILL.md               # Required — frontmatter + full body, all content inline
            └── references/            # Sparingly — see Skills below
tools/
└── validate-plugins/          # The CI gate — stdlib-only Python, own README.md
```

## Plugins

| Plugin directory   | Domain                                                                                                                                                                                                                        |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ceh-core`         | Standards that hold however Claude Code is used: usage-limit handoff, context economy via delegated bulk reads                                                                                                                |
| `ceh-coding-agent` | Agent behavior contract, write-less-code minimalism, retroactive refactoring, repo explanation                                                                                                                                |
| `ceh-git-workflow` | Branching, commits, pull requests from open to merge (`pull-request`, which also lands a branch in one pass), changelog entries, releases including hotfixes (`release`, which also runs the full ship sequence), code review |
| `ceh-architecture` | Living `ARCHITECTURE.md` (Mermaid diagrams + Key Decisions log), domain modeling (IDs, status enums, layer boundaries), invariants injected by a SessionStart hook                                                            |

## Skills

Every new `SKILL.md` and `agents/*.md` starts as a copy of the templates in
`.claude/skills/add-plugin-component/assets/`, so every component shares one frontmatter order,
one heading set, and one voice. Frontmatter uses only the fields in the official Claude Code
[skills](https://code.claude.com/docs/en/skills#frontmatter-reference) and
[subagents](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields) references.

Each skill is self-contained with inline content. `references/` is for two cases only:

- **A schema or template used by several skills**, copied word-for-word into each consumer and
  registered in `docs/CROSS_REFERENCES.md`.
- **A standards set too large to inline.**

Never for general reference material a model already knows.

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

`user-invocable: false` on any skill the user will not call by name, which includes every skill a
hook names (`agent-coding-contract`, `write-less-code`, `usage-limit-handoff`,
`delegate-bulk-reads`, `branch`). Its root `README.md` Invoke cell reads
`Model-only, no slash command`.

When a hook names the skill on every firing, the description is **one line**: what the skill is,
with no trigger phrases and no mention of the hook. Keep the full description when the model also
loads the skill unprompted (`write-less-code`, `branch`).

## Plugin Dependencies

**Declare `dependencies` in `plugin.json` only, never in the `marketplace.json` entry.** Bare
strings, no version ranges. Dependencies install and enable automatically and transitively; there
is **no optional dependency**.

Two rules decide whether a cross-plugin reference earns a dependency:

- **It must fire on every run of the skill.** A conditional handoff stays prose.
- **Negative routing never counts.** `Not for tagging, use ceh-git-workflow:release` names an
  alternative; a dependency there installs what the user steered away from.

**A cross-cutting plugin may depend only on other cross-cutting plugins.** Where a dependency
exists, the skill body calls the target explicitly —
`Invoke the Skill tool with skill="ceh-<plugin>:<skill>"` — and `validate.py` rejects the call if
the target does not resolve, is not a declared dependency, or sets `disable-model-invocation: true`.
The current graph and the evidence for each edge live in `docs/PLUGIN_DEPENDENCIES.md`.

## Adding a Component

The repo-local skill `.claude/skills/add-plugin-component/` is the single checklist for adding or
changing a skill, agent, hook, script, or a whole new plugin. It auto-loads when a `SKILL.md` or
`agents/*.md` is created; load it explicitly if it has not.

Whatever else gets skipped, these four land in the **same commit** or CI fails:

1. A row in the root `README.md` table (Skills or Agents).
2. A row in `plugins/ceh-<plugin>/README.md`.
3. A version bump in **both** `plugins/ceh-<plugin>/.claude-plugin/plugin.json` and
   `.claude-plugin/marketplace.json` — level per the Versioning section below.
4. `python tools/validate-plugins/validate.py` green.

## Commands

```bash
# Find a skill by name across all plugins
find plugins -path '*skills/<name>/SKILL.md'

# Show every declared dependency edge
grep -H '"dependencies"' plugins/*/.claude-plugin/plugin.json

# Validate the whole repo — CI runs this too
python tools/validate-plugins/validate.py

# Strict YAML parse check of one plugin's skills and agents
claude plugin validate plugins/ceh-<plugin>
```

`validate.py` fails on any `ceh-<plugin>:<name>` mention, prose included, that no longer resolves,
so renaming a skill means grepping for its old name. It shellchecks `scripts/*.sh` only when
`shellcheck` is installed. CI has it, so a local green run on Windows can still fail CI.

The pre-commit hook runs prettier and **aborts the commit when it reformats a file**, which any
Markdown table edit can trigger. Re-stage and commit again, and chain the push with `&&`, never
`;`, so a failed commit does not push.

## Versioning

Two independent layers.

**Per-plugin versions** (load-bearing for auto-update) live in `plugin.json`, mirrored in
`marketplace.json`, and both must be bumped in the same commit. Bump at commit time, not during
iterative edits.

- **PATCH** — content or description updates.
- **MINOR** — a new skill or agent, or adding/removing a `dependencies` entry.
- **MAJOR** — the plugin is renamed or removed.

**The repo git tag** (e.g. `v1.2.0`) marks a consistent state of all plugins together and is a
changelog anchor only — it does not drive auto-update. MINOR when any plugin adds a skill or agent,
PATCH for content-only. Cut it after bumping plugin versions, and add a `CHANGELOG.md` entry: prose
on what changed and why, a `### Plugin versions` table listing every plugin bumped, then
`### Added` / `### Changed` / `### Fixed`.

## Key Files

| File                                              | Purpose                                                                        |
| ------------------------------------------------- | ------------------------------------------------------------------------------ |
| `plugins/ceh-<plugin>/.claude-plugin/plugin.json` | Plugin version, metadata, dependencies                                         |
| `.claude-plugin/marketplace.json`                 | Marketplace listing (all plugins)                                              |
| `README.md`                                       | User-facing docs — plugin, skill, and agent tables live here                   |
| `docs/CROSS_REFERENCES.md`                        | Content duplicated across skills: canonical source and every copy              |
| `docs/PLUGIN_DEPENDENCIES.md`                     | Current dependency graph: every edge with its evidence                         |
| `docs/ENVIRONMENT_VARIABLES.md`                   | Every environment variable any plugin reads: plugin, reader, default, effect   |
| `CHANGELOG.md`                                    | Release notes per repo tag, each with a `### Plugin versions` table            |
| `.claude/skills/add-plugin-component/assets/`     | `SKILL.template.md` and `agent.template.md` — the base for every new component |
| `.agents_workspace/DECISION_LOG.md`               | Agent decision log — **git-ignored, local only**, append-only                  |

## Cross-Reference Rule

Before editing any skill, check `docs/CROSS_REFERENCES.md`. If the section you are changing appears
there, edit the canonical file first, then mirror the change to every listed copy in the same
session. New duplication gets a new entry.

## Shared-Standards Duplication Policy

Each use-case plugin must be self-contained so a user loads exactly one plugin per use case. When a
foundational standard is needed by more than one, **duplicate the delta into each** rather than
extracting a shared base plugin. The cost is drift; the required mitigation is to register every
duplicated block in `docs/CROSS_REFERENCES.md` and propagate edits in the same session.
