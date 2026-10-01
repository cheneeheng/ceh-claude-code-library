# ceh-claude-code-library

**WORK IN PROGRESS**

2026.09.30 - Migrating from [agent-skills](https://github.com/cheneeheng/agent-skills) repo.

## Plugins

| Plugin                | Install as               | Contents                                                                                                                                                                                                                                                                                                                                 |
| --------------------- | ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Scenario: Service     | `ceh-scenario-service`   | Install entry point for a Python backend service: core, coding-agent, git-workflow, testing, documentation, python-service, usability-audit, plan-build-review, git-datastore, ag-ui (and web-frontend through it). Manifest only                                                                                                        |
| Scenario: Library     | `ceh-scenario-library`   | Install entry point for a Python library: core, coding-agent, git-workflow, testing, documentation, python-library, usability-audit, plan-build-review. Manifest only                                                                                                                                                                    |
| Scenario: Web app     | `ceh-scenario-webapp`    | Install entry point for a web frontend: core, coding-agent, git-workflow, testing, documentation, web-frontend, usability-audit, plan-build-review, ag-ui. Manifest only                                                                                                                                                                 |
| Scenario: Ideation    | `ceh-scenario-ideation`  | Install entry point for shaping an idea before a stack is chosen: core, git-workflow, business-plan, plan-build-review. Manifest only                                                                                                                                                                                                    |
| Scenario: Editorial   | `ceh-scenario-editorial` | Install entry point for writing and publishing what readers see: core, git-workflow, blog, documentation, seo. Manifest only                                                                                                                                                                                                             |
| Core                  | `ceh-core`               | Standards that hold however Claude Code is used: usage-limit guard + handoff (`usage-limit-handoff`); context economy (`delegate-bulk-reads`, `bulk-reader`, opt-in read guards)                                                                                                                                                         |
| Agent Coding Contract | `ceh-coding-agent`       | Behavioral contract for coding agents (always-on via SessionStart hook); write-less-code minimalism (always-on via hooks); retroactive refactoring (`shrink-diff`, `refactor-repo`); explaining code until it lands; whole-repo orientation (`explain-codebase`); the `CEH Coding Agent` output style (always-on via `force-for-plugin`) |
| Git Workflow          | `ceh-git-workflow`       | Branching, commits, pull requests from open to merge, changelog entries, README upkeep (`update-readme`), releases including hotfixes, code review; a hook that blocks file edits on the default branch                                                                                                                                  |
| Testing               | `ceh-testing`            | Stack-agnostic testing technique: reproduce-first bug fixes (`test-a-bug-fix`), test-case design, suite audit (`audit-test-suite`), behavior-preservation checks, and the risk gaps a green suite misses                                                                                                                                 |
| Python Service        | `ceh-python-service`     | FastAPI, asyncpg, PostgreSQL schema, Alembic, uv/ruff/mypy, pytest, observability, security, and domain modeling for web services; unit, integration, and system tester agents                                                                                                                                                           |
| Python Library        | `ceh-python-library`     | Packaging and publishing, public API surface and semver, uv/ruff/mypy, and pytest for distributable libraries with no web dependencies                                                                                                                                                                                                   |
| Web Frontend          | `ceh-web-frontend`       | SvelteKit and React on Bun + Vite: TypeScript style and tooling, Vitest/Playwright testing, accessibility, UI visual design and themes, Cytoscape.js graphs; unit, integration, and system tester agents                                                                                                                                 |
| SEO                   | `ceh-seo`                | Discoverability for anything exposed to the internet: crawlable public web pages (head tags, structured data, sitemap, rendering), the `llms.txt` agent index, and the findability of README, package, and landing text                                                                                                                  |
| Blog                  | `ceh-blog`               | Blog posts in a personal, series-first voice: draft from a topic, repo, or notes (interviewing when material is thin), edit an existing draft, repurpose a finished post for X, LinkedIn, TL;DR, and newsletters                                                                                                                         |
| Plan Build Review     | `ceh-plan-build-review`  | The plan-driven development loop: plan a fullstack app one release at a time or all the way to MVP, implement from the plan, review the implementation against it, and patch a built version with small non-feature changes                                                                                                              |
| Documentation         | `ceh-documentation`      | User-facing documentation: a full docs set under `docs/`, user guides and operator runbooks, an exhaustive API reference, concept pages with sourced design rationale, and runnable examples                                                                                                                                             |
| AG-UI                 | `ceh-ag-ui`              | Generative-UI canvases for AG-UI agents: the agent places components from a fixed, Tidewater-styled catalogue and can never restyle them; catalogue components, a Claude-backed FastAPI agent server, live shared state, and human approval steps. Worked examples: [`examples/ceh-ag-ui/`](examples/ceh-ag-ui/)                         |
| Usability Audit       | `ceh-usability-audit`    | Measure whether a non-expert can actually use what you built: cold persona-constrained walkthroughs (`novice-walker`), a five-question interface audit across web UI/CLI/library/app surfaces, error-message rewrites, and a plain-language pass                                                                                         |
| Business Plan         | `ceh-business-plan`      | Turn a product idea or an existing app plan into a validated business plan: a product-market-fit interview loop that interrogates the weakest assumption until a readiness gate passes                                                                                                                                                   |
| Git Datastore         | `ceh-git-datastore`      | Run an app on a bare git repo instead of a database while that still fits: a gate that talks you out of it when it does not, a plumbing-only store, and the pinned-snapshot migration to Postgres or SQLite                                                                                                                              |
| Workflow Builder      | `ceh-workflow-builder`   | Turn a repetitive multi-step task into a runnable artifact: interview it into a spec, then emit one skill or a gated workflow skill with handoff schemas into the target repo                                                                                                                                                            |

### Categorization

| Tier                  | Loaded            | Plugins                                                                                                                                                      |
| --------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Scenario bundle**   | one per situation | `ceh-scenario-service`, `ceh-scenario-library`, `ceh-scenario-webapp`, `ceh-scenario-ideation`, `ceh-scenario-editorial`                                     |
| **Cross-cutting**     | most sessions     | `ceh-core`, `ceh-coding-agent`, `ceh-git-workflow`, `ceh-testing`                                                                                            |
| **Use-case workflow** | per activity      | `ceh-seo`, `ceh-blog`, `ceh-plan-build-review`, `ceh-documentation`, `ceh-usability-audit`, `ceh-business-plan`, `ceh-git-datastore`, `ceh-workflow-builder` |
| **Stack / build**     | per project type  | `ceh-python-service`, `ceh-python-library`, `ceh-web-frontend`, `ceh-ag-ui`                                                                                  |

---

## Skills

### Core (`ceh-core`)

| Skill               | Invoke                       | When                                                                                                                                               |
| ------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage Limit Handoff | Model-only, no slash command | Auto via PostToolUse guard hook when 5h or weekly usage crosses the threshold (default 90%) — stop cleanly, write a handoff artifact, end the turn |
| Delegate Bulk Reads | Model-only, no slash command | Before dispatching the `bulk-reader` agent, and before acting on its summary — the delegation prompt and the verification rules                    |

### Agent Coding Contract (`ceh-coding-agent`)

| Skill                    | Invoke                                       | When                                                                                                                                                                                                          |
| ------------------------ | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Agent Coding Contract    | Model-only, no slash command                 | Start of any coding session (auto via SessionStart hook) — core rules, five-step workflow, stop conditions, non-goals                                                                                         |
| Write Less Code          | Model-only, no slash command                 | Every coding session (auto — per-turn digest via hook) — the minimalism ladder (YAGNI → stdlib → native → installed dep → one line)                                                                           |
| Shrink Diff              | `/ceh-coding-agent:shrink-diff`              | Branch functionally done, before the PR — retroactively apply write-less-code to the accumulated diff vs `main`                                                                                               |
| Refactor Repo            | `/ceh-coding-agent:refactor-repo`            | Manual only — propose-then-apply refactor campaign over the whole repo or a named module                                                                                                                      |
| Explain Until Understood | `/ceh-coding-agent:explain-until-understood` | Explaining a subsystem, design, or diff to the person in the session: stated floor, foundations first, verified claims, ASCII pictures, one walked case, and the escalation ladder when an explanation misses |
| Explain Codebase         | `/ceh-coding-agent:explain-codebase`         | Go through a whole repo and write what each component does, how they connect, and key flows into the ignored `.agents_workspace/CODEBASE_EXPLAINED.md`                                                        |
| Document Architecture    | `/ceh-coding-agent:document-architecture`    | Writing or updating the living `.agents_workspace/ARCHITECTURE.md`: 3-second Overview, Mermaid diagrams, Key Decisions log; also when a re-plan changes system shape                                          |

### Git Workflow (`ceh-git-workflow`)

| Skill            | Invoke                               | Auto-loads when                                                                                                                                                           |
| ---------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Branch           | Model-only, no slash command         | Creating or naming a branch; a PreToolUse hook denies file edits on the default branch until one exists                                                                   |
| Commit           | `/ceh-git-workflow:commit`           | Writing a commit message or staging changes                                                                                                                               |
| Pull Request     | `/ceh-git-workflow:pull-request`     | A branch is heading into `main`: open a PR, merge it (or a local branch), or land the branch in one pass — changelog under `[Unreleased]` → commit → PR → merge → cleanup |
| Release          | `/ceh-git-workflow:release`          | Ship a version: bump → changelog → PR → merge → tag → GitHub release; also tag-only and the hotfix variant                                                                |
| Code Review      | `/ceh-git-workflow:code-review`      | Reviewing a PR or leaving review comments                                                                                                                                 |
| Update Changelog | `/ceh-git-workflow:update-changelog` | Generate or update CHANGELOG.md, write release notes, or log a change under `[Unreleased]`                                                                                |
| Update README    | `/ceh-git-workflow:update-readme`    | Refresh `README.md` after a significant change (new feature, changed install steps, new API surface); does nothing when nothing material changed                          |

### Testing (`ceh-testing`)

| Skill                     | Invoke                                   | When                                                                                                                            |
| ------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Test a Bug Fix            | `/ceh-testing:test-a-bug-fix`            | A bug, crash, or regression is being fixed: failing test first, prove it goes red without the fix, bisect on it                 |
| Design Test Cases         | `/ceh-testing:design-test-cases`         | Deciding which inputs and scenarios to cover: partitions, boundaries, decision tables, state transitions, properties, fuzzing   |
| Audit Test Suite          | `/ceh-testing:audit-test-suite`          | Finding out whether a passing suite would catch a defect: assertion quality, mutation testing on the diff, flakiness            |
| Verify Behavior Preserved | `/ceh-testing:verify-behavior-preserved` | Before a refactor, extraction, dependency or runtime upgrade, or port: characterization tests, golden files, a differential run |
| Close Test Risk Gaps      | `/ceh-testing:close-test-risk-gaps`      | Pre-completion gate: concurrency, contract drift, performance, authorization, and migration/rollout gaps                        |

### Python Service (`ceh-python-service`)

| Skill                        | Invoke                                             | When                                                                                                                                                              |
| ---------------------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Write FastAPI Endpoints      | `/ceh-python-service:write-fastapi-endpoints`      | Route handlers, dependencies, lifespan, exception handlers, layer boundaries, logging, metrics, `/health`, correlation IDs, CORS, rate limiting, input validation |
| Write PostgreSQL Code        | `/ceh-python-service:write-postgresql-code`        | Schema design, entity IDs, status enums, asyncpg queries, transactions, tenant isolation, pool config, Alembic migrations                                         |
| Configure Python Service Env | `/ceh-python-service:configure-python-service-env` | Editing `pyproject.toml`, uv commands, type hints, ruff/mypy config, secrets and `.env` files                                                                     |
| Write pytest Service Tests   | `/ceh-python-service:write-pytest-service-tests`   | Creating or modifying test files, fixtures, or mocks                                                                                                              |

### Python Library (`ceh-python-library`)

| Skill                        | Invoke                                             | When                                                                                            |
| ---------------------------- | -------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Configure Python Library Env | `/ceh-python-library:configure-python-library-env` | Editing `pyproject.toml`, uv commands, type hints, ruff/mypy config                             |
| Write pytest Library Tests   | `/ceh-python-library:write-pytest-library-tests`   | Creating or modifying test files, fixtures, or mocks                                            |
| Publish Python Library       | `/ceh-python-library:publish-python-library`       | Build backend, src layout, PyPI publishing, `__init__.py`/`__all__`, deprecations, semver bumps |

### Web Frontend (`ceh-web-frontend`)

| Skill                           | Invoke                                            | When                                                                                                                         |
| ------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Configure Bun + Vite Env        | `/ceh-web-frontend:configure-bun-vite-env`        | Bun/Vite setup, scripts, deps, TypeScript style, ESLint/Prettier                                                             |
| Write SvelteKit Code            | `/ceh-web-frontend:write-sveltekit-code`          | Editing Svelte routes, shared `.svelte.ts` state, components, or the API client                                              |
| Write React + Vite Code         | `/ceh-web-frontend:write-react-vite-code`         | Editing React components, hooks, routing, or `vite.config.ts`                                                                |
| Write Vitest + Playwright Tests | `/ceh-web-frontend:write-vitest-playwright-tests` | Writing `.test.ts`, `.test.tsx`, or `.spec.ts` files, or MSW handlers                                                        |
| Make UI Accessible              | `/ceh-web-frontend:make-ui-accessible`            | Writing component markup (Svelte or React)                                                                                   |
| Design UI                       | `/ceh-web-frontend:design-ui`                     | Any frontend visual design decision: layout, hierarchy, navigation, states, finishing recipes, Meridian and Tidewater themes |
| Visualize Graph (Cytoscape)     | `/ceh-web-frontend:visualize-graph-cytoscape`     | A network, dependency map, org chart, or any clickable node-link diagram with Cytoscape.js                                   |

### SEO (`ceh-seo`)

| Skill               | Invoke                       | When                                                                                                                                          |
| ------------------- | ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Make Page Crawlable | Model-only, no slash command | Shipping or creating a public web page: per-page head checklist, sitemap and robots, JSON-LD, content in the initial HTML, GEO citation rules |
| Write llms.txt      | Model-only, no slash command | Creating or updating the `llms.txt` reading list for AI agents: positional format, link curation, `## Optional`, markdown over HTML           |
| Pitch Project       | Model-only, no slash command | Writing the README first screen, package description and keywords, GitHub topics, marketplace listings, or landing copy                       |

### Blog (`ceh-blog`)

| Skill          | Invoke                     | When                                                                                                                        |
| -------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Draft Post     | `/ceh-blog:draft-post`     | A new post from a topic, idea, repo, or experience (interview first) or from notes, bullets, or an outline (draft directly) |
| Edit Post      | `/ceh-blog:edit-post`      | An existing draft: diagnosis first, then a full revision that keeps the author's voice                                      |
| Repurpose Post | `/ceh-blog:repurpose-post` | A finished post to adapt into a Twitter/X thread, LinkedIn post, TL;DR, or newsletter blurb                                 |

### Plan Build Review (`ceh-plan-build-review`)

| Skill                          | Invoke                                                  | When                                                                                                                             |
| ------------------------------ | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Plan Fullstack App Iteratively | `/ceh-plan-build-review:plan-fullstack-app-iteratively` | Planning the next release, feature, or a greenfield skeleton: one scoped `SKELETON.md` or `ITER_NN.md` per session               |
| Plan Fullstack App to MVP      | `/ceh-plan-build-review:plan-fullstack-app-to-mvp`      | Planning the complete build to a working MVP in one session, behind a complexity gate that falls back to the iterative planner   |
| Implement From Plan            | `/ceh-plan-build-review:implement-from-plan`            | Building a `SKELETON.md` or `ITER_NN.md` section by section, resolving iteration pointers to the authoritative spec              |
| Review Against Plan            | `/ceh-plan-build-review:review-against-plan`            | Auditing the code against a plan: gaps, deviations, and errors per section, fixed and reported                                   |
| Patch Built Version            | `/ceh-plan-build-review:patch-built-version`            | A small non-feature change to a built version, recorded as a `patch: true` `ITER_NN.md`; features route to the iterative planner |

### Documentation (`ceh-documentation`)

| Skill                     | Invoke                                         | When                                                                                                                        |
| ------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Write Project Docs        | `/ceh-documentation:write-project-docs`        | A full docs set under `docs/` for the workspace or a given project path, one job per page; sequences the three skills below |
| Write Guides and Runbooks | `/ceh-documentation:write-guides-and-runbooks` | User guides and operator runbooks: one section per audience, task-oriented verifiable procedures                            |
| Write API Reference       | `/ceh-documentation:write-api-reference`       | The exhaustive reference: every public item counted against the surface, with "Added in" markers                            |
| Write Concept Docs        | `/ceh-documentation:write-concept-docs`        | Concept pages: the mental model and the design rationale, each traced to a source, never invented                           |
| Write Examples            | `/ceh-documentation:write-examples`            | New runnable programs under `examples/`: a numbered feature tour and copy-paste recipes, each run before it is kept         |

### AG-UI (`ceh-ag-ui`)

| Skill                | Invoke                            | When                                                                                                                                                                       |
| -------------------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Build AG-UI          | `/ceh-ag-ui:build-ag-ui`          | Starting a generative-UI canvas for an AG-UI agent: own template or the bundled one (React + Vite + `@ag-ui/client`, seven catalogue components, mock agent), styling lock |
| Add Canvas Component | `/ceh-ag-ui:add-canvas-component` | Adding a component the agent can place: agent-facing description, content-only zod schema, example fixture, theme-only markup, mock verification                           |
| Build AG-UI Agent    | `/ceh-ag-ui:build-ag-ui-agent`    | Building the Claude-backed AG-UI server: append-only transcript per thread, end the run on a frontend tool call, held backend results, `RUN_ERROR` on every failure        |
| Add Live State Panel | `/ceh-ag-ui:add-live-state-panel` | A live value the agent keeps updating: `STATE_SNAPSHOT` / `STATE_DELTA`, one writer per key, a fixed validated panel                                                       |
| Add Human Approval   | `/ceh-ag-ui:add-human-approval`   | The agent must ask before acting: AG-UI interrupts, a fixed approval card, one resume for every open interrupt                                                             |

### Usability Audit (`ceh-usability-audit`)

| Skill                | Invoke                                      | When                                                                                                                                                           |
| -------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Walk First Run       | `/ceh-usability-audit:walk-first-run`       | Can a stranger reach first success: install, sign-up, setup, onboarding; cold persona walkers, milestones capped by an action budget, looped to a 5-point gate |
| Audit Interface      | `/ceh-usability-audit:audit-interface`      | They are already in: the five questions every web UI/CLI/API/screen must answer unasked, an anti-pattern sweep, the naming test, and the persona battery       |
| Audit Error Messages | `/ceh-usability-audit:audit-error-messages` | Anything a user reads when something goes wrong: the three-part rule (what happened, what was wrong, what to do next) over every user-reachable string         |
| Write Plain Language | `/ceh-usability-audit:write-plain-language` | Labels, help text, empty states, confirmation dialogs, onboarding copy: vocabulary floor, sentence rules, and an explicit never-simplify list                  |

### Business Plan (`ceh-business-plan`)

| Skill                 | Invoke                                     | When                                                                                                                                                |
| --------------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Develop Business Plan | `/ceh-business-plan:develop-business-plan` | A product idea or an existing plan needs product-market fit: drafts from any plan, PRD, or pitch, or interviews, then loops until a PMF gate passes |

### Git Datastore (`ceh-git-datastore`)

| Skill                 | Invoke                                     | When                                                                                                                                                       |
| --------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Build Git Datastore   | `/ceh-git-datastore:build-git-datastore`   | An app needs persistence but not a database yet: a gate that often says no, then a plumbing-only store on a bare git repo                                  |
| Migrate Git Datastore | `/ceh-git-datastore:migrate-git-datastore` | The store has to become a real database, or you need to know whether it is time: schema inference, pinned-snapshot export, backfill, verification, cutover |

### Workflow Builder (`ceh-workflow-builder`)

| Skill                   | Invoke                                          | When                                                                                                                                      |
| ----------------------- | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Build Agentic Workflow  | `/ceh-workflow-builder:build-agentic-workflow`  | Turning a repetitive multi-step task into a skill or gated workflow: the one-skill-vs-workflow gate, handoff schemas, leaf-first emission |
| Interview Workflow Task | `/ceh-workflow-builder:interview-workflow-task` | The task is not yet described: nine questions answered into a workflow spec file, nothing built                                           |

---

## Agents

### Core (`ceh-core`)

| Agent       | Invoke                  | When                                                                                                                                                       |
| ----------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bulk Reader | `/ceh-core:bulk-reader` | Read large or numerous files on Haiku and return a compressed, line-anchored answer to one question, keeping the file contents out of the caller's context |

### Python Service (`ceh-python-service`)

| Agent                     | Invoke                                                    | When                                                                     |
| ------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------ |
| Pytest Unit Tester        | `@"ceh-python-service:pytest-unit-tester (agent)"`        | Isolated, mocked unit tests for a function, class, or module             |
| Pytest Integration Tester | `@"ceh-python-service:pytest-integration-tester (agent)"` | Tests for module boundaries and real-database interactions               |
| Pytest System Tester      | `@"ceh-python-service:pytest-system-tester (agent)"`      | Full end-to-end scenarios against the real stack (explicit request only) |

### Web Frontend (`ceh-web-frontend`)

| Agent                     | Invoke                                                  | When                                                             |
| ------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------- |
| Vitest Unit Tester        | `@"ceh-web-frontend:vitest-unit-tester (agent)"`        | Isolated unit tests for TypeScript functions or modules          |
| Vitest Integration Tester | `@"ceh-web-frontend:vitest-integration-tester (agent)"` | Components wired with real shared state and MSW network handlers |
| Playwright System Tester  | `@"ceh-web-frontend:playwright-system-tester (agent)"`  | Playwright E2E or smoke tests against a running stack            |

### Usability Audit (`ceh-usability-audit`)

| Agent         | Invoke                                         | When                                                                                                                                               |
| ------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Novice Walker | `@"ceh-usability-audit:novice-walker (agent)"` | Walk a target cold under one persona toward one goal and report where it stalled, without using what it knows about such tools (Sonnet, read-only) |

---

## Installing in Claude Code

### Step 1 — Add the marketplace

```
/plugin marketplace add cheneeheng/ceh-claude-code-library
```

### Step 2 — Install a scenario bundle

Pick the bundle that matches your situation. Each installs its plugins as dependencies.

```
/plugin install ceh-scenario-service@ceh-claude-code-library --scope user
/plugin install ceh-scenario-library@ceh-claude-code-library --scope user
/plugin install ceh-scenario-webapp@ceh-claude-code-library --scope user
/plugin install ceh-scenario-ideation@ceh-claude-code-library --scope user
/plugin install ceh-scenario-editorial@ceh-claude-code-library --scope user
```

What each bundle installs is listed in [`docs/PLUGIN_DEPENDENCIES.md`](docs/PLUGIN_DEPENDENCIES.md).

### Or install plugins individually

```
/plugin install ceh-core@ceh-claude-code-library --scope user
/plugin install ceh-coding-agent@ceh-claude-code-library --scope user
/plugin install ceh-git-workflow@ceh-claude-code-library --scope user
/plugin install ceh-testing@ceh-claude-code-library --scope user
/plugin install ceh-python-service@ceh-claude-code-library --scope user
/plugin install ceh-python-library@ceh-claude-code-library --scope user
/plugin install ceh-web-frontend@ceh-claude-code-library --scope user
/plugin install ceh-seo@ceh-claude-code-library --scope user
/plugin install ceh-blog@ceh-claude-code-library --scope user
/plugin install ceh-plan-build-review@ceh-claude-code-library --scope user
/plugin install ceh-documentation@ceh-claude-code-library --scope user
/plugin install ceh-ag-ui@ceh-claude-code-library --scope user
/plugin install ceh-usability-audit@ceh-claude-code-library --scope user
/plugin install ceh-business-plan@ceh-claude-code-library --scope user
/plugin install ceh-git-datastore@ceh-claude-code-library --scope user
/plugin install ceh-workflow-builder@ceh-claude-code-library --scope user
```

Dependencies install automatically: each stack plugin brings `ceh-testing`, and `ceh-ag-ui` brings
`ceh-web-frontend`.

### Manual installation (alternative)

```bash
git clone https://github.com/cheneeheng/ceh-claude-code-library.git ~/ceh-claude-code-library
```

Then add plugin paths to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "plugins": [
    { "path": "~/ceh-claude-code-library/plugins/ceh-scenario-service" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-scenario-library" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-scenario-webapp" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-scenario-ideation" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-scenario-editorial" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-core" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-coding-agent" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-git-workflow" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-testing" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-python-service" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-python-library" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-web-frontend" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-seo" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-blog" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-plan-build-review" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-documentation" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-ag-ui" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-usability-audit" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-business-plan" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-git-datastore" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-workflow-builder" }
  ]
}
```

---

## Tools

| Tool             | Path                      | Purpose                                                                                                                                                                                         |
| ---------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| validate-plugins | `tools/validate-plugins/` | Repo-integrity checker run by CI (`.github/workflows/validate.yml`): plugin manifests, skill/agent frontmatter, file and skill references, dependencies, and script syntax. Stdlib-only Python. |

### Formatting

`.pre-commit-config.yaml` formats staged files on commit: ruff for Python, prettier (official npm
package) for Markdown and JSON, shfmt for shell scripts. Enable it once per clone:

```bash
pre-commit install
```
