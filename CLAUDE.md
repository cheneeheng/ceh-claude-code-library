# CEH Claude Code Library

Plugin repo for the `ceh-*` Claude Code plugins — guidance for autonomous agents, delivered as
skills, subagents, and hooks. Each plugin is a standalone, self-contained **use case**. Migration
from [agent-skills](https://github.com/cheneeheng/agent-skills) is in progress: plugins land here
one at a time, and the tables below grow as they do.

**Read `docs/VISION.md` before adding a plugin, accepting an idea, or changing a rule here.** It
says why the repo works the way this file describes: agents first and humans second, the
product-lifecycle scope, and the principles that settle a decision. If this file and the vision
disagree, fix one of them in the same PR.

## Organizing Principle

Plugins split on one axis: **use case**. Two consequences drive how skills are written and where
they live:

- **Skills trigger on moments, not topics.** A skill fires on a verb ("I'm opening a PR"), not a
  noun ("PostgreSQL"). Topic-named skills either never auto-trigger or restate what the model
  already knows, so each skill is cut to the repo-opinionated delta.
- **Plugin names declare their scope.** `ceh-python-service` vs `ceh-python-library` — the name
  states the use case and makes gaps obvious.

Plugins fall into four tiers:

| Tier                  | Loaded            | Plugins                                                                                                                                                                                                                                                     |
| --------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Scenario bundle**   | one per situation | `ceh-scenario-service`, `ceh-scenario-library`, `ceh-scenario-webapp`, `ceh-scenario-ideation`, `ceh-scenario-editorial`                                                                                                                                    |
| **Cross-cutting**     | most sessions     | `ceh-every-session`, `ceh-coding-conduct`, `ceh-git-workflow`, `ceh-testing`                                                                                                                                                                                |
| **Use-case workflow** | per activity      | `ceh-seo`, `ceh-blog`, `ceh-plan-build-review`, `ceh-documentation`, `ceh-usability-audit`, `ceh-business-plan`, `ceh-git-datastore`, `ceh-workflow-builder`, `ceh-workflow-runner`, `ceh-competitor-analysis`, `ceh-ui-design`, `ceh-codebase-explanation` |
| **Stack / build**     | per project type  | `ceh-python-service`, `ceh-python-library`, `ceh-web-frontend`, `ceh-ag-ui`                                                                                                                                                                                 |

The scenario tier is the install entry point, not a fourth axis: a bundle is a manifest with
`dependencies` and nothing else — no skills, agents, or hooks. Experimental plugins never enter a
bundle.

Categorization rules of thumb:

- **Framework variants do not split into separate plugins** when their skills trigger on disjoint
  file types. Splitting duplicates the shared standards and reintroduces drift.
- **A foundational standard needed by more than one use-case plugin is duplicated into each**, not
  extracted into a shared base plugin — see the Shared-Standards Duplication Policy below.
- **Scenario bundles live in `plugins/scenarios/`**, every other plugin in `plugins/standalone/`.
  The `ceh-scenario-` prefix carries the distinction and `validate.py` enforces the structural
  invariant (manifest + README only).
- **App-specific patterns are not standards.** Anything bound to one application's schema or design
  is removed rather than kept as a niche plugin.
- **`ceh-every-session` admits only what holds however Claude Code is used** — coding, writing, research,
  or ops. If a component assumes a repository, code, or a specific activity, it belongs elsewhere.
  "Useful almost everywhere" is not the test; that is how an every-session plugin becomes a dumping ground.
- **The cross-cutting tier is orthogonal by construction.** It holds a discipline that applies
  whatever you are building, so it loads _alongside_ a use-case plugin, never instead of one.
- **Technique splits from tooling when the technique is genuinely stack-agnostic.** The test:
  would the content be byte-identical across stacks? If a technique skill grows stack-specific
  branches, it was tooling all along.

## Structure

```
.agents_workspace/            # Session artifacts, git-ignored in full: DECISION_LOG.md, skill-evals/
.claude/skills/               # Repo-local skills — add-plugin-component and its templates (assets/), model-audit (scripts/, references/, assets/)
.claude-plugin/               # Marketplace manifest (marketplace.json)
archive/                      # Retired plugins or plugin contents — unpublished, not validated
audits/<date>/                # Model-audit reports, one <plugin>.md each plus SUMMARY.md — written by the model-audit skill
.github/workflows/            # validate.yml — runs validate.py on push and PR; model-audit.yml — weekly audit draft PR
docs/                         # Maintainer docs — VISION.md, CROSS_REFERENCES.md, PLUGIN_DEPENDENCIES.md, ENVIRONMENT_VARIABLES.md, TESTING_WORKFLOW.md, PLUGIN_VERSIONS.md, IDEAS.md
examples/                     # Worked usage examples, one ceh-<plugin>/README.md each — not validated
plugins/                      # All plugins — two folders, one directory per plugin, no tier subfolders
├── scenarios/
│   └── ceh-scenario-<name>/  # Scenario bundle — .claude-plugin/plugin.json + README.md ONLY
└── standalone/
    └── ceh-<plugin-name>/
        ├── .claude-plugin/           # plugin.json — version and dependencies live here; tuning.json — model-audit state
        ├── agents/                   # Optional — subagents, one <name>.md each
        ├── docs/                     # Optional — maintainer docs for this plugin (architecture, test records), not loaded by any skill
        ├── hooks/                    # Optional — hooks.json wiring scripts via ${CLAUDE_PLUGIN_ROOT}
        ├── output-styles/            # Optional — output style .md files
        ├── references/               # Optional — files shared by several skills of this plugin, read via ${CLAUDE_PLUGIN_ROOT}
        ├── scripts/                  # Optional — hook scripts and shell helpers
        └── skills/
            └── <skill-name>/
                ├── SKILL.md               # Required — frontmatter + full body, all content inline
                └── references/            # Sparingly — see Skills below (same for assets/, scripts/)
tools/
├── model-audit/               # README.md pointer only — the tools live in .claude/skills/model-audit/
├── skills-sync/               # Copies skills into a project's .claude/skills/ — py/sh/ps1/html, own README.md
└── validate-plugins/          # The CI gate — stdlib-only Python, own README.md
```

## Plugins

Each plugin's domain is in the root `README.md` Plugins table and its own `plugin.json`
`description`.

A concept-map skill for markdown-only knowledge bases would be a separate sibling of
`document-architecture`, not part of it.

## Skills and Frontmatter

Skill and agent authoring rules (templates, `references/` policy, naming, frontmatter conventions)
live in `plugins/CLAUDE.md`, which loads when working under `plugins/`.

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
2. A row in `plugins/standalone/ceh-<plugin>/README.md`.
3. A version bump in **both** `plugins/standalone/ceh-<plugin>/.claude-plugin/plugin.json` and
   `.claude-plugin/marketplace.json` — level per the Versioning section below. CI checks only that
   the two match.
4. `python tools/validate-plugins/validate.py` green.

The PR also carries its `CHANGELOG.md` entry and `docs/PLUGIN_VERSIONS.md` rows, per Versioning.

## Commands

```bash
# Validate the whole repo — CI runs this too
# (no arguments, whole repo only; CI uses Python 3.13; the repo has no test suite, this is the gate)
python tools/validate-plugins/validate.py

# Strict YAML parse check of one plugin's skills and agents
claude plugin validate plugins/standalone/ceh-<plugin>
```

`validate.py` fails on any `ceh-<plugin>:<name>` mention, prose included, that no longer resolves,
so renaming a skill means grepping for its old name. It shellchecks `scripts/*.sh` only when
`shellcheck` is installed. CI has it, so a local green run on Windows can still fail CI.

The pre-commit hook (`pre-commit install` once per clone) runs ruff-format, prettier, and shfmt and
**aborts the commit when it reformats a file**, which any Markdown table edit can trigger. Re-stage
and commit again, and chain the push with `&&`, never `;`, so a failed commit does not push.

## Evaluation

Evals use Anthropic's own tools, nothing bespoke. Two options, by scope:

- **One skill:** the `skill-creator:skill-creator` plugin, which runs a with/without comparison
  inside a session from a skill's own `evals/evals.json`. Keep its workspace in
  `.agents_workspace/skill-evals/<skill>/`, never under `plugins/`.
- **A whole plugin:** `claude plugin eval` run from the plugin root, per
  [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals). `claude plugin eval init`
  writes the cases to `evals/` (one directory per case: `prompt.md` plus `graders/`), and
  `claude plugin eval .` runs each case three times with and without the plugin and reports the
  difference. It needs Claude Code v2.1.269+ and git 2.31+, and every run and judge grader is a
  real model call on your account. Pass `--no-publish` to keep the report local. In CI, add
  `--threshold`, `--json` and `--trust-plugin`.

The two tools do not read each other's case files. Eval only when asked, because the cost is real.
Do not run the archived `ceh-evaluation` plugin (`archive/ceh-evaluation/`): these two replace it.

## Versioning

**Per-plugin versions** (load-bearing for auto-update) live in `plugin.json`, mirrored in
`marketplace.json`, and both must be bumped in the same commit. Bump at commit time, not during
iterative edits.

- **PATCH** — content or description updates.
- **MINOR** — a new skill or agent, or adding/removing a `dependencies` entry.
- **MAJOR** — the plugin is renamed or removed.

**This repo has no releases**: no version tags, no GitHub releases, no release commits. Changes
reach users through per-plugin version bumps and the dated `CHANGELOG.md` sections each PR adds. If
the user asks for a release in any form ("cut a release", "ship it", "tag a release", the full ship
sequence, or `ceh-git-workflow:release`), do not start it. Reply with a warning that releases are
not intended or used in this repository, and stop.

**Every PR adds its own `CHANGELOG.md` entry**, in the PR's own commit, under a section headed by
the date the PR is opened, `## YYYY-MM-DD`. PRs opened on the same day share that day's section:
add to it if it exists, otherwise create it at the top, below the intro. Order is by date opened,
not merged. A section holds prose on what changed and why, a `### Plugin versions` table listing
every plugin the PR bumped (merged with any table already in that day's section), then
`### Added` / `### Changed` / `### Fixed`. In the same commit, update `docs/PLUGIN_VERSIONS.md`: the
new version and the section date on every bumped plugin's row.

### Landing a branch

Follow `ceh-git-workflow:pull-request` (open, merge, land), with these differences for this repo.
Where they conflict, this section wins:

- **Changelog step:** do not log under `## [Unreleased]` or run `ceh-git-workflow:update-changelog`
  in Unreleased mode. Write the entry under today's `## YYYY-MM-DD` section, per the rule above.
- **Version bumps ride in the PR.** The skill's "needs a version bump or tag → switch to
  `ceh-git-workflow:release`" does not apply: bump `plugin.json`, `marketplace.json`, and
  `docs/PLUGIN_VERSIONS.md` in the PR's commit, and never tag or release.
- **Commit step:** expect the pre-commit hook to abort on reformatted Markdown, see Commands.

## Key Files

| File                                                         | Purpose                                                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| `plugins/standalone/ceh-<plugin>/.claude-plugin/plugin.json` | Plugin version, metadata, dependencies                                         |
| `.claude-plugin/marketplace.json`                            | Marketplace listing (all plugins)                                              |
| `README.md`                                                  | User-facing docs — plugin, skill, and agent tables live here                   |
| `docs/VISION.md`                                             | Identity, scope, goals, and principles: why the rules here are what they are   |
| `docs/CROSS_REFERENCES.md`                                   | Content duplicated across skills: canonical source and every copy              |
| `docs/PLUGIN_DEPENDENCIES.md`                                | Current dependency graph: every edge with its evidence                         |
| `docs/ENVIRONMENT_VARIABLES.md`                              | Every environment variable any plugin reads: plugin, reader, default, effect   |
| `docs/TESTING_WORKFLOW.md`                                   | How `ceh-testing`, the stack testing skills, and the tester agents route       |
| `docs/PLUGIN_VERSIONS.md`                                    | Every plugin's current version, and the changelog date that set it             |
| `CHANGELOG.md`                                               | One section per PR-open date, each with a `### Plugin versions` table          |
| `.claude/skills/add-plugin-component/assets/`                | `SKILL.template.md` and `agent.template.md` — the base for every new component |
| `.agents_workspace/DECISION_LOG.md`                          | Agent decision log — **git-ignored, local only**, append-only                  |

## Cross-Reference Rule

Before editing any skill, check `docs/CROSS_REFERENCES.md`. If the section you are changing appears
there, edit the canonical file first, then mirror the change to every listed copy in the same
session. New duplication gets a new entry.

## Shared-Standards Duplication Policy

Each use-case plugin must be self-contained so a user loads exactly one plugin per use case. When a
foundational standard is needed by more than one, **duplicate the delta into each** rather than
extracting a shared base plugin. The cost is drift; the required mitigation is to register every
duplicated block in `docs/CROSS_REFERENCES.md` and propagate edits in the same session.
