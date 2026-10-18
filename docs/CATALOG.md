# Catalog

Every skill and agent the `ceh-*` plugins ship, grouped by plugin. What each plugin is for is in
the [Plugins](../README.md#plugins) table of the root `README.md`, and each plugin's own README has
its prerequisites, hooks, and environment variables.

## Skills

### [Every Session (`ceh-every-session`)](../plugins/standalone/ceh-every-session/)

| Skill                                                                                                        | Invoke                                                                       | When                                                                                                                                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Hand Off Session](../plugins/standalone/ceh-every-session/skills/hand-off-session/SKILL.md)                 | `/ceh-every-session:hand-off-session [save \| load [path]]`                  | Save the session's working state to a handoff file, or load one in a new session and resume from its first open step                                                                                                                                       |
| [Usage Limit Handoff](../plugins/standalone/ceh-every-session/skills/usage-limit-handoff/SKILL.md)           | Model-only, no slash command                                                 | Auto via PostToolUse guard hook when 5h or weekly usage crosses the threshold (default 90%) — stop cleanly, save a handoff via `hand-off-session`, end the turn                                                                                            |
| [Delegate Bulk Reads](../plugins/standalone/ceh-every-session/skills/delegate-bulk-reads/SKILL.md)           | Model-only, no slash command                                                 | Before dispatching the `bulk-reader` agent, and before acting on its summary — the delegation prompt and the verification rules                                                                                                                            |
| [Write Questionnaire](../plugins/standalone/ceh-every-session/skills/write-questionnaire/SKILL.md)           | `/ceh-every-session:write-questionnaire [write \| read [path]]`              | Turn open questions into a self-contained file someone outside the session answers later, then read the answers back and continue                                                                                                                          |
| [Write Research Note](../plugins/standalone/ceh-every-session/skills/write-research-note/SKILL.md)           | `/ceh-every-session:write-research-note <question>`                          | Answer a question from outside sources: a background agent writes one note with every claim cited, then the session spot-checks the citations                                                                                                              |
| [Stress-Test Plan](../plugins/standalone/ceh-every-session/skills/stress-test-plan/SKILL.md)                 | `/ceh-every-session:stress-test-plan [plan-file]`                            | Question a plan, design, strategy, or roadmap in rounds, each question with a recommended answer, facts fetched by a subagent, outcome written back into the plan                                                                                          |
| [Prevent Repeat Mistake](../plugins/standalone/ceh-every-session/skills/prevent-repeat-mistake/SKILL.md)     | `/ceh-every-session:prevent-repeat-mistake [the mistake]`                    | A mistake must not happen again, repeated or found by a retro: pick the strongest fix that would have caught it, prove it fails on the real mistake, draft anything that changes later sessions for approval, saved for a later session. Any kind of files |
| [Find Available Guide](../plugins/standalone/ceh-every-session/skills/find-available-guide/SKILL.md)         | Model-only, no slash command                                                 | The work first names a framework, library, or service: look it up in a registry of installable skills, plugins, and MCP servers, and after the task note what to install and how. Installs nothing                                                         |
| [Record Project Decisions](../plugins/standalone/ceh-every-session/skills/record-project-decisions/SKILL.md) | `/ceh-every-session:record-project-decisions [record <decision> \| seed]`    | Write each decision that binds the project as its own short rule file, `.claude/rules/decision-<topic>.md`, loaded in every session, so code, planning, and writing tasks all follow it                                                                    |
| [What's Next](../plugins/standalone/ceh-every-session/skills/whats-next/SKILL.md)                            | `/ceh-every-session:whats-next [what you want to do]`, or ask "what's next?" | Suggest the installed skills or agents that fit the request and the repo state, each with why now and how to start it, or a `ceh-` plugin to install when nothing installed fits. Runs none of them                                                        |

### [Coding Conduct (`ceh-coding-conduct`)](../plugins/standalone/ceh-coding-conduct/)

| Skill                                                                                                   | Invoke                                | When                                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------- | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Agent Coding Contract](../plugins/standalone/ceh-coding-conduct/skills/agent-coding-contract/SKILL.md) | Model-only, no slash command          | Start of any coding session (auto via SessionStart hook) — core rules, five-step workflow, stop conditions, non-goals                                                                         |
| [Write Less Code](../plugins/standalone/ceh-coding-conduct/skills/write-less-code/SKILL.md)             | Model-only, no slash command          | Every coding session (auto — per-turn digest via hook) — the minimalism ladder (YAGNI → stdlib → native → installed dep → one line)                                                           |
| [Shrink Diff](../plugins/standalone/ceh-coding-conduct/skills/shrink-diff/SKILL.md)                     | `/ceh-coding-conduct:shrink-diff`     | Branch functionally done, before the PR — retroactively apply write-less-code to the accumulated diff vs `main`                                                                               |
| [Refactor Repo](../plugins/standalone/ceh-coding-conduct/skills/refactor-repo/SKILL.md)                 | `/ceh-coding-conduct:refactor-repo`   | Manual only — propose-then-apply refactor campaign over the whole repo or a named module                                                                                                      |
| [Find Root Cause](../plugins/standalone/ceh-coding-conduct/skills/find-root-cause/SKILL.md)             | `/ceh-coding-conduct:find-root-cause` | Something is broken and no command has yet shown why, before any fix: reproduce, falsifiable hypotheses, evidence, a cause confirmed by prediction, saved as a fix record in `product/fixes/` |
| [Sketch Design](../plugins/standalone/ceh-coding-conduct/skills/sketch-design/SKILL.md)                 | `/ceh-coding-conduct:sketch-design`   | Before the code for a feature that adds a type, module, or called function: types, signatures, boundaries, then four checks on the sketch                                                     |

