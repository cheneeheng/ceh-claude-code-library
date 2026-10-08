# ceh-claude-code-library

Claude Code plugins that guide autonomous agents through a product's life: shaping the idea,
building and proving the software, and getting it in front of the people who should find it. They
are written for agents first and people second. An agent follows them with no human watching, and a
person using Claude Code gets the same guidance and can override it with an explicit instruction.
Plugins are organized around **use cases**: load the ones that match what you are building.

**Vision:** [`docs/VISION.md`](docs/VISION.md) — the identity, scope, and principles that settle
decisions about this repo.

**Guides:** [`docs/TESTING_WORKFLOW.md`](docs/TESTING_WORKFLOW.md) — how `ceh-testing` and the three
stack testing skills route between each other, with the trigger phrases and sequence for each moment.

**Versions:** each plugin keeps its own semantic version, and the repo has no releases.
[`CHANGELOG.md`](CHANGELOG.md) groups changes by the date each PR was opened, and
[`docs/PLUGIN_VERSIONS.md`](docs/PLUGIN_VERSIONS.md) lists every plugin's current version.

## Plugins

| Plugin               | Install as                 | Contents                                                                                                                                                                                                                                                                                                                         |
| -------------------- | -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Scenario: Service    | `ceh-scenario-service`     | Install entry point for a Python backend service: every-session, coding-conduct, codebase-explanation, git-workflow, testing, documentation, python-service, usability-audit, plan-build-review, git-datastore. Manifest only                                                                                                    |
| Scenario: Library    | `ceh-scenario-library`     | Install entry point for a Python library: every-session, coding-conduct, codebase-explanation, git-workflow, testing, documentation, python-library, usability-audit, plan-build-review. Manifest only                                                                                                                           |
| Scenario: Web app    | `ceh-scenario-webapp`      | Install entry point for a web frontend: every-session, coding-conduct, codebase-explanation, git-workflow, testing, documentation, web-frontend, usability-audit, plan-build-review, ag-ui. Manifest only                                                                                                                        |
| Scenario: Ideation   | `ceh-scenario-ideation`    | Install entry point for shaping an idea before a stack is chosen: every-session, git-workflow, business-plan, plan-build-review. Manifest only                                                                                                                                                                                   |
| Scenario: Editorial  | `ceh-scenario-editorial`   | Install entry point for writing and publishing what readers see: every-session, git-workflow, blog, documentation, seo. Manifest only                                                                                                                                                                                            |
| Every Session        | `ceh-every-session`        | Standards every session loads, however Claude Code is used: usage-limit guard + handoff (`usage-limit-handoff`); context economy (`delegate-bulk-reads`, `bulk-reader`, opt-in read guards)                                                                                                                                      |
| Coding Conduct       | `ceh-coding-conduct`       | Behavioral contract for coding agents (always-on via SessionStart hook); write-less-code minimalism (always-on via hooks); retroactive refactoring (`shrink-diff`, `refactor-repo`); the `CEH Coding Conduct` output style (always-on via `force-for-plugin`)                                                                    |
| Codebase Explanation | `ceh-codebase-explanation` | Leave a codebase understood: explaining a subsystem, design, or diff until it lands (`explain-until-understood`); whole-repo orientation (`explain-codebase`); the living architecture document (`document-architecture`)                                                                                                        |
| Git Workflow         | `ceh-git-workflow`         | Branching, commits, pull requests from open to merge, changelog entries, README upkeep (`update-readme`), releases including hotfixes, code review; a hook that blocks file edits on the default branch                                                                                                                          |
| Testing              | `ceh-testing`              | Stack-agnostic testing technique: reproduce-first bug fixes (`test-a-bug-fix`), test-case design, suite audit (`audit-test-suite`), behavior-preservation checks, and the risk gaps a green suite misses                                                                                                                         |
| Python Service       | `ceh-python-service`       | FastAPI, asyncpg, PostgreSQL schema, Alembic, uv/ruff/mypy, and pytest for web services; unit, integration, and system tester agents                                                                                                                                                                                             |
| Python Library       | `ceh-python-library`       | Packaging and publishing, public API surface and semver, uv/ruff/mypy, and pytest for distributable libraries with no web dependencies                                                                                                                                                                                           |
| Web Frontend         | `ceh-web-frontend`         | SvelteKit and React on Bun + Vite: TypeScript style and tooling, Vitest/Playwright testing, accessibility, Cytoscape.js graphs; unit, integration, and system tester agents. Brings `ceh-ui-design` for visual design                                                                                                            |
| UI Design            | `ceh-ui-design`            | Framework-agnostic visual design for any UI or HTML page: layout archetypes, hierarchy, navigation and in-page contents, states, finishing recipes, and the Meridian and Tidewater themes                                                                                                                                        |
| SEO                  | `ceh-seo`                  | Discoverability for anything exposed to the internet: crawlable public web pages (head tags, structured data, sitemap, rendering), the `llms.txt` agent index, and the findability of README, package, and landing text                                                                                                          |
| Blog                 | `ceh-blog`                 | Blog posts in a personal, series-first voice: draft from a topic, repo, or notes (interviewing when material is thin), edit an existing draft, repurpose a finished post for X, LinkedIn, TL;DR, and newsletters                                                                                                                 |
| Plan Build Review    | `ceh-plan-build-review`    | The plan-driven development loop: plan a fullstack app one release at a time or all the way to MVP, implement from the plan, review the implementation against it, and patch a built version with small non-feature changes                                                                                                      |
| Documentation        | `ceh-documentation`        | User-facing documentation: a full docs set under `docs/`, user guides and operator runbooks, an exhaustive API reference, concept pages with sourced design rationale, and runnable examples                                                                                                                                     |
| AG-UI                | `ceh-ag-ui`                | Generative-UI canvases for AG-UI agents: the agent places components from a fixed, Tidewater-styled catalogue and can never restyle them; catalogue components, a Claude-backed FastAPI agent server, live shared state, and human approval steps. Worked examples: [`examples/ceh-ag-ui/`](examples/ceh-ag-ui/)                 |
| Usability Audit      | `ceh-usability-audit`      | Measure whether a non-expert can actually use what you built: cold persona-constrained walkthroughs (`newcomer-simulator`), a five-question interface audit across web UI/CLI/library/app surfaces, error-message rewrites, and a plain-language pass                                                                            |
| Business Plan        | `ceh-business-plan`        | Turn a product idea or an existing app plan into a validated business plan: a product-market-fit interview loop that interrogates the weakest assumption until a readiness gate passes, then a board-style review and five specialist passes on strategy, unit economics, go-to-market, premortem, and the 90-day operating plan |
| Git Datastore        | `ceh-git-datastore`        | Run an app on a bare git repo instead of a database while that still fits: a gate that talks you out of it when it does not, a plumbing-only store, and the pinned-snapshot migration to Postgres or SQLite                                                                                                                      |
| Workflow Builder     | `ceh-workflow-builder`     | Turn a repetitive multi-step task into a runnable artifact: interview it into a spec, then emit one skill or a gated workflow skill with handoff schemas into the target repo                                                                                                                                                    |
| Workflow Runner      | `ceh-workflow-runner`      | Run a built `flow.yaml` workflow, interactive or headless: stages in order, approvals, gates, run state and resume. Install it wherever a flow runs, without the builder                                                                                                                                                         |
| Competitor Analysis  | `ceh-competitor-analysis`  | Study a competitor's repo or product and learn from it: one evidence-anchored report each (breakdown, inventory, "oh wow" mechanisms, what to incorporate), then a side-by-side comparison with your own work. Repos are read as untrusted data, never run                                                                       |

