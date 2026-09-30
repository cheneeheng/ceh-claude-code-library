---
name: add-plugin-component
description: >-
  Load this skill when adding or changing anything under plugins/ in this repo: a skill, agent,
  hook, script, or a whole new ceh-* plugin, including migrating one from the old agent-skills
  repo. Covers which plugin it belongs in, the SKILL.md and agent templates every new file starts
  from, the frontmatter rules, and every registration chore that must land in the same commit
  (both README tables, docs/CROSS_REFERENCES.md, plugin.json + marketplace.json version bumps,
  validate.py). Trigger when a new SKILL.md or agents/*.md is being created, one is renamed or
  moved between plugins, a directory is added under plugins/, or the user says "add a skill", "add
  an agent", "new plugin component", "create a plugin", "new ceh plugin", "migrate this skill", or
  asks why validate.py is failing. Overrides plugin-dev and skill-creator advice that conflicts
  with this repo. Not for building a skill into another project's .claude/skills/ (use
  ceh-workflow-builder:build-agentic-workflow).
argument-hint: "[skill-or-agent-name]"
---

# Adding a Component to This Repo

Every new `SKILL.md` or `agents/*.md` starts as a copy of its template, then gets registered in
the same commit. The content is the easy half. The half that gets forgotten is registration: the
same fact lives in both READMEs, both manifests, and sometimes `docs/CROSS_REFERENCES.md`, and CI
fails when they drift.

## 1. Pick the plugin and the component type

Plugins split on **use case**, not tech domain or lifecycle phase. Load exactly one plugin per
use case, so each must be self-contained. The tiers are defined in `CLAUDE.md`.

- A skill triggers on a **moment** (a verb: "I'm opening a PR", "I'm writing a migration"), never
  a **topic** (a noun: "PostgreSQL"). Topic-named skills either never auto-trigger or restate what
  the model already knows. If you cannot name the moment, the skill is not ready.
- Framework variants do **not** get their own plugin when their skills trigger on disjoint file
  types — `sveltekit` and `react-vite` share `ceh-web-frontend`.
- A foundational standard needed by two use-case plugins is **duplicated into both**, never
  extracted into a shared base plugin. Register the duplication (step 4).
- App-specific patterns are not standards. Anything bound to one application's schema or design
  gets removed, not filed as a niche plugin.

If no existing plugin owns the use case, create one first — see [New plugin](#new-plugin) — then
continue at step 2.

Then pick the component type by what the need is:

| Need                                                                             | Component                                   | Settle before writing                                                                            |
| -------------------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Knowledge or a procedure Claude applies at a moment, or a user-invoked `/action` | Skill                                       | Trigger phrases, what it adds beyond model knowledge, arguments, tools, interactive or automated |
| An autonomous task whose output or cost should stay out of the main session      | Agent                                       | Proactive or on request, tool set, model, output format                                          |
| A rule that must hold on every event, whether or not Claude remembers it         | Hook                                        | Which events, prompt or command, what blocks vs warns                                            |
| An external service or API                                                       | MCP server                                  | Server type, authentication, which tools                                                         |
| User or project configuration                                                    | Environment variable, never a settings file | Variable names, required vs optional, defaults                                                   |

New slash commands are skills (`skills/<name>/SKILL.md`), never the legacy `commands/` layout.
Answer the "settle" column from the request and the code. Ask the user only for what neither
settles.

## 2. Write the component

Editing an existing skill instead? Check `docs/CROSS_REFERENCES.md` first (step 4).

Creating any component, including one migrated from agent-skills, starts by loading its
authoring skill. Where that skill's advice conflicts with this repo, this skill wins — see
[the override table](#when-plugin-dev-or-skill-creator-skills-are-also-loaded).

| Creating   | First                                                                                                                                                                                                         |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Skill      | Invoke the Skill tool with skill="skill-creator:skill-creator". Never `plugin-dev:skill-development`. Skip its eval loop (test runs, benchmark, viewer, description optimization) unless the user asks for it |
| Agent      | Invoke the Skill tool with skill="plugin-dev:agent-development"                                                                                                                                               |
| Hook       | Invoke the Skill tool with skill="plugin-dev:hook-development"                                                                                                                                                |
| MCP server | Invoke the Skill tool with skill="plugin-dev:mcp-integration"                                                                                                                                                 |

**Skill** — copy `${CLAUDE_SKILL_DIR}/assets/SKILL.template.md` to
`plugins/ceh-<plugin>/skills/<name>/SKILL.md`, `name` matching the directory. Fill every
placeholder, then delete the `TEMPLATE-GUIDANCE` comment. Content stays inline. `references/` is
for two cases only: a schema or template shared by several skills, or a standard too large to
inline.

**Agent** — copy `${CLAUDE_SKILL_DIR}/assets/agent.template.md` to
`plugins/ceh-<plugin>/agents/<name>.md`, `name` matching the file name. Auto-delegation is driven
entirely by `description` (include "use proactively" to encourage it).

**Migrating from agent-skills** — still start from the template: move the old frontmatter and
sections into the template's order and headings rather than copying the old file whole. Old files
mix heading case and section names, and the templates exist to end that.

**Hook or script** — hook wiring goes in `plugins/ceh-<plugin>/hooks/hooks.json`, scripts in
`plugins/ceh-<plugin>/scripts/`, referenced as `${CLAUDE_PLUGIN_ROOT}/scripts/<file>`. Keep
`*.sh` LF-only: a CRLF checkout breaks bash with `$'\r'`.

**MCP server** — config goes in `plugins/ceh-<plugin>/.mcp.json` with `${CLAUDE_PLUGIN_ROOT}`
paths.

**Configuration** — environment variables only, never a `.claude/*.local.md` settings file or
other config file. Hooks, MCP servers, and scripts use HTTPS and never hardcode a credential: read
it from an environment variable and document every variable in the plugin README.

**`description` is always a folded block scalar (`>-`)** — never quoted, never plain. `validate.py`
rejects anything else.

```yaml
description: >-
  Load this skill when doing X: the colon is literal here, as are "quotes" and 'apostrophes'.
  Wrap at ~98 chars with a uniform 2-space indent and no blank lines.
```

It is the only style with no escaping burden. A plain scalar cannot contain `: `, single-quoted
needs `''` doubling, double-quoted needs `\` and `"` escaping — all three have silently produced
invalid YAML in this repo. Keep the indent uniform (a more-indented line becomes a literal newline
instead of folding) and avoid blank lines. Any _other_ key containing `: ` gets single quotes.
Put the key use case first: Claude Code truncates long descriptions in the skill listing.

Claude Code silently ignores a frontmatter field it does not recognize, so a typo reads as
working config. Use only fields from the official
[skills](https://code.claude.com/docs/en/skills#frontmatter-reference) and
[subagents](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields) references.
`validate.py` rejects any other key. Frontmatter worth reaching for before writing prose that does
the same job:

| Field                      | Use it for                                                                                   | Watch out                                                                                                                                                            |
| -------------------------- | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `paths`                    | Skills whose trigger really is a file type                                                   | **Narrows** auto-loading. A skill with real non-file triggers ("a `uv` command is run") loses them                                                                   |
| `effort`                   | Reasoning-heavy skills                                                                       | Default inherits the session level. Set it only when the skill needs a different one                                                                                 |
| `disable-model-invocation` | Workflows with side effects the user should trigger by hand                                  | The skill can then never be preloaded into an agent or called with `Invoke the Skill tool`                                                                           |
| `disallowed-tools`         | Skills that must not write                                                                   | Check the body first; most "review" skills here do apply fixes                                                                                                       |
| `context: fork`            | Heavy, self-contained task skills                                                            | The subagent does **not** see the conversation and runs in the background with the reduced tool set below. Set `background: false` if a step needs a tool outside it |
| `argument-hint`            | Skills the user invokes as `/name <arg>`                                                     | Cosmetic but free                                                                                                                                                    |
| `${CLAUDE_SKILL_DIR}`      | Referencing a file bundled with the skill                                                    | Substituted in the body _and_ in `allowed-tools` Bash rules                                                                                                          |
| `${CLAUDE_PLUGIN_ROOT}`    | Referencing a plugin-level script shared by several skills                                   | Substituted in plugin skill bodies and `allowed-tools`, not in project skills                                                                                        |
| `memory`                   | Agents that should learn across sessions                                                     | Auto-enables Read/Write/Edit on that agent                                                                                                                           |
| `compatibility`            | Skills that need software the machine may lack (`git`, `gh`, `uv`, `bun`, a server, network) | `>-` scalar, max 500 chars. Name runtime + minimum version and what fails without it. Omit for read-files-emit-Markdown skills                                       |

**Cross-plugin calls** — when a skill must call a skill in another plugin on _every_ run, add the
target plugin to `dependencies` in `plugin.json` (never in `marketplace.json`; bare strings, no
ranges) and call it explicitly: `Invoke the Skill tool with skill="ceh-<plugin>:<skill>"`.
Conditional handoffs and negative routing ("Not for X, use ...") stay prose with no dependency. A
cross-cutting plugin may depend only on other cross-cutting plugins. `validate.py` rejects a call
whose target does not resolve, is not a declared dependency, or sets
`disable-model-invocation: true`.

**Plugin-agent gotchas** — Claude Code ignores `permissionMode`, `hooks`, `mcpServers`, and
`initialPrompt` on plugin agents (security restriction). Do not add them; they read as working
config and are not. Grant edit permissions via session `permissions.allow` in `settings.json`
instead. Subagents run in the **background by default**, and background subagents keep only a
reduced built-in tool set — if an agent needs a tool outside `Read/Grep/Glob/LSP/Bash/PowerShell/
Edit/Write/NotebookEdit/WebFetch/WebSearch/TodoWrite/Skill/ToolSearch/EnterWorktree/ExitWorktree/
Monitor/TaskStop/SendMessage/Artifact`, it will be stripped silently. `AskUserQuestion` is stripped
from _every_ subagent, foreground or background — an agent can never stop to ask.

`skills:` entries must be fully qualified as `plugin:skill`; an entry that does not resolve is
skipped with only a debug-log warning. The preload is also the only route a hook-loaded standard
has into an agent: `SessionStart` hooks never fire for subagents.

**`isolation: worktree` is deliberately unused in this repo.** Subagent worktrees branch from the
repository's **default branch**, not the parent session's `HEAD`, unless `worktree.baseRef: "head"`
is set in `settings.json` — and their changes stay in the worktree rather than landing in your
checkout. Under this repo's feature-branch rule that hands an agent a copy of `main` without your
work, so no agent sets it.

## 3. Update both README tables

- Root `README.md` — add a row under the correct plugin group in **Skills** or **Agents**. If the
  plugin has no group there yet, add a `### <Plugin> (\`ceh-<plugin>\`)` subsection.
- `plugins/ceh-<plugin>/README.md` — add a row to that plugin's own table. The plugin README also
  carries anything a user must do before the component works: prerequisites, when a hook fires,
  and every environment variable the plugin reads, with its default and whether it is required.

## 4. Register any duplication

Before editing an existing skill, check `docs/CROSS_REFERENCES.md`. If the section appears there,
propagate the edit to **every** listed file in the same session — canonical file first, then the
copies. If you introduce new duplication, add an entry naming the canonical source, every copy,
what is shared, and what deliberately diverges.

## 5. Bump the version in both manifests

Same commit, both files, or CI fails:

- `plugins/ceh-<plugin>/.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`

**PATCH** for content/description updates, **MINOR** for a new skill or agent or for adding or
removing a `dependencies` entry, **MAJOR** for renaming or removing the plugin. Bump at commit
time, not during iterative edits. The repo git tag and its `CHANGELOG.md` entry are a separate,
independent layer — cut them after the plugin bumps land.

## 6. Validate

```bash
python tools/validate-plugins/validate.py
```

Same gate CI runs via `.github/workflows/validate.yml`. It checks:

- manifests: `plugin.json` ↔ `marketplace.json` sync, semver, `name` matching the directory
- frontmatter: `name` format and match, `description` present, `>-`, ≤ 1024 chars;
  `compatibility` ≤ 500 chars; only documented keys; no plugin-agent keys Claude Code ignores
- no `TEMPLATE-GUIDANCE` comment left from a template
- `references/...`, `${CLAUDE_PLUGIN_ROOT}/scripts/...`, and `${CLAUDE_SKILL_DIR}/...` mentions
  resolve to real files, and `ceh-<plugin>:<component>` mentions resolve
- `dependencies` resolve, the graph is acyclic, scenario bundles hold only a manifest and README
- every `Invoke the Skill tool with skill="..."` call is resolvable, declared, and invocable
- bundled `*.sh` / `*.py` scripts parse

`validate.py` does not parse YAML strictly. For a YAML syntax check, also run
`claude plugin validate plugins/ceh-<plugin>`.

A green validator proves the files are well-formed, not that the component works. Load the plugin
in a fresh session with `claude --plugin-dir plugins/ceh-<plugin>` and check what you added:

- Skill: a prompt using a description trigger phrase loads it; `/ceh-<plugin>:<skill>` runs it
- Agent: a prompt matching its description delegates to it
- Hook: `claude --debug` shows it firing on its event
- MCP server: `/mcp` lists the server and its tools

Report any check you did not run as not run. Do not imply it passed.

## New plugin

Only when step 1 finds no plugin that owns the use case. The layout is fixed by this section and
the Structure section of `CLAUDE.md`, so do not load `plugin-dev:plugin-structure`. Decide the
tier (scenario bundle, cross-cutting, use-case workflow, stack/build — see `CLAUDE.md`) and plan
every component with the step 1 table before creating anything, then:

1. `plugins/ceh-<name>/.claude-plugin/plugin.json`, flat under `plugins/` with no tier folder:

   ```json
   {
     "name": "ceh-<name>",
     "version": "1.0.0",
     "description": "CEH <name>: <one sentence on the use case>.",
     "author": { "name": "cheneeheng", "email": "eeheng.chen@gmail.com" },
     "repository": "https://github.com/cheneeheng/ceh-claude-code-library",
     "license": "Apache-2.0",
     "keywords": ["agent", "<keyword>"]
   }
   ```

   Add `"dependencies": ["ceh-<other>"]` only per the cross-plugin rule in step 2.

2. `plugins/ceh-<name>/README.md` with the plugin's own skill/agent table.
3. `.claude-plugin/marketplace.json` — a new entry whose `source` (`./plugins/ceh-<name>`),
   `version`, and `description` mirror `plugin.json`. `validate.py` fails on a plugin missing from
   the marketplace or a version mismatch.
4. Root `README.md` — a row in the **Plugins** table, the plugin in the **Categorization** tier
   table, its Skills/Agents rows, and a line in both install lists (`/plugin install` and the
   manual `path` list).
5. `CLAUDE.md` — a row in the **Plugins** table and the plugin in the tier table.
6. A `ceh-scenario-*` bundle, only if the plugin belongs in that situation's install set. A bundle
   holds `plugin.json` (with `dependencies`) and `README.md` and nothing else — `validate.py`
   enforces it. Record any new edge in `docs/PLUGIN_DEPENDENCIES.md`.

The repo tag bumps MINOR and `CHANGELOG.md` lists the plugin at `1.0.0` under `### Added`.

## When plugin-dev or skill-creator skills are also loaded

Step 2 loads `skill-creator` and the plugin-dev authoring skills on purpose, and
`plugin-dev:create-plugin` triggers on the same phrases as this skill. They give generic advice.
Where it conflicts with this repo, this skill wins:

| They say                                                                                     | This repo does                                                                          |
| -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `plugin-dev:skill-development` for skills                                                    | `skill-creator:skill-creator`                                                           |
| Run test prompts, benchmark, open the viewer, optimize the description                       | Only when the user asks. Otherwise stop after the draft                                 |
| `plugin-dev:plugin-structure` for layout                                                     | The layout in [New plugin](#new-plugin) and `CLAUDE.md`                                 |
| `plugin-dev:plugin-settings`, `.claude/<plugin>.local.md` settings files                     | Environment variables, documented in the plugin README                                  |
| Lean SKILL.md, detail in `references/` and `examples/`                                       | Content inline. `references/` only for shared schemas or oversized standards            |
| "This skill should be used when…" descriptions, any scalar style                             | `>-` folded scalar, "Load this skill when…" (agents: "Use this agent to…")              |
| Write the file from scratch, or generate an agent with the `agent-creator` agent             | Start from the template in `${CLAUDE_SKILL_DIR}/assets/`                                |
| Skills in the legacy `commands/` layout                                                      | `skills/<name>/SKILL.md` only                                                           |
| Hook scripts in `examples/`                                                                  | `scripts/`, referenced as `${CLAUDE_PLUGIN_ROOT}/scripts/...`                           |
| New plugin at `0.1.0`, marketplace entry optional                                            | `1.0.0`, marketplace entry in the same commit                                           |
| `plugin-validator` / `skill-reviewer` agents, `validate-agent.sh`, `validate-hook-schema.sh` | `python tools/validate-plugins/validate.py` is the gate, then the live checks in step 6 |
| Agent `<example>` blocks and `color`                                                         | Prose `description`, no `<example>` blocks; `color` optional                            |
| Eval workspace next to the skill directory                                                   | `.agents_workspace/skill-evals/<skill>/`, git-ignored, never inside `plugins/`          |
| Wait for user confirmation at each phase, ask where to create, `git init`                    | Autonomous mode, flat `plugins/`, existing repo                                         |

Everything else in those skills applies — hook event payloads, prompt-based hooks, MCP server
types, agent system-prompt design, skill-creator's drafting guidance.