### [Codebase Explanation (`ceh-codebase-explanation`)](../plugins/standalone/ceh-codebase-explanation/)

| Skill                                                                                                               | Invoke                                                   | When                                                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Explain Until Understood](../plugins/standalone/ceh-codebase-explanation/skills/explain-until-understood/SKILL.md) | `/ceh-codebase-explanation:explain-until-understood`     | Explaining a subsystem, design, or diff to the person in the session: stated floor, foundations first, verified claims, ASCII pictures, one walked case, and the escalation ladder when an explanation misses |
| [Explain Codebase](../plugins/standalone/ceh-codebase-explanation/skills/explain-codebase/SKILL.md)                 | `/ceh-codebase-explanation:explain-codebase`             | Go through a whole repo, code or knowledge base, and write what each component does, how they connect, and key flows into the ignored `.agents_workspace/CODEBASE_EXPLAINED.md`                               |
| [Document Architecture](../plugins/standalone/ceh-codebase-explanation/skills/document-architecture/SKILL.md)       | `/ceh-codebase-explanation:document-architecture`        | Writing or updating the living, committed `product/ARCHITECTURE.md`: 3-second Overview, Mermaid diagrams, Key Decisions log; also when a re-plan changes system shape                                         |
| [Trace Code Rationale](../plugins/standalone/ceh-codebase-explanation/skills/trace-code-rationale/SKILL.md)         | `/ceh-codebase-explanation:trace-code-rationale`         | "Why is it like this", or before removing code that looks pointless: trace it through git log, blame, PRs, and issues, and answer with every claim cited and the unrecorded parts named                       |
| [Maintain Glossary](../plugins/standalone/ceh-codebase-explanation/skills/maintain-glossary/SKILL.md)               | `/ceh-codebase-explanation:maintain-glossary [term ...]` | A term is used two ways or two words name one thing: settle one word and definition in a committed `GLOSSARY.md`, list files still using a rejected alias                                                     |

### [Git Workflow (`ceh-git-workflow`)](../plugins/standalone/ceh-git-workflow/)

| Skill                                                                                                     | Invoke                                                 | Auto-loads when                                                                                                                                                                    |
| --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Branch](../plugins/standalone/ceh-git-workflow/skills/branch/SKILL.md)                                   | Model-only, no slash command                           | Creating or naming a branch; a PreToolUse hook denies file edits on the default branch until one exists                                                                            |
| [Commit](../plugins/standalone/ceh-git-workflow/skills/commit/SKILL.md)                                   | `/ceh-git-workflow:commit`                             | Writing a commit message or staging changes                                                                                                                                        |
| [Pull Request](../plugins/standalone/ceh-git-workflow/skills/pull-request/SKILL.md)                       | `/ceh-git-workflow:pull-request`                       | A branch is heading into `main`: open a PR, merge it (or a local branch), or land the branch in one pass — changelog under `[Unreleased]` → commit → PR → merge → cleanup          |
| [Release](../plugins/standalone/ceh-git-workflow/skills/release/SKILL.md)                                 | `/ceh-git-workflow:release`                            | Ship a version: bump → changelog → PR → merge → tag → GitHub release; also tag-only and the hotfix variant                                                                         |
| [Code Review](../plugins/standalone/ceh-git-workflow/skills/code-review/SKILL.md)                         | `/ceh-git-workflow:code-review`                        | Reviewing a PR or leaving review comments, with the spec checked on its own axis, an opt-in panel of reviewers on different models, and an opt-in two-reviewer gate                |
| [Address Review Comments](../plugins/standalone/ceh-git-workflow/skills/address-review-comments/SKILL.md) | `/ceh-git-workflow:address-review-comments`            | Acting on review feedback on your own change: verify each comment against the code, fix what holds, push back with evidence, reply to every thread                                 |
| [Update Changelog](../plugins/standalone/ceh-git-workflow/skills/update-changelog/SKILL.md)               | `/ceh-git-workflow:update-changelog`                   | Generate or update CHANGELOG.md, write release notes, or log a change under `[Unreleased]`                                                                                         |
| [Update README](../plugins/standalone/ceh-git-workflow/skills/update-readme/SKILL.md)                     | `/ceh-git-workflow:update-readme`                      | Refresh `README.md` after a significant change (new feature, changed install steps, new API surface); does nothing when nothing material changed                                   |
| [Review Recent Work](../plugins/standalone/ceh-git-workflow/skills/review-recent-work/SKILL.md)           | `/ceh-git-workflow:review-recent-work [since] [until]` | Look back over a period from git history: what shipped, time to merge, reverts, churn hotspots, at most three issues each routed to the skill that fixes it, no per-person ranking |