### Categorization

| Tier                  | Loaded            | Plugins                                                                                                                                                                                                                                                     |
| --------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Scenario bundle**   | one per situation | `ceh-scenario-service`, `ceh-scenario-library`, `ceh-scenario-webapp`, `ceh-scenario-ideation`, `ceh-scenario-editorial`                                                                                                                                    |
| **Cross-cutting**     | most sessions     | `ceh-every-session`, `ceh-coding-conduct`, `ceh-git-workflow`, `ceh-testing`                                                                                                                                                                                |
| **Use-case workflow** | per activity      | `ceh-seo`, `ceh-blog`, `ceh-plan-build-review`, `ceh-documentation`, `ceh-usability-audit`, `ceh-business-plan`, `ceh-git-datastore`, `ceh-workflow-builder`, `ceh-workflow-runner`, `ceh-competitor-analysis`, `ceh-ui-design`, `ceh-codebase-explanation` |
| **Stack / build**     | per project type  | `ceh-python-service`, `ceh-python-library`, `ceh-web-frontend`, `ceh-ag-ui`                                                                                                                                                                                 |

Each plugin is self-contained: a foundational standard needed by more than one plugin is duplicated
into each instead of extracted into a shared base, so one plugin per use case is all you load.
Cross-cutting plugins are the orthogonal tier. They hold a discipline that applies whatever you are
building, so they load _alongside_ a use-case plugin, not instead of one.

