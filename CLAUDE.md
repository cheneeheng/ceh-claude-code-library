# CEH Claude Code Library

Plugin repo for the `ceh-*` Claude Code plugins — guidance for autonomous agents, delivered as
skills, subagents, and hooks. Each plugin is a standalone, self-contained **use case**. The plugins
were migrated from [agent-skills](https://github.com/cheneeheng/agent-skills). One left there
arrives the same way, through `add-plugin-component`, only if it passes the scope test in the
vision.

`docs/VISION.md` says why the repo works the way this file describes: agents first and humans
second, the product-lifecycle scope, and the principles that settle a decision. Every change must
hold up against it, per `.claude/rules/decision-vision-governs.md`.

The project's decisions live in `.claude/rules/decision-<topic>.md`, one file each, and this file
describes the repo and its procedures. A new decision gets its own file, through
`ceh-every-session:record-project-decisions`, never a paragraph here.

## Organizing Principle

Plugins split on one axis: **use case**. How they split, and what each tier admits, is in
`decision-plugin-boundaries.md`, `decision-no-bundles.md`, `decision-every-session-admission.md`,
and `decision-shared-standards-duplication.md`. `docs/GETTING_STARTED.md` is the install entry
point.

Plugins fall into three tiers:

| Tier                  | Loaded           | Plugins                                                                                                                                                                                                                                                                                                                                                                                                         |
| --------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Cross-cutting**     | most sessions    | `ceh-every-session`, `ceh-coding-conduct`, `ceh-git-workflow`, `ceh-testing`                                                                                                                                                                                                                                                                                                                                    |
| **Use-case workflow** | per activity     | `ceh-seo`, `ceh-blog`, `ceh-build-planning`, `ceh-build-from-plan`, `ceh-check-build-against-plan`, `ceh-documentation`, `ceh-usability-audit`, `ceh-business-plan`, `ceh-git-datastore`, `ceh-workflow-builder`, `ceh-workflow-runner`, `ceh-session-to-skill`, `ceh-session-diagnosis`, `ceh-security-audit`, `ceh-competitor-analysis`, `ceh-ui-design`, `ceh-codebase-explanation`, `ceh-orchestration-lab` |
| **Stack / build**     | per project type | `ceh-python-service`, `ceh-python-library`, `ceh-web-frontend`, `ceh-ag-ui`                                                                                                                                                                                                                                                                                                                                     |

## Structure

```
.agents_workspace/            # Session artifacts, git-ignored in full: DECISION_LOG.md, skill-evals/
.claude/rules/                # Project decisions, one decision-<topic>.md each
.claude/skills/               # Repo-local skills — add-plugin-component and its templates (assets/), model-audit (scripts/, references/, assets/), evaluate-plugin (scripts/)
.claude-plugin/               # Marketplace manifest (marketplace.json)
archive/                      # Retired plugins or plugin contents — unpublished, not validated
audits/<date>/                # Model-audit reports, one <plugin>.md each plus SUMMARY.md — written by the model-audit skill
.github/workflows/            # validate.yml — runs validate.py on push and PR; model-audit.yml — weekly audit draft PR
docs/                         # GETTING_STARTED.md (user-facing install guide), CATALOG.md (every skill and agent), and maintainer docs — VISION.md, STRATEGY.md, CROSS_REFERENCES.md, PLUGIN_DEPENDENCIES.md, ENVIRONMENT_VARIABLES.md, TESTING_WORKFLOW.md, RETRO_WORKFLOW.md, PLUGIN_VERSIONS.md, IDEAS.md
examples/                     # Worked usage examples, a ceh-<plugin>/README.md where one exists (only ceh-ag-ui today) — not validated
plugins/                      # All plugins — one directory per plugin, no tier subfolders
└── standalone/
    └── ceh-<plugin-name>/
        ├── .claude-plugin/           # plugin.json — version and dependencies live here; tuning.json — model-audit state
        ├── agents/                   # Optional — subagents, one <name>.md each
        ├── docs/                     # Optional — maintainer docs for this plugin (architecture, test records), not loaded by any skill
        ├── hooks/                    # Optional — hooks.json wiring scripts via ${CLAUDE_PLUGIN_ROOT}, and a mod's hooks module under `modules`
        ├── tests/                    # Optional — a mod's *.test.tsx, run by `claude plugin test`, not by validate.py
        ├── types/                    # Optional — a mod's state contract, named by plugin.json `types`
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

## Skills and Frontmatter

Skill and agent authoring rules (templates, `references/` policy, naming, frontmatter conventions)
live in `plugins/CLAUDE.md`, which loads when working under `plugins/`.

## Plugin Dependencies

When a reference earns a dependency, and where it is declared, is in
`.claude/rules/decision-plugin-dependencies.md`. `validate.py` rejects an
`Invoke the Skill tool with skill="..."` call whose target does not resolve, is not a declared
dependency, or sets `disable-model-invocation: true`. The current graph and the evidence for each
edge live in `docs/PLUGIN_DEPENDENCIES.md`.

## Adding a Component

The repo-local skill `.claude/skills/add-plugin-component/` is the single checklist for adding or
changing a skill, agent, hook, script, or a whole new plugin. It auto-loads when a `SKILL.md` or
`agents/*.md` is created; load it explicitly if it has not.

Whatever else gets skipped, these four land in the **same commit**. CI fails when item 2, 3, or 4
is missing. Item 1 is a review rule:

1. A row in `docs/CATALOG.md` (Skills or Agents).
2. A row in `plugins/standalone/ceh-<plugin>/README.md`.
3. A version bump in **both** `plugins/standalone/ceh-<plugin>/.claude-plugin/plugin.json` and
   `.claude-plugin/marketplace.json` — level per `decision-version-levels.md`. CI checks only that
   the two match.
4. `python tools/validate-plugins/validate.py` green.

The PR also carries its `CHANGELOG.md` entry and `docs/PLUGIN_VERSIONS.md` rows, per
`decision-changelog-sections.md`.

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

Which tools, and when to run them, is in `.claude/rules/decision-evaluation.md`. Two options, by
scope:

- **One skill:** the `skill-creator:skill-creator` plugin, which runs a with/without comparison
  inside a session from a skill's own `evals/evals.json`.
- **A whole plugin:** `claude plugin eval` run from the plugin root, per
  [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals). `claude plugin eval init`
  writes the cases to `evals/` (one directory per case: `prompt.md` plus `graders/`), and
  `claude plugin eval .` runs each case three times with and without the plugin and reports the
  difference. It needs Claude Code v2.1.269+ and git 2.31+, and every run and judge grader is a
  real model call on your account. Pass `--no-publish` to keep the report local. In CI, add
  `--threshold`, `--json` and `--trust-plugin`.

The two tools do not read each other's case files. The repo-local skill
`.claude/skills/evaluate-plugin/` is the procedure: it writes plugin-eval cases for skills, hooks,
agents, and MCP servers, fixes one gap per round, and hands description fixes to skill-creator and
long tuning runs to `/claude-api hillclimb` through its converter script.

## Versioning

Version levels, the no-releases rule, and the changelog shape are in
`.claude/rules/decision-version-levels.md`, `decision-no-releases.md`, and
`decision-changelog-sections.md`.

### Landing a branch

Follow `ceh-git-workflow:pull-request` (open, merge, land), with these differences for this repo.
Where they conflict, this section wins:

- **Changelog step:** start `ceh-git-workflow:update-changelog` as the step says, but write the
  entry under today's `## YYYY-MM-DD` section, per `decision-changelog-sections.md`, never under
  `## [Unreleased]`.
- **Version bumps ride in the PR.** The skill's "needs a version bump or tag → switch to
  `ceh-git-workflow:release`" does not apply: bump `plugin.json`, `marketplace.json`, and
  `docs/PLUGIN_VERSIONS.md` in the PR's commit, and never tag or release.
- **Commit step:** expect the pre-commit hook to abort on reformatted Markdown, see Commands.

## Key Files

| File                                                         | Purpose                                                                        |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| `plugins/standalone/ceh-<plugin>/.claude-plugin/plugin.json` | Plugin version, metadata, dependencies                                         |
| `.claude-plugin/marketplace.json`                            | Marketplace listing (all plugins)                                              |
| `README.md`                                                  | User-facing overview — Plugins and lifecycle-stage tables, install steps       |
| `docs/CATALOG.md`                                            | Every skill and agent, grouped by plugin, with its Invoke cell                 |
| `CONTRIBUTING.md`                                            | Repo tools, the local CI gate, and pre-commit formatting                       |
| `docs/GETTING_STARTED.md`                                    | First-time install route: the core, then one plugin per stage reached          |
| `docs/VISION.md`                                             | Identity, scope, goals, and principles: why the rules here are what they are   |
| `docs/STRATEGY.md`                                           | How the plugins form one system: stages, handoff files, how work is chosen     |
| `docs/CROSS_REFERENCES.md`                                   | Content duplicated across skills: canonical source and every copy              |
| `docs/PLUGIN_DEPENDENCIES.md`                                | Current dependency graph: every edge with its evidence                         |
| `docs/ENVIRONMENT_VARIABLES.md`                              | Every environment variable any plugin reads: plugin, reader, default, effect   |
| `docs/TESTING_WORKFLOW.md`                                   | How `ceh-testing`, the stack testing skills, and the tester agents route       |
| `docs/RETRO_WORKFLOW.md`                                     | How the three retro skills route issues and where their reports are saved      |
| `docs/PLUGIN_VERSIONS.md`                                    | Every plugin's current version, and the changelog date that set it             |
| `CHANGELOG.md`                                               | One section per PR-open date, each with a `### Plugin versions` table          |
| `.claude/skills/add-plugin-component/assets/`                | `SKILL.template.md` and `agent.template.md` — the base for every new component |
| `.claude/rules/decision-*.md`                                | One file per project decision, loaded in every session unless it sets `paths`  |
| `.agents_workspace/DECISION_LOG.md`                          | Agent decision log — **git-ignored, local only**, append-only                  |