### [Testing (`ceh-testing`)](../plugins/standalone/ceh-testing/)

| Skill                                                                                                    | Invoke                                   | When                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [Test a Bug Fix](../plugins/standalone/ceh-testing/skills/test-a-bug-fix/SKILL.md)                       | `/ceh-testing:test-a-bug-fix`            | A bug, crash, or regression is being fixed: failing test first, prove it goes red without the fix, bisect on it, commit the fix record with the fix          |
| [Design Test Cases](../plugins/standalone/ceh-testing/skills/design-test-cases/SKILL.md)                 | Model-only, no slash command             | Deciding which inputs and scenarios to cover: partitions, boundaries, decision tables, state transitions, properties, fuzzing                                |
| [Audit Test Suite](../plugins/standalone/ceh-testing/skills/audit-test-suite/SKILL.md)                   | `/ceh-testing:audit-test-suite`          | Finding out whether a passing suite would catch a defect: assertion quality, mutation testing on the diff, flakiness                                         |
| [Verify Behavior Preserved](../plugins/standalone/ceh-testing/skills/verify-behavior-preserved/SKILL.md) | `/ceh-testing:verify-behavior-preserved` | Before a refactor, extraction, dependency or runtime upgrade, or port: characterization tests, golden files, a differential run                              |
| [Close Test Risk Gaps](../plugins/standalone/ceh-testing/skills/close-test-risk-gaps/SKILL.md)           | `/ceh-testing:close-test-risk-gaps`      | Pre-completion gate: concurrency, contract drift, performance, authorization, and migration/rollout gaps                                                     |
| [Write Test First](../plugins/standalone/ceh-testing/skills/write-test-first/SKILL.md)                   | `/ceh-testing:write-test-first`          | About to write code that adds or changes behavior: red, green, refactor per slice, by default and not only when asked                                        |
| [Measure Performance](../plugins/standalone/ceh-testing/skills/measure-performance/SKILL.md)             | `/ceh-testing:measure-performance`       | Speed, memory, or size is the task: vet the measurement against its noise, baseline, profile, one change per measurement and one commit per win              |
| [Explore App for Bugs](../plugins/standalone/ceh-testing/skills/explore-app-for-bugs/SKILL.md)           | `/ceh-testing:explore-app-for-bugs`      | Try the running app for bugs: written charters over the changed areas, each bug reproduced twice, report-only by default and fix mode on request             |
| [Write Evidence Report](../plugins/standalone/ceh-testing/skills/write-evidence-report/SKILL.md)         | `/ceh-testing:write-evidence-report`     | Before a launch or a post about the product: roll the latest test, QA, performance, security, and usability results into one committed `product/EVIDENCE.md` |

### [Python Service (`ceh-python-service`)](../plugins/standalone/ceh-python-service/)

| Skill                                                                                                                 | Invoke                       | When                                                                                                                                                              |
| --------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Write FastAPI Endpoints](../plugins/standalone/ceh-python-service/skills/write-fastapi-endpoints/SKILL.md)           | Model-only, no slash command | Route handlers, dependencies, lifespan, exception handlers, layer boundaries, logging, metrics, `/health`, correlation IDs, CORS, rate limiting, input validation |
| [Write PostgreSQL Code](../plugins/standalone/ceh-python-service/skills/write-postgresql-code/SKILL.md)               | Model-only, no slash command | Schema design, entity IDs, status enums, asyncpg queries, transactions, tenant isolation, pool config, Alembic migrations                                         |
| [Configure Python Service Env](../plugins/standalone/ceh-python-service/skills/configure-python-service-env/SKILL.md) | Model-only, no slash command | Editing `pyproject.toml`, uv commands, type hints, ruff/mypy config, secrets and `.env` files                                                                     |
| [Write pytest Service Tests](../plugins/standalone/ceh-python-service/skills/write-pytest-service-tests/SKILL.md)     | Model-only, no slash command | Creating or modifying test files, fixtures, or mocks                                                                                                              |

### [Python Library (`ceh-python-library`)](../plugins/standalone/ceh-python-library/)