---

## Skills

### Every Session (`ceh-every-session`)

| Skill               | Invoke                       | When                                                                                                                                               |
| ------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage Limit Handoff | Model-only, no slash command | Auto via PostToolUse guard hook when 5h or weekly usage crosses the threshold (default 90%) — stop cleanly, write a handoff artifact, end the turn |
| Delegate Bulk Reads | Model-only, no slash command | Before dispatching the `bulk-reader` agent, and before acting on its summary — the delegation prompt and the verification rules                    |

### Coding Conduct (`ceh-coding-conduct`)

| Skill                 | Invoke                              | When                                                                                                                                |
| --------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Agent Coding Contract | Model-only, no slash command        | Start of any coding session (auto via SessionStart hook) — core rules, five-step workflow, stop conditions, non-goals               |
| Write Less Code       | Model-only, no slash command        | Every coding session (auto — per-turn digest via hook) — the minimalism ladder (YAGNI → stdlib → native → installed dep → one line) |
| Shrink Diff           | `/ceh-coding-conduct:shrink-diff`   | Branch functionally done, before the PR — retroactively apply write-less-code to the accumulated diff vs `main`                     |
| Refactor Repo         | `/ceh-coding-conduct:refactor-repo` | Manual only — propose-then-apply refactor campaign over the whole repo or a named module                                            |

### Codebase Explanation (`ceh-codebase-explanation`)

| Skill                    | Invoke                                               | When                                                                                                                                                                                                          |
| ------------------------ | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Explain Until Understood | `/ceh-codebase-explanation:explain-until-understood` | Explaining a subsystem, design, or diff to the person in the session: stated floor, foundations first, verified claims, ASCII pictures, one walked case, and the escalation ladder when an explanation misses |
| Explain Codebase         | `/ceh-codebase-explanation:explain-codebase`         | Go through a whole repo and write what each component does, how they connect, and key flows into the ignored `.agents_workspace/CODEBASE_EXPLAINED.md`                                                        |
| Document Architecture    | `/ceh-codebase-explanation:document-architecture`    | Writing or updating the living `.agents_workspace/ARCHITECTURE.md`: 3-second Overview, Mermaid diagrams, Key Decisions log; also when a re-plan changes system shape                                          |

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

| Skill                        | Invoke                       | When                                                                                                                                                              |
| ---------------------------- | ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Write FastAPI Endpoints      | Model-only, no slash command | Route handlers, dependencies, lifespan, exception handlers, layer boundaries, logging, metrics, `/health`, correlation IDs, CORS, rate limiting, input validation |
| Write PostgreSQL Code        | Model-only, no slash command | Schema design, entity IDs, status enums, asyncpg queries, transactions, tenant isolation, pool config, Alembic migrations                                         |
| Configure Python Service Env | Model-only, no slash command | Editing `pyproject.toml`, uv commands, type hints, ruff/mypy config, secrets and `.env` files                                                                     |
| Write pytest Service Tests   | Model-only, no slash command | Creating or modifying test files, fixtures, or mocks                                                                                                              |

