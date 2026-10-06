# Changelog

This repo has no releases. Every pull request adds its entry under a section headed by the date the
PR was opened, `YYYY-MM-DD`, and PRs opened on the same day share one section. Each plugin keeps its
own [Semantic Versioning](https://semver.org/) version, listed per section under
`### Plugin versions` and tracked in [`docs/PLUGIN_VERSIONS.md`](docs/PLUGIN_VERSIONS.md). Notes
before this repo live in
[agent-skills](https://github.com/cheneeheng/agent-skills/blob/main/CHANGELOG.md).

---

## 2026-10-06

The root `CLAUDE.md` loads in every session, so it now carries only what a session cannot derive
and what applies repo-wide. Plugin-authoring rules load only when working under `plugins/`. No
plugin version changes.

A repo-local `model-audit` skill keeps the plugins aligned with Claude's per-model prompting guides.
It detects guides a plugin has not been checked against, runs headless `/doctor prompt-audit` and
pinned-agent tuning passes, and hands the reports over as a draft PR. It never merges or runs evals.
No plugin version changes.

The first model audit ran on `ceh-core` against the Fable 5.1, Opus 5.5 and Sonnet 5.5 guide
chains and kept no edits, so only its `tuning.json` state is new. The audit scripts now locate
plugins by path instead of assuming `plugins/standalone/`. No plugin version changes.

A second model audit ran on `ceh-coding-agent` and `ceh-git-workflow` against the same guide
chains, and every edit it proposed was kept. These edits remove stale wording and references to
things that do not exist, and make the base branch in `shrink-diff` explicit.

A third model audit ran on `ceh-blog` and `ceh-documentation` against the same guide chains, and
every edit it proposed was kept. It resolves two contradictions: the Launch template's product-line
hook against the no-pitch Opening rule, and runbook page numbers left with gaps under
`write-project-docs`. It also drops rules that other steps already cover. The removed "No fluff
drafts" rule left one point not covered anywhere else, so `draft-post`'s Length line now says
length follows the content, not the source material.

The `model-audit` workflow's weekly schedule is off for now, so it runs only on manual dispatch.
When it runs, it applies the proposed edits by default, since they land on the `audit/<date>`
branch behind a draft PR. Claude Code now comes from the native installer, because the npm package
is deprecated. No plugin version changes.

### Plugin versions

| Plugin              | Version |
| ------------------- | ------- |
| `ceh-blog`          | 1.0.1   |
| `ceh-coding-agent`  | 1.0.1   |
| `ceh-documentation` | 1.0.1   |
| `ceh-git-workflow`  | 1.0.1   |

### Added

- `audits/2026-10-06/`: the `ceh-core`, `ceh-coding-agent` and `ceh-git-workflow` audit reports
- `plugins/standalone/ceh-core/.claude-plugin/tuning.json`: model-audit state recording the guides `ceh-core` was checked against
- `tuning.json` model-audit state for `ceh-coding-agent` and `ceh-git-workflow`
- `audits/2026-10-06/`: the `ceh-blog` and `ceh-documentation` audit reports, with `SUMMARY.md` covering all five plugins audited that day
- `tuning.json` model-audit state for `ceh-blog` and `ceh-documentation`
- `.claude/skills/model-audit/`: the `/model-audit` skill, with the stdlib detector and parallel audit runner in `scripts/`, the filter and tuning prompts in `references/`, and the config and guide state in `assets/`
- `.github/workflows/model-audit.yml`: a weekly (Friday 06:00 UTC) or manual run that opens the audit draft PR
- `tools/model-audit/README.md`, a pointer to the skill folder

### Changed

- Move the Skills and Frontmatter Conventions sections from `CLAUDE.md` to a new `plugins/CLAUDE.md`, leaving a pointer
- Drop the plugin domain table from `CLAUDE.md`, which repeated the root `README.md` Plugins table, and the `find`/`grep` one-liners from Commands
- The `add-plugin-component` new-plugin checklist no longer asks for a `CLAUDE.md` Plugins table row
- `model-audit` `SKILL.md` gains a next-steps section for the reviewer (keep or drop edits, accept or reject pinned tuning, mirror shared content, bump, changelog, re-run failures, merge), and the skill's `README.md` an Arguments table saying what each argument does and its default
- `model-audit`: `--plugins` takes plugin paths from the repo root instead of bare names, and the stale scan finds every plugin under `plugins/` except scenario bundles instead of globbing `plugins/standalone/`
- `ceh-coding-agent:shrink-diff` diffs against the base-branch argument (default `main`) instead of a hard-coded `main`
- `ceh-coding-agent:explain-until-understood` points its honesty rules at the output style, not the contract, and `explain-codebase` drops a closing line about a mapper that does not exist
- `ceh-coding-agent` README: the `agent-coding-contract` row no longer claims a role section, and `explain-codebase` is listed as on demand, matching its model-invocable frontmatter
- `ceh-git-workflow:update-readme` folds the no-marketing rule into "Match existing voice" as plain, technical prose
- `ceh-blog:draft-post` and `edit-post`: the Project / Launch hook opens on the moment that led to building it, with what it does and who it's for inside the first paragraph, instead of a one-line product pitch
- `ceh-blog:draft-post` drops "No fluff drafts" and folds its source-length point into the Length line. `edit-post` drops "Diagnose before editing", "One question after" and "Draft is already good", which its Output, Step 4 and diagnosis sections already state
- `ceh-documentation:write-guides-and-runbooks`: under `write-project-docs`, the runbook renumbers its remaining pages from `OP-01` instead of leaving gaps
- `ceh-documentation:write-project-docs` says delegated skills read the shared `docs-standard.md` instead of shipping their own copy
- `.github/workflows/model-audit.yml`: the weekly schedule is commented out, `apply` defaults to true (scheduled runs always apply), Claude Code installs via `claude.ai/install.sh` instead of npm, `actions/checkout` is `@v6`, and a concurrency group stops runs overlapping

## 2026-10-05

Releases are retired. The changelog now grows one dated section per PR-open day, written in the
PR itself, instead of one section per tagged release.

The workflow runner splits out of `ceh-workflow-builder` into its own `ceh-workflow-runner` plugin.
Building a flow and running it are different moments, and a session that only runs a flow has no
use for the interview and builder skills.

### Plugin versions

| Plugin                 | Version |
| ---------------------- | ------- |
| `ceh-workflow-builder` | 1.3.0   |
| `ceh-workflow-runner`  | 1.0.0   |

### Added

- Add the `ceh-workflow-runner` plugin at 1.0.0, holding `run-agentic-workflow` and its own word-for-word copy of `flow-config-schema.md`, registered in `docs/CROSS_REFERENCES.md`

### Changed

- Move `run-agentic-workflow` from `ceh-workflow-builder` to `ceh-workflow-runner`. Generated `<name>-flow` skills now call `ceh-workflow-runner:run-agentic-workflow` and name that plugin in their `compatibility`. Flows emitted before this change still call `ceh-workflow-builder:run-agentic-workflow` and must have that line updated

- Replace the release process with per-PR changelog entries grouped by the date the PR is opened, in `CLAUDE.md`, the `add-plugin-component` checklist, `README.md`, and `docs/PLUGIN_VERSIONS.md`
- Rename the old release sections `v2026.10.02` and `v2026.10.03` to the date format, here and in `docs/PLUGIN_VERSIONS.md`
- Document in `CLAUDE.md` how landing a branch in this repo differs from `ceh-git-workflow:pull-request`
- `CLAUDE.md` now tells an agent to refuse any release request with a warning that releases are not used in this repo

## 2026-10-03

Built workflows become runnable without a human driving them. `ceh-workflow-builder` now emits a
`flow.yaml` config that a new generic runner executes, interactively or headless with `claude -p`,
with Claude Code dynamic workflows as an optional backend for big fan-out stages. The design rests
on empirical tests of how dynamic workflows behave headless, now recorded in the plugin's docs.

### Plugin versions

| Plugin                 | Version |
| ---------------------- | ------- |
| `ceh-workflow-builder` | 1.2.0   |

### Added

- Add the `ceh-workflow-builder:run-agentic-workflow` skill, a generic runner that executes a built workflow from its `flow.yaml`, interactively or headless (`claude -p`): stages, approvals between stages, gates, run state and resume, ending on a `FLOW STATUS:` line. Stages run as a skill, agent, script, inline instructions, or a saved Claude Code dynamic workflow, which is never assumed: a missing Workflow tool runs the declared fallback or fails, never imitates
- Add `ceh-workflow-builder/references/flow-config-schema.md`, the `flow.yaml` contract shared by the builder and the runner
- Add `ceh-workflow-builder/docs/ARCHITECTURE.md` and `docs/TEST_RESULTS.md`: how build and run fit together, and the empirical dynamic-workflow tests (F1-F14) the design rests on, with the full re-run procedure

### Changed

- `ceh-workflow-builder:build-agentic-workflow` emits a `flow.yaml` plus a thin trigger skill and an invocation guide instead of a pipeline-table flow skill, and its emitted `SKILL.md` templates move to the skill's `references/emitted-templates.md` to keep it under 500 lines
- Align the three `ceh-workflow-builder` skills with the component template: sentence-case titles, "Load this skill when" descriptions, and the runner's sections in template order

## 2026-10-02

First release of this repo. It completes the migration from agent-skills: 16 standalone plugins
restructured onto one `SKILL.md` and agent template, five scenario bundles as the install entry
point, the `validate.py` CI gate, and the maintainer docs. Plugins keep the version they migrated
at, so nothing is bumped. Releases are named by date from here on, and `docs/PLUGIN_VERSIONS.md`
maps each plugin version to the release that last changed it.

### Plugin versions

| Plugin                   | Version |
| ------------------------ | ------- |
| `ceh-ag-ui`              | 1.0.0   |
| `ceh-blog`               | 1.0.0   |
| `ceh-business-plan`      | 1.0.5   |
| `ceh-coding-agent`       | 1.0.0   |
| `ceh-core`               | 1.0.0   |
| `ceh-documentation`      | 1.0.0   |
| `ceh-git-datastore`      | 1.0.1   |
| `ceh-git-workflow`       | 1.0.0   |
| `ceh-plan-build-review`  | 1.0.0   |
| `ceh-python-library`     | 1.0.0   |
| `ceh-python-service`     | 1.0.0   |
| `ceh-seo`                | 1.0.0   |
| `ceh-testing`            | 1.0.0   |
| `ceh-usability-audit`    | 1.0.0   |
| `ceh-web-frontend`       | 1.0.0   |
| `ceh-workflow-builder`   | 1.1.2   |
| `ceh-scenario-editorial` | 1.0.0   |
| `ceh-scenario-ideation`  | 1.0.0   |
| `ceh-scenario-library`   | 1.0.0   |
| `ceh-scenario-service`   | 1.0.0   |
| `ceh-scenario-webapp`    | 1.0.0   |

### Added

- Add `docs/PLUGIN_VERSIONS.md`, the version of every plugin as of the latest release and the release that last changed it

- Add five scenario bundles as the install entry point, each a manifest and README with no skills, agents, or hooks: `ceh-scenario-service`, `ceh-scenario-library`, `ceh-scenario-webapp`, `ceh-scenario-ideation`, and `ceh-scenario-editorial`, all at `1.0.0`. They replace the agent-skills `-iterate` bundles under shorter names. `ceh-scenario-core`, the `-greenfield` bundles, and `ceh-scenario-agent-tooling` are not migrated: the stack bundles list the cross-cutting plugins directly, `ceh-scenario-ideation` covers the greenfield delta, and `ceh-evaluation` is archived
- Migrate `tools/skills-sync` from agent-skills unchanged apart from a stale decision-log pointer in its README: the py, sh, ps1 and html implementations that copy skills into a project's `.claude/skills/`. `tools/skill-evals` stays behind, since the Evaluation section of `CLAUDE.md` replaces it with Anthropic's own eval tools
- Add the `add-plugin-component` repo skill with `SKILL.md` and agent templates as the base for every new component
- Add `tools/validate-plugins/validate.py` and its CI workflow, ported from agent-skills, now also rejecting undocumented frontmatter keys, malformed names, and leftover template guidance
- Add the empty `ceh-claude-code-library` marketplace and skeleton `CLAUDE.md`, `docs/CROSS_REFERENCES.md`, and `docs/PLUGIN_DEPENDENCIES.md` for migrated plugins to land into
- Add a pre-commit config that formats Python with ruff, Markdown and JSON with the official npm prettier, and shell scripts with shfmt
- Migrate `ceh-git-workflow` from agent-skills at `1.0.0`: its 11 skills (branch, commit, open-pr, merge, hotfix, release, code-review, dependency-management, update-changelog, merge-flow, release-flow) restructured onto the repo `SKILL.md` template, plus `scripts/check-semver.py` and its cross-reference entries
- Migrate `ceh-coding-agent` from agent-skills at `1.0.0`: 8 skills, 2 agents, hooks, scripts, and the output style, reshaped to this repo's templates with content unchanged. The `delegate-bulk-reads` eval suite stays in agent-skills
- Add the cross-cutting `ceh-core` plugin for standards that hold however Claude Code is used, seeded with `usage-limit-handoff`, `delegate-bulk-reads`, the `bulk-reader` agent, and their hooks moved out of `ceh-coding-agent`
- Add a `ceh-git-workflow` PreToolUse branch guard that denies file edits on the default branch until a feature branch exists, disabled with `CEH_BRANCH_GUARD=off`
- Add `docs/ENVIRONMENT_VARIABLES.md`, the index of every environment variable any plugin reads
- Migrate `ceh-architecture` from agent-skills at `1.0.0` as a standalone use-case workflow plugin: `document-architecture` and `domain-modeling`, both invocable by name. The SessionStart invariants hook is not migrated: it injected layering rules into every session and pushed unrequested `ARCHITECTURE.md` upkeep, and the skill descriptions already carry the triggers. The README no longer points at plugins that have not migrated
- Migrate `ceh-seo` from agent-skills at `1.0.0` as a standalone use-case workflow plugin: `make-page-crawlable` (was `web-discoverability`), `pitch-project` (was `text-discoverability`), and `write-llms-txt`. The `write-llms-txt` eval suite stays in agent-skills, and references to plugins that have not migrated become prose
- Migrate `ceh-blog` from agent-skills at `1.0.0` as a standalone use-case workflow plugin: `draft-post`, `edit-post`, and `repurpose-post`. `blog-interviewer` and `blog-writer` merge into `draft-post`, which interviews when the material is thin and drafts directly when it is rich, so the shared Voice and post-type blocks exist once
- Add the shared blog voice, blog post-type structures, and GEO writing rules to `docs/CROSS_REFERENCES.md`
- Migrate `ceh-testing` from agent-skills at `1.0.0` as a cross-cutting plugin: `test-a-bug-fix`, `design-test-cases`, `audit-test-suite`, `verify-behavior-preserved`, and `close-test-risk-gaps`. The `test-suite-auditor` agent is not migrated: `audit-test-suite` gains a report-only mode for delegated runs, with the mutation-run cap. The routing doc `docs/TESTING_WORKFLOW.md` stays in agent-skills
- Migrate `ceh-python-service` from agent-skills at `1.0.0` as a stack plugin: seven skills renamed to say what they apply to (`write-fastapi-endpoints`, `write-postgresql-code`, `configure-python-service-env`, `write-pytest-service-tests`, `add-observability`, `secure-service-code`, `model-domain`). `write-postgresql-code` merges the asyncpg, PostgreSQL schema, and Alembic skills, which fire together, the unit, integration, and system tester agents, and the test-runner scripts
- Migrate `ceh-python-library` from agent-skills at `1.0.0` as a stack plugin: `publish-python-library` (packaging, public API, and semver in one skill), `configure-python-library-env`, and `write-pytest-library-tests`
- Migrate `ceh-web-frontend` from agent-skills at `1.0.0` as a stack plugin: `configure-bun-vite-env`, `write-sveltekit-code`, `write-react-vite-code`, `write-vitest-playwright-tests`, `make-ui-accessible`, `design-ui` with its Meridian and Tidewater themes, `visualize-graph-cytoscape` with its references, template, and converter script, the TypeScript tester agents, and the test-runner scripts
- Add the shared Python environment and testing foundations, the design-test-cases hand-off, the asyncpg pool call, the layer boundaries, and the audit findings report to `docs/CROSS_REFERENCES.md`, the three `ceh-testing` dependency edges to `docs/PLUGIN_DEPENDENCIES.md`, and the test-target variables to `docs/ENVIRONMENT_VARIABLES.md`
- Migrate `ceh-plan-build-review` from agent-skills at `1.0.0` as a use-case workflow plugin: `plan-fullstack-app-iteratively`, `plan-fullstack-app-to-mvp`, `implement-from-plan`, `review-against-plan`, and `patch-built-version`, restructured onto the repo `SKILL.md` template with every rule kept. `plan-schema.md`, `section-specs.md`, `audit-checklist.md`, and `implementation-gotchas.md` live once in the plugin-level `references/` folder and are read through `${CLAUDE_PLUGIN_ROOT}`. `plan-schema.md` is the single source for file naming, version families, and frontmatter, and the implement, patch, and review skills read the gotchas as well as the planners
- Migrate `ceh-documentation` from agent-skills at `1.0.0` as a use-case workflow plugin: `write-project-docs`, `write-guides-and-runbooks`, `write-api-reference`, `write-concept-docs`, and `write-examples`, restructured onto the repo `SKILL.md` template with every rule kept. `docs-standard.md` lives once in the plugin-level `references/` folder, read by the four writing skills, and references to plugins that have not migrated become prose
- Add the §02 Mermaid diagram requirement, the patch ITER frontmatter, and the planners' "Plan families and versions" prose to `docs/CROSS_REFERENCES.md`
- Migrate `ceh-ag-ui` from agent-skills at `1.0.0` as a stack plugin: `build-ag-ui`, `add-canvas-component`, `build-ag-ui-agent`, `add-live-state-panel`, and `add-human-approval`, restructured onto the repo `SKILL.md` template with every rule kept, plus the bundled canvas template and agent server unchanged. It depends on `ceh-web-frontend` for the `design-ui` theme, and its worked examples land in a new root `examples/ceh-ag-ui/`
- Migrate `ceh-usability-audit` from agent-skills at `1.0.0` as a use-case workflow plugin: `walk-first-run` (was `first-run-walkthrough`), `audit-interface`, `audit-error-messages`, `write-plain-language` (was `plain-language-pass`), and the `novice-walker` agent, restructured onto the repo templates with every rule kept. Hand-offs point at this repo's skill names. The persona table and severity scale that `walk-first-run` and `audit-interface` each carried now live once in the plugin-level `references/personas-and-severity.md`, both skills run at `high` effort instead of `xhigh`, and `audit-interface` gains a `compatibility` field
- Migrate `ceh-business-plan` (`develop-business-plan`), `ceh-git-datastore` (`build-git-datastore`, `migrate-git-datastore`), and `ceh-workflow-builder` (`build-agentic-workflow`, `interview-workflow-task`) from agent-skills as use-case workflow plugins, each moved as is at its agent-skills version with the content unchanged. Their `repository` URL now points at this repo, and references to `ceh-evaluation` and `ceh-orchestration`, which stay archived, are dropped. `ceh-git-datastore` points at `ceh-python-service:write-postgresql-code` and `ceh-coding-agent:document-architecture`, where the skills it named now live
- Document in `CLAUDE.md` that evals use Anthropic's tools: `skill-creator` for one skill and `claude plugin eval` for a whole plugin, and that the archived `ceh-evaluation` plugin is not to be run. `plugins/*/evals/results/` is git-ignored
- Migrate `ceh-readme` from agent-skills into `ceh-git-workflow` as the `update-readme` skill instead of a one-skill plugin: it fires at the same moment as `update-changelog`, reads the same git diff, and the `pull-request` and `release` sequences already carry a README step, which now names it. Every "the ceh-readme plugin" pointer in `ceh-documentation`, `ceh-seo`, and `ceh-usability-audit` becomes `ceh-git-workflow:update-readme`
- Add the usability persona set and severity scale and the AG-UI styling lock to `docs/CROSS_REFERENCES.md`, and the `ceh-ag-ui` → `ceh-web-frontend` edge to `docs/PLUGIN_DEPENDENCIES.md`
- Add six model-only specialist skills to `ceh-business-plan`, for use once the PMF gate passes: `review-business-plan` (report-only board review on seven lenses), `sharpen-strategy`, `stress-test-unit-economics`, `plan-go-to-market`, `run-premortem`, and `set-operating-plan`. Each writes one subsection into the existing 13-section schema, and `develop-business-plan` stays the only slash command and names the specialist to run next. `business-plan-schema.md` moves to the plugin `references/` because seven skills now share it. No version bump, since no release tag exists yet
- Add a `SubagentStart` hook to `ceh-coding-agent` that gives subagents the contract directive and the less-code digest, which `SessionStart` and `UserPromptSubmit` never deliver inside a subagent. Agents without the Skill tool are pointed at the contract file, and the read-only `Explore`, `Plan` and `bulk-reader` agents are skipped
- Migrate the documentation that still applies from agent-skills: `docs/TESTING_WORKFLOW.md` rewritten for this repo's skill and agent names, five `docs/CROSS_REFERENCES.md` entries (auto-merge probe, blog location and destination, blog repurpose handoff, git datastore hard stops, the workflow spec's nine questions) and its update protocol, the dependency behavior, edge rules, non-edge references, and bundle membership in `docs/PLUGIN_DEPENDENCIES.md`, and the README prerequisites, plugin-agent limitations, and verify step

### Changed

- Split `plugins/` into `plugins/scenarios/` for the five `ceh-scenario-*` bundles and `plugins/standalone/` for every other plugin. Plugin names and versions are unchanged. `validate.py` now globs `plugins/*/ceh-*`, and `marketplace.json`, the README install paths, the docs, and the `add-plugin-component` skill point at the new locations. Local `--plugin-dir` or settings paths that use `plugins/ceh-*` need updating
- Merge `ceh-python-service` from seven skills to four: `add-observability`, `secure-service-code` and `model-domain` fire once per project, so their rules now ride on skills that load on most service work. `write-fastapi-endpoints` absorbs logging, metrics, `/health`, correlation IDs, CORS, rate limiting, input validation and layer boundaries, `write-postgresql-code` absorbs entity IDs, status enums and immutability rules, and `configure-python-service-env` absorbs secrets management. The unused `argon2-cffi` and `pyjwt` requirement, the TypeScript enum snippet and the `ceh-scaffolding` pointer are dropped, and the HTTP status table is cut to the service's own choices
- Clean up `ceh-web-frontend` without merging any skill: `write-sveltekit-code` standardizes on Svelte 5 runes (shared state in `.svelte.ts` modules instead of `writable` / `derived` stores), `make-ui-accessible` and `write-vitest-playwright-tests` serve React as well as Svelte, source-application names (challenges, reasoning panel) become generic items, and `configure-bun-vite-env` drops the naming table, import-order block and Prettier config that the tooling already enforces. The API client and `ApiRequestError` duplication between the React and SvelteKit skills is registered in `docs/CROSS_REFERENCES.md`
- Retire `ceh-architecture` before its first release: `document-architecture` moves into `ceh-coding-agent` beside `explain-codebase`, and `domain-modeling` moves into `ceh-python-service` as `model-domain`. The stack plugins ship no SessionStart invariants hooks, matching the `ceh-architecture` decision, so their skills load from descriptions alone
- Route component authoring through `skill-creator` (no eval loop unless asked) and the plugin-dev agent, hook, and MCP skills; configure plugins through environment variables only
- Point the `ceh-coding-agent` less-code hook at the full `write-less-code` skill so it loads before implementing, and gate the skill's runnable-check rule on tests being in scope
- Consolidate `ceh-git-workflow` from 11 skills to 6: `open-pr`, `merge` and `merge-flow` become `pull-request`, and `release-flow` and `hotfix` fold into `release`, so a compound request loads two skills instead of one per step
- Make `ceh-git-workflow` stack-agnostic: Python and TypeScript checks, the coverage table, and `ARCHITECTURE.md` references are replaced by stack-neutral rules
- State `disable-model-invocation`, `user-invocable`, and `license` in every skill's frontmatter and in the `SKILL.md` template; `agent-coding-contract`, `write-less-code`, `usage-limit-handoff`, `delegate-bulk-reads` and `branch` become model-only, so they no longer appear as slash commands
- Trim the descriptions of the hook-loaded skills `agent-coding-contract`, `usage-limit-handoff` and `delegate-bulk-reads` to one line each, since their hooks name them explicitly and no trigger phrases are needed
- Make `ceh-business-plan:develop-business-plan` a thin entry point that finds the plan, routes to the specialist that owns the moment, and resets `status: draft` when the gate drops below 8/8. The product-market-fit loop moves whole into a new model-only skill, `find-product-market-fit`, and every specialist description shrinks to one sentence because only the entry point triggers. The duplicated `plan-schema.md` is deleted in favour of three inlined rules
- Tighten the `ceh-business-plan` schema and specialists: `business-plan-schema.md` fixes the heading form (`## §NN Title`) and the file location, lists every section each skill writes, and gains a worked example. Each specialist now writes one named subsection before it asks anything, asks at most three questions (five for `sharpen-strategy`), and tags any line it writes outside its subsection. `sharpen-strategy` confirms before removing refused items, `plan-go-to-market` stops on a missing acquisition ceiling, and `review-business-plan` derives its verdict from the scores
- Name repo releases by release date (`vYYYY.MM.DD`) instead of a semantic version. Plugin versions stay semantic
- Require `model` in every agent's frontmatter, enforced by `validate.py`

- Name skills with a verb phrase and agents with a noun, with two exemptions (model-only standards, established terms of art). The rule lives in `CLAUDE.md` and the `SKILL.md` template guidance

- Make four `ceh-testing` skills (`test-a-bug-fix`, `verify-behavior-preserved`, `close-test-risk-gaps`, `audit-test-suite`) write no tests and run no suite unless the user asked for them: each names the test or check it would run and what stays unverified. This follows the agent coding contract without depending on it. The shared section is registered in `docs/CROSS_REFERENCES.md`
- Reword the coverage percentages in `write-pytest-service-tests`, `write-pytest-library-tests`, `write-vitest-playwright-tests` and the `ceh-web-frontend` README as a floor for finding blind spots, not a goal, so they no longer contradict `design-test-cases` and `audit-test-suite`. The `vitest-unit-tester` agent reports the regions still untested instead of a coverage delta
- Warn in `write-sveltekit-code` that shared-state modules are browser-only, because module-level state is shared across every user's request during server rendering, and guard `setSession` with `browser`
- Align the skills and agents of `ceh-testing`, `ceh-python-service`, `ceh-python-library` and `ceh-web-frontend` with the `SKILL.md` and agent templates: every skill gets an intro, `## Procedure`, and `## Rules` (existing topic sections nested under it), with `## Output`, `## Stop conditions`, and `## Hands off to` where the content already existed. The three `design-test-cases` hand-offs move to `## Hands off to`, and every tester agent gains a `Report` step, an output example, and the "not run" rule
- Align `build-agentic-workflow`, `interview-workflow-task`, `build-git-datastore` and `migrate-git-datastore` with the `SKILL.md` template: they gain the always-present `disable-model-invocation`, `user-invocable` and `license` keys, and their sections move under `## Procedure`, `## Rules`, `## Output`, `## Stop conditions` and `## Hands off to` with the existing topic sections nested as H3. `bulk-reader` gains the "cannot ask questions" rule. Body text is otherwise unchanged
- Make the 11 stack-standards skills of `ceh-python-service`, `ceh-python-library` and `ceh-web-frontend` model-only (all but `publish-python-library`, `design-ui` and `visualize-graph-cytoscape`), since they are rule sets applied while writing code, and give the three `ceh-seo` skills their slash commands back, since each is a task asked for by name
- Drop the proactive triggers from `walk-first-run` ("before shipping a README or sign-up flow") and `explain-codebase` ("before making the first change to an unfamiliar codebase"), so neither starts a costly walk nobody asked for
- Merge `plan-fullstack-app-iteratively` and `plan-fullstack-app-to-mvp` into `plan-fullstack-app`, with a mode table (next release, whole build to MVP) in place of two skills that pointed at each other. The complexity gate's STOP now offers next-release mode instead of naming another skill, and the rules that conflict between the modes are scoped to their own mode. The shared plan-file locate step moves into `plan-schema.md` under "Locating plan files", and `implement-from-plan`, `review-against-plan` and `patch-built-version` cite it. The slash commands `/ceh-plan-build-review:plan-fullstack-app-iteratively` and `...-to-mvp` no longer exist

### Fixed

- Fix a renumbered Sequencing line in `verify-behavior-preserved` that read "3. ... 2. refactor → 5."
- Fix the `ceh-python-service` description in `CLAUDE.md`, `README.md`, `plugin.json` and `marketplace.json`, which still advertised observability, security and domain modeling after those skills were removed
- Fix `CLAUDE.md` statements that had drifted from the repo: the bundled-files exemption now covers `ceh-ag-ui` and `ceh-git-datastore`, the version-bump rule says CI only checks that `plugin.json` and `marketplace.json` match, the pre-commit note names the install step and all three formatters, and the always-present frontmatter keys are stated
- Add `CEH_WORKFLOW_BUILD_DIR` and `CEH_WORKFLOW_RUN_DIR` to `docs/ENVIRONMENT_VARIABLES.md`

### Removed

- Archive the `repo-tree-mapper` agent and its `walk-repo.sh` script to `archive/ceh-coding-agent/`
- Archive `ceh-git-workflow:dependency-management` to `archive/ceh-git-workflow/` until a stack plugin can own it
- Archive the eight agent-skills plugins that have not migrated, whole and unchanged, under `archive/`: `ceh-advisor`, `ceh-evaluation`, `ceh-fabled`, `ceh-lessons-learned`, `ceh-ops`, `ceh-orchestration`, `ceh-scaffolding`, and `ceh-summarize-chat`. They are unpublished and not validated