| Skill                                                                                                                 | Invoke                                       | When                                                                                            |
| --------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| [Configure Python Library Env](../plugins/standalone/ceh-python-library/skills/configure-python-library-env/SKILL.md) | Model-only, no slash command                 | Editing `pyproject.toml`, uv commands, type hints, ruff/mypy config                             |
| [Write pytest Library Tests](../plugins/standalone/ceh-python-library/skills/write-pytest-library-tests/SKILL.md)     | Model-only, no slash command                 | Creating or modifying test files, fixtures, or mocks                                            |
| [Publish Python Library](../plugins/standalone/ceh-python-library/skills/publish-python-library/SKILL.md)             | `/ceh-python-library:publish-python-library` | Build backend, src layout, PyPI publishing, `__init__.py`/`__all__`, deprecations, semver bumps |

### [Web Frontend (`ceh-web-frontend`)](../plugins/standalone/ceh-web-frontend/)

| Skill                                                                                                                   | Invoke                                        | When                                                                                                                         |
| ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| [Configure Bun + Vite Env](../plugins/standalone/ceh-web-frontend/skills/configure-bun-vite-env/SKILL.md)               | Model-only, no slash command                  | Bun/Vite setup, scripts, deps, TypeScript style, ESLint/Prettier                                                             |
| [Write SvelteKit Code](../plugins/standalone/ceh-web-frontend/skills/write-sveltekit-code/SKILL.md)                     | Model-only, no slash command                  | Editing Svelte routes, shared `.svelte.ts` state, components, or the API client                                              |
| [Write React + Vite Code](../plugins/standalone/ceh-web-frontend/skills/write-react-vite-code/SKILL.md)                 | Model-only, no slash command                  | Editing React components, hooks, routing, or `vite.config.ts`                                                                |
| [Write Vitest + Playwright Tests](../plugins/standalone/ceh-web-frontend/skills/write-vitest-playwright-tests/SKILL.md) | Model-only, no slash command                  | Writing `.test.ts`, `.test.tsx`, or `.spec.ts` files, or MSW handlers                                                        |
| [Make UI Accessible](../plugins/standalone/ceh-web-frontend/skills/make-ui-accessible/SKILL.md)                         | Model-only, no slash command                  | Writing component markup (Svelte or React)                                                                                   |
| [Visualize Graph (Cytoscape)](../plugins/standalone/ceh-web-frontend/skills/visualize-graph-cytoscape/SKILL.md)         | `/ceh-web-frontend:visualize-graph-cytoscape` | A network, dependency map, org chart, or any clickable node-link diagram with Cytoscape.js                                   |
| [Check Visual Parity](../plugins/standalone/ceh-web-frontend/skills/check-visual-parity/SKILL.md)                       | `/ceh-web-frontend:check-visual-parity`       | A migration or restyle must not change the look: Playwright screenshots of the old version as baseline, every diff explained |

### [UI Design (`ceh-ui-design`)](../plugins/standalone/ceh-ui-design/)

| Skill                                                                      | Invoke                     | When                                                                                                                                                                          |
| -------------------------------------------------------------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Design UI](../plugins/standalone/ceh-ui-design/skills/design-ui/SKILL.md) | `/ceh-ui-design:design-ui` | Any visual design decision for a UI or HTML page: layout, hierarchy, navigation, in-page contents, states, finishing recipes, a variants board, Meridian and Tidewater themes |

### [SEO (`ceh-seo`)](../plugins/standalone/ceh-seo/)

| Skill                                                                                                  | Invoke                                | When                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------ | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| [Make Page Crawlable](../plugins/standalone/ceh-seo/skills/make-page-crawlable/SKILL.md)               | `/ceh-seo:make-page-crawlable`        | Shipping or creating a public web page: per-page head checklist, sitemap and robots, JSON-LD, content in the initial HTML, GEO citation rules |
| [Write llms.txt](../plugins/standalone/ceh-seo/skills/write-llms-txt/SKILL.md)                         | `/ceh-seo:write-llms-txt`             | Creating or updating the `llms.txt` reading list for AI agents: positional format, link curation, `## Optional`, markdown over HTML           |
| [Write Project Listing Text](../plugins/standalone/ceh-seo/skills/write-project-listing-text/SKILL.md) | `/ceh-seo:write-project-listing-text` | Writing the README first screen, package description and keywords, GitHub topics, marketplace listings, or landing copy                       |

### [Blog (`ceh-blog`)](../plugins/standalone/ceh-blog/)

| Skill                                                                           | Invoke                     | When                                                                                                                        |
| ------------------------------------------------------------------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| [Draft Post](../plugins/standalone/ceh-blog/skills/draft-post/SKILL.md)         | `/ceh-blog:draft-post`     | A new post from a topic, idea, repo, or experience (interview first) or from notes, bullets, or an outline (draft directly) |
| [Edit Post](../plugins/standalone/ceh-blog/skills/edit-post/SKILL.md)           | `/ceh-blog:edit-post`      | An existing draft: diagnosis first, then a full revision that keeps the author's voice                                      |
| [Repurpose Post](../plugins/standalone/ceh-blog/skills/repurpose-post/SKILL.md) | `/ceh-blog:repurpose-post` | A finished post to adapt into a Twitter/X thread, LinkedIn post, TL;DR, or newsletter blurb                                 |