### Python Library (`ceh-python-library`)

| Skill                        | Invoke                                       | When                                                                                            |
| ---------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Configure Python Library Env | Model-only, no slash command                 | Editing `pyproject.toml`, uv commands, type hints, ruff/mypy config                             |
| Write pytest Library Tests   | Model-only, no slash command                 | Creating or modifying test files, fixtures, or mocks                                            |
| Publish Python Library       | `/ceh-python-library:publish-python-library` | Build backend, src layout, PyPI publishing, `__init__.py`/`__all__`, deprecations, semver bumps |

### Web Frontend (`ceh-web-frontend`)

| Skill                           | Invoke                                        | When                                                                                       |
| ------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Configure Bun + Vite Env        | Model-only, no slash command                  | Bun/Vite setup, scripts, deps, TypeScript style, ESLint/Prettier                           |
| Write SvelteKit Code            | Model-only, no slash command                  | Editing Svelte routes, shared `.svelte.ts` state, components, or the API client            |
| Write React + Vite Code         | Model-only, no slash command                  | Editing React components, hooks, routing, or `vite.config.ts`                              |
| Write Vitest + Playwright Tests | Model-only, no slash command                  | Writing `.test.ts`, `.test.tsx`, or `.spec.ts` files, or MSW handlers                      |
| Make UI Accessible              | Model-only, no slash command                  | Writing component markup (Svelte or React)                                                 |
| Visualize Graph (Cytoscape)     | `/ceh-web-frontend:visualize-graph-cytoscape` | A network, dependency map, org chart, or any clickable node-link diagram with Cytoscape.js |

### UI Design (`ceh-ui-design`)

| Skill     | Invoke                     | When                                                                                                                                                        |
| --------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Design UI | `/ceh-ui-design:design-ui` | Any visual design decision for a UI or HTML page: layout, hierarchy, navigation, in-page contents, states, finishing recipes, Meridian and Tidewater themes |

### SEO (`ceh-seo`)

| Skill                      | Invoke                                | When                                                                                                                                          |
| -------------------------- | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Make Page Crawlable        | `/ceh-seo:make-page-crawlable`        | Shipping or creating a public web page: per-page head checklist, sitemap and robots, JSON-LD, content in the initial HTML, GEO citation rules |
| Write llms.txt             | `/ceh-seo:write-llms-txt`             | Creating or updating the `llms.txt` reading list for AI agents: positional format, link curation, `## Optional`, markdown over HTML           |
| Write Project Listing Text | `/ceh-seo:write-project-listing-text` | Writing the README first screen, package description and keywords, GitHub topics, marketplace listings, or landing copy                       |

### Blog (`ceh-blog`)

| Skill          | Invoke                     | When                                                                                                                        |
| -------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Draft Post     | `/ceh-blog:draft-post`     | A new post from a topic, idea, repo, or experience (interview first) or from notes, bullets, or an outline (draft directly) |
| Edit Post      | `/ceh-blog:edit-post`      | An existing draft: diagnosis first, then a full revision that keeps the author's voice                                      |
| Repurpose Post | `/ceh-blog:repurpose-post` | A finished post to adapt into a Twitter/X thread, LinkedIn post, TL;DR, or newsletter blurb                                 |

### Plan Build Review (`ceh-plan-build-review`)

| Skill                      | Invoke                                              | When                                                                                                                         |
| -------------------------- | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Plan Fullstack App         | `/ceh-plan-build-review:plan-fullstack-app`         | Planning a project: one scoped `SKELETON.md` or `ITER_NN.md` per session, or the whole build to MVP behind a complexity gate |
| Implement From Plan        | `/ceh-plan-build-review:implement-from-plan`        | Building a `SKELETON.md` or `ITER_NN.md` section by section, resolving iteration pointers to the authoritative spec          |
| Review Against Plan        | `/ceh-plan-build-review:review-against-plan`        | Auditing the code against a plan: gaps, deviations, and errors per section, fixed and reported                               |
| Apply Small Fix To Version | `/ceh-plan-build-review:apply-small-fix-to-version` | A small non-feature change to a built version, recorded as a `patch: true` `ITER_NN.md`; features route to the planner skill |

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

