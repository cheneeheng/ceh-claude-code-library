# Catalog

Every skill and agent the `ceh-*` plugins ship, grouped by plugin. What each plugin is for is in
the [Plugins](../README.md#plugins) table of the root `README.md`, and each plugin's own README has
its prerequisites, hooks, and environment variables.

## Skills

### Every Session (`ceh-every-session`)

| Skill                    | Invoke                                                                       | When                                                                                                                                                                                       |
| ------------------------ | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Hand Off Session         | `/ceh-every-session:hand-off-session [save \| load [path]]`                  | Save the session's working state to a handoff file, or load one in a new session and resume from its first open step                                                                       |
| Usage Limit Handoff      | Model-only, no slash command                                                 | Auto via PostToolUse guard hook when 5h or weekly usage crosses the threshold (default 90%) — stop cleanly, save a handoff via `hand-off-session`, end the turn                            |
| Delegate Bulk Reads      | Model-only, no slash command                                                 | Before dispatching the `bulk-reader` agent, and before acting on its summary — the delegation prompt and the verification rules                                                            |
| Write Questionnaire      | `/ceh-every-session:write-questionnaire [write \| read [path]]`              | Turn open questions into a self-contained file someone outside the session answers later, then read the answers back and continue                                                          |
| Write Research Note      | `/ceh-every-session:write-research-note <question>`                          | Answer a question from outside sources: a background agent writes one note with every claim cited, then the session spot-checks the citations                                              |
| Stress-Test Plan         | `/ceh-every-session:stress-test-plan [plan-file]`                            | Question a plan, design, strategy, or roadmap in rounds, each question with a recommended answer, facts fetched by a subagent, outcome written back into the plan                          |
| Prevent Repeat Mistake   | `/ceh-every-session:prevent-repeat-mistake [the mistake \| retro]`           | A mistake happened twice: pick the strongest fix that would have caught it, prove it fails on the real mistake, draft anything that changes later sessions for approval. Any kind of files |
| Record Project Decisions | `/ceh-every-session:record-project-decisions [record <decision> \| seed]`    | Write each decision that binds the project as its own short rule file, `.claude/rules/decision-<topic>.md`, loaded in every session, so code, planning, and writing tasks all follow it    |
| What's Next              | `/ceh-every-session:whats-next [what you want to do]`, or ask "what's next?" | Suggest the installed skills or agents that fit the request and the repo state, each with why now and how to start it. Runs none of them                                                   |

### Coding Conduct (`ceh-coding-conduct`)

| Skill                 | Invoke                                | When                                                                                                                                       |
| --------------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Agent Coding Contract | Model-only, no slash command          | Start of any coding session (auto via SessionStart hook) — core rules, five-step workflow, stop conditions, non-goals                      |
| Write Less Code       | Model-only, no slash command          | Every coding session (auto — per-turn digest via hook) — the minimalism ladder (YAGNI → stdlib → native → installed dep → one line)        |
| Shrink Diff           | `/ceh-coding-conduct:shrink-diff`     | Branch functionally done, before the PR — retroactively apply write-less-code to the accumulated diff vs `main`                            |
| Refactor Repo         | `/ceh-coding-conduct:refactor-repo`   | Manual only — propose-then-apply refactor campaign over the whole repo or a named module                                                   |
| Find Root Cause       | `/ceh-coding-conduct:find-root-cause` | Something is broken and the cause is unknown, before any fix: reproduce, falsifiable hypotheses, evidence, a cause confirmed by prediction |
| Sketch Design         | `/ceh-coding-conduct:sketch-design`   | Before the code for a feature that adds a type, module, or called function: types, signatures, boundaries, then four checks on the sketch  |

### Codebase Explanation (`ceh-codebase-explanation`)

| Skill                    | Invoke                                                   | When                                                                                                                                                                                                          |
| ------------------------ | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Explain Until Understood | `/ceh-codebase-explanation:explain-until-understood`     | Explaining a subsystem, design, or diff to the person in the session: stated floor, foundations first, verified claims, ASCII pictures, one walked case, and the escalation ladder when an explanation misses |
| Explain Codebase         | `/ceh-codebase-explanation:explain-codebase`             | Go through a whole repo, code or knowledge base, and write what each component does, how they connect, and key flows into the ignored `.agents_workspace/CODEBASE_EXPLAINED.md`                               |
| Document Architecture    | `/ceh-codebase-explanation:document-architecture`        | Writing or updating the living, committed `docs/ARCHITECTURE.md`: 3-second Overview, Mermaid diagrams, Key Decisions log; also when a re-plan changes system shape                                            |
| Trace Code Rationale     | `/ceh-codebase-explanation:trace-code-rationale`         | "Why is it like this", or before removing code that looks pointless: trace it through git log, blame, PRs, and issues, and answer with every claim cited and the unrecorded parts named                       |
| Maintain Glossary        | `/ceh-codebase-explanation:maintain-glossary [term ...]` | A term is used two ways or two words name one thing: settle one word and definition in a committed `GLOSSARY.md`, list files still using a rejected alias                                                     |

### Git Workflow (`ceh-git-workflow`)

| Skill                   | Invoke                                                      | Auto-loads when                                                                                                                                                           |
| ----------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Branch                  | Model-only, no slash command                                | Creating or naming a branch; a PreToolUse hook denies file edits on the default branch until one exists                                                                   |
| Commit                  | `/ceh-git-workflow:commit`                                  | Writing a commit message or staging changes                                                                                                                               |
| Pull Request            | `/ceh-git-workflow:pull-request`                            | A branch is heading into `main`: open a PR, merge it (or a local branch), or land the branch in one pass — changelog under `[Unreleased]` → commit → PR → merge → cleanup |
| Release                 | `/ceh-git-workflow:release`                                 | Ship a version: bump → changelog → PR → merge → tag → GitHub release; also tag-only and the hotfix variant                                                                |
| Code Review             | `/ceh-git-workflow:code-review`                             | Reviewing a PR or leaving review comments, with the spec checked on its own axis, an opt-in panel of reviewers on different models, and an opt-in two-reviewer gate       |
| Address Review Comments | `/ceh-git-workflow:address-review-comments`                 | Acting on review feedback on your own change: verify each comment against the code, fix what holds, push back with evidence, reply to every thread                        |
| Update Changelog        | `/ceh-git-workflow:update-changelog`                        | Generate or update CHANGELOG.md, write release notes, or log a change under `[Unreleased]`                                                                                |
| Update README           | `/ceh-git-workflow:update-readme`                           | Refresh `README.md` after a significant change (new feature, changed install steps, new API surface); does nothing when nothing material changed                          |
| Write Engineering Retro | `/ceh-git-workflow:write-engineering-retro [since] [until]` | Look back over a period from git history: what shipped, time to merge, reverts, churn hotspots, at most three changes, no per-person ranking                              |

### Testing (`ceh-testing`)

| Skill                     | Invoke                                   | When                                                                                                                                                      |
| ------------------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Test a Bug Fix            | `/ceh-testing:test-a-bug-fix`            | A bug, crash, or regression is being fixed: failing test first, prove it goes red without the fix, bisect on it                                           |
| Design Test Cases         | Model-only, no slash command             | Deciding which inputs and scenarios to cover: partitions, boundaries, decision tables, state transitions, properties, fuzzing                             |
| Audit Test Suite          | `/ceh-testing:audit-test-suite`          | Finding out whether a passing suite would catch a defect: assertion quality, mutation testing on the diff, flakiness                                      |
| Verify Behavior Preserved | `/ceh-testing:verify-behavior-preserved` | Before a refactor, extraction, dependency or runtime upgrade, or port: characterization tests, golden files, a differential run                           |
| Close Test Risk Gaps      | `/ceh-testing:close-test-risk-gaps`      | Pre-completion gate: concurrency, contract drift, performance, authorization, and migration/rollout gaps                                                  |
| Write Test First          | `/ceh-testing:write-test-first`          | About to write code that adds or changes behavior: red, green, refactor per slice, by default and not only when asked                                     |
| Measure Performance       | `/ceh-testing:measure-performance`       | Speed, memory, or size is the task: vet the measurement against its noise, baseline, profile, one change per measurement and one commit per win           |
| Explore App for Bugs      | `/ceh-testing:explore-app-for-bugs`      | Try the running app for bugs: written charters over the changed areas, each bug reproduced twice, report-only by default and fix mode on request          |
| Write Evidence Report     | `/ceh-testing:write-evidence-report`     | Before a launch or a post about the product: roll the latest test, QA, performance, security, and usability results into one committed `docs/EVIDENCE.md` |

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

| Skill                           | Invoke                                        | When                                                                                                                         |
| ------------------------------- | --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Configure Bun + Vite Env        | Model-only, no slash command                  | Bun/Vite setup, scripts, deps, TypeScript style, ESLint/Prettier                                                             |
| Write SvelteKit Code            | Model-only, no slash command                  | Editing Svelte routes, shared `.svelte.ts` state, components, or the API client                                              |
| Write React + Vite Code         | Model-only, no slash command                  | Editing React components, hooks, routing, or `vite.config.ts`                                                                |
| Write Vitest + Playwright Tests | Model-only, no slash command                  | Writing `.test.ts`, `.test.tsx`, or `.spec.ts` files, or MSW handlers                                                        |
| Make UI Accessible              | Model-only, no slash command                  | Writing component markup (Svelte or React)                                                                                   |
| Visualize Graph (Cytoscape)     | `/ceh-web-frontend:visualize-graph-cytoscape` | A network, dependency map, org chart, or any clickable node-link diagram with Cytoscape.js                                   |
| Check Visual Parity             | `/ceh-web-frontend:check-visual-parity`       | A migration or restyle must not change the look: Playwright screenshots of the old version as baseline, every diff explained |

### UI Design (`ceh-ui-design`)

| Skill     | Invoke                     | When                                                                                                                                                                          |
| --------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Design UI | `/ceh-ui-design:design-ui` | Any visual design decision for a UI or HTML page: layout, hierarchy, navigation, in-page contents, states, finishing recipes, a variants board, Meridian and Tidewater themes |

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

### Build Planning (`ceh-build-planning`)

| Skill             | Invoke                                  | When                                                                                                                           |
| ----------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Write Build Plan  | `/ceh-build-planning:write-build-plan`  | Before building an app or a feature: triage, In and Out scope, the design decisions the build needs, phases with checks        |
| Review Build Plan | `/ceh-build-planning:review-build-plan` | A plan or spec is written and nobody has built from it: scope, engineering, design, and developer-experience lenses, a verdict |

### Build From Plan (`ceh-build-from-plan`)

| Skill               | Invoke                                     | When                                                                                                          |
| ------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| Implement From Plan | `/ceh-build-from-plan:implement-from-plan` | Building a plan phase by phase: test first, only what the phase names, its check run and recorded as evidence |

### Check Build Against Plan (`ceh-check-build-against-plan`)

| Skill                    | Invoke                                                   | When                                                                                                                                                   |
| ------------------------ | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Check Build Against Plan | `/ceh-check-build-against-plan:check-build-against-plan` | Whether finished code is what the plan said to build: gaps, deviations, unplanned extras, phase checks rerun, and an opt-in two-reviewer gate on fixes |

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
| Audit Error Messages        | Model-only, no slash command                       | Anything a user reads when something goes wrong: the three-part rule (what happened, what was wrong, what to do next) over every user-reachable string         |
| Write Plain Language        | Model-only, no slash command                       | Labels, help text, empty states, confirmation dialogs, onboarding copy: vocabulary floor, sentence rules, and an explicit never-simplify list                  |

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
| Write Investor Materials   | Model-only, no slash command               | Money must be raised on a validated plan: a deck outline with every claim traced to a plan section, an ask tied to milestones, and outreach notes   |

### Git Datastore (`ceh-git-datastore`)

| Skill                 | Invoke                                     | When                                                                                                                                                       |
| --------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Build Git Datastore   | `/ceh-git-datastore:build-git-datastore`   | An app needs persistence but not a database yet: a gate that often says no, then a plumbing-only store on a bare git repo                                  |
| Migrate Git Datastore | `/ceh-git-datastore:migrate-git-datastore` | The store has to become a real database, or you need to know whether it is time: schema inference, pinned-snapshot export, backfill, verification, cutover |

### Workflow Builder (`ceh-workflow-builder`)

| Skill                   | Invoke                                          | When                                                                                                                                                                  |
| ----------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Build Agentic Workflow  | `/ceh-workflow-builder:build-agentic-workflow`  | Product work that repeats in the same shape becomes a skill or gated workflow: the one-skill-vs-workflow gate, native-first stages, handoff schemas, a headless draft |
| Interview Workflow Task | `/ceh-workflow-builder:interview-workflow-task` | The repeated task is not yet described: the repetition test, then nine questions answered into a workflow spec file, nothing built                                    |

### Workflow Runner (`ceh-workflow-runner`)

| Skill                | Invoke                                      | When                                                                                                                                            |
| -------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Run Agentic Workflow | `/ceh-workflow-runner:run-agentic-workflow` | Running a built workflow from its `flow.yaml`, interactive or headless: native stages, approvals, gates, run state, resume, a final status line |

### Session to Skill (`ceh-session-to-skill`)

| Skill                   | Invoke                                          | When                                                                                                                                                                      |
| ----------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Turn Session Into Skill | `/ceh-session-to-skill:turn-session-into-skill` | A task was just done in this session and should be repeatable: one `SKILL.md` from the steps that worked, corrections as rules, per-run values as arguments, no interview |

### Session Diagnosis (`ceh-session-diagnosis`)

| Skill            | Invoke                                    | When                                                                                                                           |
| ---------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Diagnose Session | `/ceh-session-diagnosis:diagnose-session` | A session went wrong: four analysts read its transcript in parallel, root causes cited to transcript lines and routed to fixes |

### Security Audit (`ceh-security-audit`)

| Skill                   | Invoke                                        | When                                                                                                                          |
| ----------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Audit Codebase Security | `/ceh-security-audit:audit-codebase-security` | The whole codebase needs a security audit: attack surface first, each entry point traced to its sinks, report-only by default |

### Competitor Analysis (`ceh-competitor-analysis`)

| Skill               | Invoke                                         | When                                                                                                                                         |
| ------------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Analyze Competitor  | `/ceh-competitor-analysis:analyze-competitor`  | Analysing a competitor repo or product: breakdown, full inventory, "oh wow" mechanisms with evidence, what to incorporate and where it lands |
| Compare Competitors | `/ceh-competitor-analysis:compare-competitors` | Putting the analysed competitors side by side with your own work: at-a-glance table, inventory by capability, strengths and weaknesses       |

### Orchestration Lab (`ceh-orchestration-lab`)

Experimental, and user-invoked only.

| Skill               | Invoke                                       | When                                                                                                                                           |
| ------------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Plan Then Implement | `/ceh-orchestration-lab:plan-then-implement` | Trying a task as one plan and one handoff: this session plans, one implementer on a cheaper model carries it out, the run is logged            |
| Orchestrate         | `/ceh-orchestration-lab:orchestrate`         | Trying a task as a supervised loop: this session briefs and reviews, implementers on a cheaper model do every edit and test, the run is logged |

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

| Agent                     | Invoke                                                    | When                                                                                                  |
| ------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Pytest Unit Tester        | `@"ceh-python-service:pytest-unit-tester (agent)"`        | Isolated, mocked unit tests for a function, class, or module                                          |
| Pytest Integration Tester | `@"ceh-python-service:pytest-integration-tester (agent)"` | Tests for module boundaries and real-database interactions                                            |
| Pytest System Tester      | `@"ceh-python-service:pytest-system-tester (agent)"`      | Full end-to-end scenarios against the real stack (explicit request only)                              |
| Python Service Reviewer   | `@"ceh-python-service:python-service-reviewer (agent)"`   | Read-only review of the Python service files in a large diff, dispatched in parallel by `code-review` |

### Web Frontend (`ceh-web-frontend`)

| Agent                     | Invoke                                                  | When                                                                                            |
| ------------------------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Vitest Unit Tester        | `@"ceh-web-frontend:vitest-unit-tester (agent)"`        | Isolated unit tests for TypeScript functions or modules                                         |
| Vitest Integration Tester | `@"ceh-web-frontend:vitest-integration-tester (agent)"` | Components wired with real shared state and MSW network handlers                                |
| Playwright System Tester  | `@"ceh-web-frontend:playwright-system-tester (agent)"`  | Playwright E2E or smoke tests against a running stack                                           |
| Web Frontend Reviewer     | `@"ceh-web-frontend:web-frontend-reviewer (agent)"`     | Read-only review of the frontend files in a large diff, dispatched in parallel by `code-review` |

### Usability Audit (`ceh-usability-audit`)

| Agent              | Invoke                                              | When                                                                                                                                               |
| ------------------ | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Newcomer Simulator | `@"ceh-usability-audit:newcomer-simulator (agent)"` | Walk a target cold under one persona toward one goal and report where it stalled, without using what it knows about such tools (Sonnet, read-only) |

### Competitor Analysis (`ceh-competitor-analysis`)

| Agent              | Invoke                                                  | When                                                                                                                   |
| ------------------ | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Competitor Analyst | `@"ceh-competitor-analysis:competitor-analyst (agent)"` | Read one competitor repo or product in isolation and return an evidence-anchored fact sheet (read-only, never runs it) |

### Orchestration Lab (`ceh-orchestration-lab`)

| Agent       | Invoke                                         | When                                                                                                             |
| ----------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Implementer | `@"ceh-orchestration-lab:implementer (agent)"` | Carry out one brief and run its check, as the worker of both orchestration-lab skills, on the model the run sets |

### Session Diagnosis (`ceh-session-diagnosis`)

| Agent              | Invoke                                                | When                                                                                                                                         |
| ------------------ | ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Transcript Analyst | `@"ceh-session-diagnosis:transcript-analyst (agent)"` | Read one session transcript through one lens and return findings that each cite a line, dispatched by `diagnose-session` (Sonnet, read-only) |