### [Build Planning (`ceh-build-planning`)](../plugins/standalone/ceh-build-planning/)

| Skill                                                                                           | Invoke                                  | When                                                                                                                           |
| ----------------------------------------------------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| [Write Build Plan](../plugins/standalone/ceh-build-planning/skills/write-build-plan/SKILL.md)   | `/ceh-build-planning:write-build-plan`  | Before building an app or a feature: triage, In and Out scope, the design decisions the build needs, phases with checks        |
| [Review Build Plan](../plugins/standalone/ceh-build-planning/skills/review-build-plan/SKILL.md) | `/ceh-build-planning:review-build-plan` | A plan or spec is written and nobody has built from it: scope, engineering, design, and developer-experience lenses, a verdict |

### [Build From Plan (`ceh-build-from-plan`)](../plugins/standalone/ceh-build-from-plan/)

| Skill                                                                                                | Invoke                                     | When                                                                                                          |
| ---------------------------------------------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| [Implement From Plan](../plugins/standalone/ceh-build-from-plan/skills/implement-from-plan/SKILL.md) | `/ceh-build-from-plan:implement-from-plan` | Building a plan phase by phase: test first, only what the phase names, its check run and recorded as evidence |

### [Check Build Against Plan (`ceh-check-build-against-plan`)](../plugins/standalone/ceh-check-build-against-plan/)

| Skill                                                                                                                   | Invoke                                                   | When                                                                                                                                                   |
| ----------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [Check Build Against Plan](../plugins/standalone/ceh-check-build-against-plan/skills/check-build-against-plan/SKILL.md) | `/ceh-check-build-against-plan:check-build-against-plan` | Whether finished code is what the plan said to build: gaps, deviations, unplanned extras, phase checks rerun, and an opt-in two-reviewer gate on fixes |

### [Documentation (`ceh-documentation`)](../plugins/standalone/ceh-documentation/)

| Skill                                                                                                          | Invoke                                         | When                                                                                                                        |
| -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| [Write Project Docs](../plugins/standalone/ceh-documentation/skills/write-project-docs/SKILL.md)               | `/ceh-documentation:write-project-docs`        | A full docs set under `docs/` for the workspace or a given project path, one job per page; sequences the three skills below |
| [Write Guides and Runbooks](../plugins/standalone/ceh-documentation/skills/write-guides-and-runbooks/SKILL.md) | `/ceh-documentation:write-guides-and-runbooks` | User guides and operator runbooks: one section per audience, task-oriented verifiable procedures                            |
| [Write API Reference](../plugins/standalone/ceh-documentation/skills/write-api-reference/SKILL.md)             | `/ceh-documentation:write-api-reference`       | The exhaustive reference: every public item counted against the surface, with "Added in" markers                            |
| [Write Concept Docs](../plugins/standalone/ceh-documentation/skills/write-concept-docs/SKILL.md)               | `/ceh-documentation:write-concept-docs`        | Concept pages: the mental model and the design rationale, each traced to a source, never invented                           |
| [Write Examples](../plugins/standalone/ceh-documentation/skills/write-examples/SKILL.md)                       | `/ceh-documentation:write-examples`            | New runnable programs under `examples/`: a numbered feature tour and copy-paste recipes, each run before it is kept         |

### [AG-UI (`ceh-ag-ui`)](../plugins/standalone/ceh-ag-ui/)

| Skill                                                                                        | Invoke                            | When                                                                                                                                                                       |
| -------------------------------------------------------------------------------------------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Build AG-UI](../plugins/standalone/ceh-ag-ui/skills/build-ag-ui/SKILL.md)                   | `/ceh-ag-ui:build-ag-ui`          | Starting a generative-UI canvas for an AG-UI agent: own template or the bundled one (React + Vite + `@ag-ui/client`, seven catalogue components, mock agent), styling lock |
| [Add Canvas Component](../plugins/standalone/ceh-ag-ui/skills/add-canvas-component/SKILL.md) | `/ceh-ag-ui:add-canvas-component` | Adding a component the agent can place: agent-facing description, content-only zod schema, example fixture, theme-only markup, mock verification                           |
| [Build AG-UI Agent](../plugins/standalone/ceh-ag-ui/skills/build-ag-ui-agent/SKILL.md)       | `/ceh-ag-ui:build-ag-ui-agent`    | Building the Claude-backed AG-UI server: append-only transcript per thread, end the run on a frontend tool call, held backend results, `RUN_ERROR` on every failure        |
| [Add Live State Panel](../plugins/standalone/ceh-ag-ui/skills/add-live-state-panel/SKILL.md) | `/ceh-ag-ui:add-live-state-panel` | A live value the agent keeps updating: `STATE_SNAPSHOT` / `STATE_DELTA`, one writer per key, a fixed validated panel                                                       |
| [Add Human Approval](../plugins/standalone/ceh-ag-ui/skills/add-human-approval/SKILL.md)     | `/ceh-ag-ui:add-human-approval`   | The agent must ask before acting: AG-UI interrupts, a fixed approval card, one resume for every open interrupt                                                             |