| Skill                       | Invoke                                             | When                                                                                                                                                           |
| --------------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Simulate Newcomer First Run | `/ceh-usability-audit:simulate-newcomer-first-run` | Can a stranger reach first success: install, sign-up, setup, onboarding; cold persona walkers, milestones capped by an action budget, looped to a 5-point gate |
| Audit Interface             | `/ceh-usability-audit:audit-interface`             | They are already in: the five questions every web UI/CLI/API/screen must answer unasked, an anti-pattern sweep, the naming test, and the persona battery       |
| Audit Error Messages        | `/ceh-usability-audit:audit-error-messages`        | Anything a user reads when something goes wrong: the three-part rule (what happened, what was wrong, what to do next) over every user-reachable string         |
| Write Plain Language        | `/ceh-usability-audit:write-plain-language`        | Labels, help text, empty states, confirmation dialogs, onboarding copy: vocabulary floor, sentence rules, and an explicit never-simplify list                  |

### Business Plan (`ceh-business-plan`)

| Skill                      | Invoke                                     | When                                                                                                                                                |
| -------------------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Develop Business Plan      | `/ceh-business-plan:develop-business-plan` | Anything about a business plan: the single entry point, which finds the plan, works out the moment, and routes to the specialist below that owns it |
| Find Product-Market Fit    | Model-only, no slash command               | A product idea or an existing plan needs product-market fit: drafts from any plan, PRD, or pitch, or interviews, then loops until a PMF gate passes |
| Review Business Plan       | Model-only, no slash command               | A plan needs a verdict before time or money goes in: report-only score on seven lenses, one headline finding, and the skill to run next             |
| Sharpen Strategy           | Model-only, no slash command               | The plan cannot say why it wins or what it refuses: where to play, how to win, what to decline, checked against nine tests                          |
| Stress-Test Unit Economics | Model-only, no slash command               | The numbers must be believed before spending: per-unit model with arithmetic, cash low point, and the input that kills the business                 |
| Plan Go-to-Market          | Model-only, no slash command               | The plan must say how the first customers are won: the first ten by name, one channel, its arithmetic, a pass-or-fail test                          |
| Run Premortem              | Model-only, no slash command               | A hard-to-undo commitment is near: failure stories, each with a warning signal, a kill criterion set in advance, and a loss cap                     |
| Set Operating Plan         | Model-only, no slash command               | The plan is agreed and work must start: 90 days of at most three objectives, owned key results, weekly inputs, a stop-doing list                    |

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

### Workflow Runner (`ceh-workflow-runner`)

| Skill                | Invoke                                      | When                                                                                                                                     |
| -------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Run Agentic Workflow | `/ceh-workflow-runner:run-agentic-workflow` | Running a built workflow from its `flow.yaml`, interactive or headless: stages, approvals, gates, run state, resume, a final status line |

### Competitor Analysis (`ceh-competitor-analysis`)

| Skill               | Invoke                                         | When                                                                                                                                         |
| ------------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Analyze Competitor  | `/ceh-competitor-analysis:analyze-competitor`  | Analysing a competitor repo or product: breakdown, full inventory, "oh wow" mechanisms with evidence, what to incorporate and where it lands |
| Compare Competitors | `/ceh-competitor-analysis:compare-competitors` | Putting the analysed competitors side by side with your own work: at-a-glance table, inventory by capability, strengths and weaknesses       |

---

## Agents

Agents run autonomously for a defined task and hand results back to the parent session.

> **Plugin-agent limitation:** every agent here ships inside a plugin. Claude Code **ignores** the
> `permissionMode`, `hooks`, `mcpServers`, and `initialPrompt` frontmatter fields on plugin
> subagents (for security reasons), so no agent in this repo sets them. These agents inherit the
> permission context of your session and prompt for edit/write permissions accordingly. To avoid
> the prompts, put the session in `acceptEdits` (`Shift+Tab`) before dispatching, or add
> `permissions.allow` rules in `settings.json`. See the
> [subagents docs](https://code.claude.com/docs/en/sub-agents#choose-the-subagent-scope).
>
> **Background tool filter:** subagents run in the background by default, and a background
> subagent keeps only `Read`, `Grep`, `Glob`, `LSP`, `Bash`, `PowerShell`, `Edit`, `Write`,
> `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, `EnterWorktree`,
> `ExitWorktree`, `Monitor`, `TaskStop`, `SendMessage`, and `Artifact`. Anything else is stripped
> silently, even when named in `tools:`. `AskUserQuestion` is removed from every subagent, so no
> agent here can stop to ask you a question.

### Every Session (`ceh-every-session`)

| Agent       | Invoke                           | When                                                                                                                                                       |
| ----------- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bulk Reader | `/ceh-every-session:bulk-reader` | Read large or numerous files on Haiku and return a compressed, line-anchored answer to one question, keeping the file contents out of the caller's context |

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

| Agent              | Invoke                                              | When                                                                                                                                               |
| ------------------ | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Newcomer Simulator | `@"ceh-usability-audit:newcomer-simulator (agent)"` | Walk a target cold under one persona toward one goal and report where it stalled, without using what it knows about such tools (Sonnet, read-only) |

### Competitor Analysis (`ceh-competitor-analysis`)

| Agent              | Invoke                                                  | When                                                                                                                   |
| ------------------ | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Competitor Analyst | `@"ceh-competitor-analysis:competitor-analyst (agent)"` | Read one competitor repo or product in isolation and return an evidence-anchored fact sheet (read-only, never runs it) |

---

## Installing in Claude Code

### Prerequisites

`python3` on `PATH` (stdlib only, no packages) for the hooks in `ceh-every-session` and `ceh-git-workflow`,
and `bash` for the hooks in `ceh-coding-conduct`. No other plugin ships a hook. The Python hooks fail
open: without `python3` the usage-limit guard, the bulk-read guards, and the branch guard do
nothing instead of blocking you. Install with `winget install Python.Python.3.12` /
`brew install python` / `apt install python3`.

Individual **skills** have their own prerequisites, stated in each `SKILL.md`'s `compatibility`
frontmatter and surfaced when the skill loads: the git and GitHub CLIs for `ceh-git-workflow`,
Python 3.12 with `uv` for the two Python plugins, Bun or Node for `ceh-web-frontend`. Installing a
plugin never installs these. A skill whose prerequisite is missing says so instead of guessing.
Skills that only read files and write Markdown (planning, blog, review) declare nothing and need
nothing.

Environment variables the plugins read are indexed in
[`docs/ENVIRONMENT_VARIABLES.md`](docs/ENVIRONMENT_VARIABLES.md).

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
/plugin install ceh-every-session@ceh-claude-code-library --scope user
/plugin install ceh-coding-conduct@ceh-claude-code-library --scope user
/plugin install ceh-codebase-explanation@ceh-claude-code-library --scope user
/plugin install ceh-git-workflow@ceh-claude-code-library --scope user
/plugin install ceh-testing@ceh-claude-code-library --scope user
/plugin install ceh-python-service@ceh-claude-code-library --scope user
/plugin install ceh-python-library@ceh-claude-code-library --scope user
/plugin install ceh-web-frontend@ceh-claude-code-library --scope user
/plugin install ceh-ui-design@ceh-claude-code-library --scope user
/plugin install ceh-seo@ceh-claude-code-library --scope user
/plugin install ceh-blog@ceh-claude-code-library --scope user
/plugin install ceh-plan-build-review@ceh-claude-code-library --scope user
/plugin install ceh-documentation@ceh-claude-code-library --scope user
/plugin install ceh-ag-ui@ceh-claude-code-library --scope user
/plugin install ceh-usability-audit@ceh-claude-code-library --scope user
/plugin install ceh-business-plan@ceh-claude-code-library --scope user
/plugin install ceh-git-datastore@ceh-claude-code-library --scope user
/plugin install ceh-workflow-builder@ceh-claude-code-library --scope user
/plugin install ceh-workflow-runner@ceh-claude-code-library --scope user
/plugin install ceh-competitor-analysis@ceh-claude-code-library --scope user
```

Dependencies install automatically: each stack plugin brings `ceh-testing`, and `ceh-web-frontend`,
`ceh-ag-ui` and `ceh-competitor-analysis` bring `ceh-ui-design`. `ceh-workflow-builder` and `ceh-workflow-runner` are in no bundle, so install
them on their own: the builder where you author a flow, the runner wherever a flow runs.
`ceh-competitor-analysis` is in no bundle either: install it when you need it. Add `--scope project` instead of `--scope user` for a project-specific install.

### Step 3 — Verify

```
/help
```

The `ceh-*:` skills should appear in the skills list.

### Manual installation (alternative)

```bash
git clone https://github.com/cheneeheng/ceh-claude-code-library.git ~/ceh-claude-code-library
```

Then add plugin paths to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "plugins": [
    {
      "path": "~/ceh-claude-code-library/plugins/scenarios/ceh-scenario-service"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/scenarios/ceh-scenario-library"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/scenarios/ceh-scenario-webapp"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/scenarios/ceh-scenario-ideation"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/scenarios/ceh-scenario-editorial"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/standalone/ceh-every-session"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/standalone/ceh-coding-conduct"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/standalone/ceh-codebase-explanation"
    },
    { "path": "~/ceh-claude-code-library/plugins/standalone/ceh-git-workflow" },
    { "path": "~/ceh-claude-code-library/plugins/standalone/ceh-testing" },
    {
      "path": "~/ceh-claude-code-library/plugins/standalone/ceh-python-service"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/standalone/ceh-python-library"
    },
    { "path": "~/ceh-claude-code-library/plugins/standalone/ceh-web-frontend" },
    { "path": "~/ceh-claude-code-library/plugins/standalone/ceh-ui-design" },
    { "path": "~/ceh-claude-code-library/plugins/standalone/ceh-seo" },
    { "path": "~/ceh-claude-code-library/plugins/standalone/ceh-blog" },
    {
      "path": "~/ceh-claude-code-library/plugins/standalone/ceh-plan-build-review"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/standalone/ceh-documentation"
    },
    { "path": "~/ceh-claude-code-library/plugins/standalone/ceh-ag-ui" },
    {
      "path": "~/ceh-claude-code-library/plugins/standalone/ceh-usability-audit"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/standalone/ceh-business-plan"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/standalone/ceh-git-datastore"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/standalone/ceh-workflow-builder"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/standalone/ceh-workflow-runner"
    },
    {
      "path": "~/ceh-claude-code-library/plugins/standalone/ceh-competitor-analysis"
    }
  ]
}
```

---

## Tools

| Tool             | Path                      | Purpose                                                                                                                                                                                                  |
| ---------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| skills-sync      | `tools/skills-sync/`      | Copy individual skills (from this repo or any other) into a project's `.claude/skills/` directory: install, update, add, remove, list. Python, bash, PowerShell, and browser-based HTML implementations. |
| validate-plugins | `tools/validate-plugins/` | Repo-integrity checker run by CI (`.github/workflows/validate.yml`): plugin manifests, skill/agent frontmatter, file and skill references, dependencies, and script syntax. Stdlib-only Python.          |

### Formatting

`.pre-commit-config.yaml` formats staged files on commit: ruff for Python, prettier (official npm
package) for Markdown and JSON, shfmt for shell scripts. Enable it once per clone:

```bash
pre-commit install
```