### [Usability Audit (`ceh-usability-audit`)](../plugins/standalone/ceh-usability-audit/)

| Skill                                                                                                                | Invoke                                             | When                                                                                                                                                           |
| -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Simulate Newcomer First Run](../plugins/standalone/ceh-usability-audit/skills/simulate-newcomer-first-run/SKILL.md) | `/ceh-usability-audit:simulate-newcomer-first-run` | Can a stranger reach first success: install, sign-up, setup, onboarding; cold persona walkers, milestones capped by an action budget, looped to a 5-point gate |
| [Audit Interface](../plugins/standalone/ceh-usability-audit/skills/audit-interface/SKILL.md)                         | `/ceh-usability-audit:audit-interface`             | They are already in: the five questions every web UI/CLI/API/screen must answer unasked, an anti-pattern sweep, the naming test, and the persona battery       |
| [Audit Error Messages](../plugins/standalone/ceh-usability-audit/skills/audit-error-messages/SKILL.md)               | Model-only, no slash command                       | Anything a user reads when something goes wrong: the three-part rule (what happened, what was wrong, what to do next) over every user-reachable string         |
| [Write Plain Language](../plugins/standalone/ceh-usability-audit/skills/write-plain-language/SKILL.md)               | Model-only, no slash command                       | Labels, help text, empty states, confirmation dialogs, onboarding copy: vocabulary floor, sentence rules, and an explicit never-simplify list                  |

### [Business Plan (`ceh-business-plan`)](../plugins/standalone/ceh-business-plan/)

| Skill                                                                                                            | Invoke                                     | When                                                                                                                                                |
| ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Develop Business Plan](../plugins/standalone/ceh-business-plan/skills/develop-business-plan/SKILL.md)           | `/ceh-business-plan:develop-business-plan` | Anything about a business plan: the single entry point, which finds the plan, works out the moment, and routes to the specialist below that owns it |
| [Find Product-Market Fit](../plugins/standalone/ceh-business-plan/skills/find-product-market-fit/SKILL.md)       | Model-only, no slash command               | A product idea or an existing plan needs product-market fit: drafts from any plan, PRD, or pitch, or interviews, then loops until a PMF gate passes |
| [Review Business Plan](../plugins/standalone/ceh-business-plan/skills/review-business-plan/SKILL.md)             | Model-only, no slash command               | A plan needs a verdict before time or money goes in: report-only score on seven lenses, one headline finding, and the skill to run next             |
| [Sharpen Strategy](../plugins/standalone/ceh-business-plan/skills/sharpen-strategy/SKILL.md)                     | Model-only, no slash command               | The plan cannot say why it wins or what it refuses: where to play, how to win, what to decline, checked against nine tests                          |
| [Stress-Test Unit Economics](../plugins/standalone/ceh-business-plan/skills/stress-test-unit-economics/SKILL.md) | Model-only, no slash command               | The numbers must be believed before spending: per-unit model with arithmetic, cash low point, and the input that kills the business                 |
| [Plan Go-to-Market](../plugins/standalone/ceh-business-plan/skills/plan-go-to-market/SKILL.md)                   | Model-only, no slash command               | The plan must say how the first customers are won: the first ten by name, one channel, its arithmetic, a pass-or-fail test                          |
| [Run Premortem](../plugins/standalone/ceh-business-plan/skills/run-premortem/SKILL.md)                           | Model-only, no slash command               | A hard-to-undo commitment is near: failure stories, each with a warning signal, a kill criterion set in advance, and a loss cap                     |
| [Set Operating Plan](../plugins/standalone/ceh-business-plan/skills/set-operating-plan/SKILL.md)                 | Model-only, no slash command               | The plan is agreed and work must start: 90 days of at most three objectives, owned key results, weekly inputs, a stop-doing list                    |
| [Write Investor Materials](../plugins/standalone/ceh-business-plan/skills/write-investor-materials/SKILL.md)     | Model-only, no slash command               | Money must be raised on a validated plan: a deck outline with every claim traced to a plan section, an ask tied to milestones, and outreach notes   |

### [Git Datastore (`ceh-git-datastore`)](../plugins/standalone/ceh-git-datastore/)

| Skill                                                                                                  | Invoke                                     | When                                                                                                                                                       |
| ------------------------------------------------------------------------------------------------------ | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Build Git Datastore](../plugins/standalone/ceh-git-datastore/skills/build-git-datastore/SKILL.md)     | `/ceh-git-datastore:build-git-datastore`   | An app needs persistence but not a database yet: a gate that often says no, then a plumbing-only store on a bare git repo                                  |
| [Migrate Git Datastore](../plugins/standalone/ceh-git-datastore/skills/migrate-git-datastore/SKILL.md) | `/ceh-git-datastore:migrate-git-datastore` | The store has to become a real database, or you need to know whether it is time: schema inference, pinned-snapshot export, backfill, verification, cutover |

### [Workflow Builder (`ceh-workflow-builder`)](../plugins/standalone/ceh-workflow-builder/)

| Skill                                                                                                         | Invoke                                          | When                                                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Build Agentic Workflow](../plugins/standalone/ceh-workflow-builder/skills/build-agentic-workflow/SKILL.md)   | `/ceh-workflow-builder:build-agentic-workflow`  | Product work that repeats in the same shape becomes a skill or gated workflow: the one-skill-vs-workflow gate, native-first stages, handoff schemas, a headless draft |
| [Interview Workflow Task](../plugins/standalone/ceh-workflow-builder/skills/interview-workflow-task/SKILL.md) | `/ceh-workflow-builder:interview-workflow-task` | The repeated task is not yet described: the repetition test, then nine questions answered into a workflow spec file, nothing built                                    |

### [Workflow Runner (`ceh-workflow-runner`)](../plugins/standalone/ceh-workflow-runner/)

| Skill                                                                                                  | Invoke                                      | When                                                                                                                                            |
| ------------------------------------------------------------------------------------------------------ | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [Run Agentic Workflow](../plugins/standalone/ceh-workflow-runner/skills/run-agentic-workflow/SKILL.md) | `/ceh-workflow-runner:run-agentic-workflow` | Running a built workflow from its `flow.yaml`, interactive or headless: native stages, approvals, gates, run state, resume, a final status line |

### [Session to Skill (`ceh-session-to-skill`)](../plugins/standalone/ceh-session-to-skill/)

| Skill                                                                                                         | Invoke                                          | When                                                                                                                                                                      |
| ------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Turn Session Into Skill](../plugins/standalone/ceh-session-to-skill/skills/turn-session-into-skill/SKILL.md) | `/ceh-session-to-skill:turn-session-into-skill` | A task was just done in this session and should be repeatable: one `SKILL.md` from the steps that worked, corrections as rules, per-run values as arguments, no interview |

### [Session Diagnosis (`ceh-session-diagnosis`)](../plugins/standalone/ceh-session-diagnosis/)

| Skill                                                                                            | Invoke                                    | When                                                                                                                                               |
| ------------------------------------------------------------------------------------------------ | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Diagnose Session](../plugins/standalone/ceh-session-diagnosis/skills/diagnose-session/SKILL.md) | `/ceh-session-diagnosis:diagnose-session` | A session went wrong: four analysts read its transcript in parallel, root causes cited to transcript lines, each routed to the skill that fixes it |

### [Security Audit (`ceh-security-audit`)](../plugins/standalone/ceh-security-audit/)

| Skill                                                                                                       | Invoke                                        | When                                                                                                                          |
| ----------------------------------------------------------------------------------------------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| [Audit Codebase Security](../plugins/standalone/ceh-security-audit/skills/audit-codebase-security/SKILL.md) | `/ceh-security-audit:audit-codebase-security` | The whole codebase needs a security audit: attack surface first, each entry point traced to its sinks, report-only by default |

### [Competitor Analysis (`ceh-competitor-analysis`)](../plugins/standalone/ceh-competitor-analysis/)

| Skill                                                                                                    | Invoke                                         | When                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| [Analyze Competitor](../plugins/standalone/ceh-competitor-analysis/skills/analyze-competitor/SKILL.md)   | `/ceh-competitor-analysis:analyze-competitor`  | Analysing a competitor repo or product: breakdown, full inventory, "oh wow" mechanisms with evidence, what to incorporate and where it lands |
| [Compare Competitors](../plugins/standalone/ceh-competitor-analysis/skills/compare-competitors/SKILL.md) | `/ceh-competitor-analysis:compare-competitors` | Putting the analysed competitors side by side with your own work: at-a-glance table, inventory by capability, strengths and weaknesses       |

### [Orchestration Lab (`ceh-orchestration-lab`)](../plugins/standalone/ceh-orchestration-lab/)

Experimental, and user-invoked only.

| Skill                                                                                                  | Invoke                                       | When                                                                                                                                                                                  |
| ------------------------------------------------------------------------------------------------------ | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Plan Then Implement](../plugins/standalone/ceh-orchestration-lab/skills/plan-then-implement/SKILL.md) | `/ceh-orchestration-lab:plan-then-implement` | Trying a task as one plan and one handoff: this session plans, one implementer on a cheaper model carries it out, the run is logged                                                   |
| [Orchestrate](../plugins/standalone/ceh-orchestration-lab/skills/orchestrate/SKILL.md)                 | `/ceh-orchestration-lab:orchestrate`         | Trying a task as a supervised loop: a scout maps the code, this session splits, briefs and reviews, implementers on a cheaper model do the pieces worth delegating, the run is logged |

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

### [Every Session (`ceh-every-session`)](../plugins/standalone/ceh-every-session/)

| Agent                                                                        | Invoke                           | When                                                                                                                                                       |
| ---------------------------------------------------------------------------- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Bulk Reader](../plugins/standalone/ceh-every-session/agents/bulk-reader.md) | `/ceh-every-session:bulk-reader` | Read large or numerous files on Haiku and return a compressed, line-anchored answer to one question, keeping the file contents out of the caller's context |

### [Python Service (`ceh-python-service`)](../plugins/standalone/ceh-python-service/)

| Agent                                                                                                     | Invoke                                                    | When                                                                                                  |
| --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| [Pytest Unit Tester](../plugins/standalone/ceh-python-service/agents/pytest-unit-tester.md)               | `@"ceh-python-service:pytest-unit-tester (agent)"`        | Isolated, mocked unit tests for a function, class, or module                                          |
| [Pytest Integration Tester](../plugins/standalone/ceh-python-service/agents/pytest-integration-tester.md) | `@"ceh-python-service:pytest-integration-tester (agent)"` | Tests for module boundaries and real-database interactions                                            |
| [Pytest System Tester](../plugins/standalone/ceh-python-service/agents/pytest-system-tester.md)           | `@"ceh-python-service:pytest-system-tester (agent)"`      | Full end-to-end scenarios against the real stack (explicit request only)                              |
| [Python Service Reviewer](../plugins/standalone/ceh-python-service/agents/python-service-reviewer.md)     | `@"ceh-python-service:python-service-reviewer (agent)"`   | Read-only review of the Python service files in a large diff, dispatched in parallel by `code-review` |

### [Web Frontend (`ceh-web-frontend`)](../plugins/standalone/ceh-web-frontend/)

| Agent                                                                                                   | Invoke                                                  | When                                                                                            |
| ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| [Vitest Unit Tester](../plugins/standalone/ceh-web-frontend/agents/vitest-unit-tester.md)               | `@"ceh-web-frontend:vitest-unit-tester (agent)"`        | Isolated unit tests for TypeScript functions or modules                                         |
| [Vitest Integration Tester](../plugins/standalone/ceh-web-frontend/agents/vitest-integration-tester.md) | `@"ceh-web-frontend:vitest-integration-tester (agent)"` | Components wired with real shared state and MSW network handlers                                |
| [Playwright System Tester](../plugins/standalone/ceh-web-frontend/agents/playwright-system-tester.md)   | `@"ceh-web-frontend:playwright-system-tester (agent)"`  | Playwright E2E or smoke tests against a running stack                                           |
| [Web Frontend Reviewer](../plugins/standalone/ceh-web-frontend/agents/web-frontend-reviewer.md)         | `@"ceh-web-frontend:web-frontend-reviewer (agent)"`     | Read-only review of the frontend files in a large diff, dispatched in parallel by `code-review` |

### [Usability Audit (`ceh-usability-audit`)](../plugins/standalone/ceh-usability-audit/)

| Agent                                                                                        | Invoke                                              | When                                                                                                                                               |
| -------------------------------------------------------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Newcomer Simulator](../plugins/standalone/ceh-usability-audit/agents/newcomer-simulator.md) | `@"ceh-usability-audit:newcomer-simulator (agent)"` | Walk a target cold under one persona toward one goal and report where it stalled, without using what it knows about such tools (Sonnet, read-only) |

### [Competitor Analysis (`ceh-competitor-analysis`)](../plugins/standalone/ceh-competitor-analysis/)

| Agent                                                                                            | Invoke                                                  | When                                                                                                                   |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| [Competitor Analyst](../plugins/standalone/ceh-competitor-analysis/agents/competitor-analyst.md) | `@"ceh-competitor-analysis:competitor-analyst (agent)"` | Read one competitor repo or product in isolation and return an evidence-anchored fact sheet (read-only, never runs it) |

### [Orchestration Lab (`ceh-orchestration-lab`)](../plugins/standalone/ceh-orchestration-lab/)

| Agent                                                                            | Invoke                                         | When                                                                                                             |
| -------------------------------------------------------------------------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| [Implementer](../plugins/standalone/ceh-orchestration-lab/agents/implementer.md) | `@"ceh-orchestration-lab:implementer (agent)"` | Carry out one brief and run its check, as the worker of both orchestration-lab skills, on the model the run sets |

### [Session Diagnosis (`ceh-session-diagnosis`)](../plugins/standalone/ceh-session-diagnosis/)

| Agent                                                                                          | Invoke                                                | When                                                                                                                                         |
| ---------------------------------------------------------------------------------------------- | ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| [Transcript Analyst](../plugins/standalone/ceh-session-diagnosis/agents/transcript-analyst.md) | `@"ceh-session-diagnosis:transcript-analyst (agent)"` | Read one session transcript through one lens and return findings that each cite a line, dispatched by `diagnose-session` (Sonnet, read-only) |
