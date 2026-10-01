# ceh-claude-code-library

**WORK IN PROGRESS**

2026.09.30 - Migrating from [agent-skills](https://github.com/cheneeheng/agent-skills) repo.

## Plugins

| Plugin                | Install as           | Contents                                                                                                                                                                                                                                                                                                                                 |
| --------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Core                  | `ceh-core`           | Standards that hold however Claude Code is used: usage-limit guard + handoff (`usage-limit-handoff`); context economy (`delegate-bulk-reads`, `bulk-reader`, opt-in read guards)                                                                                                                                                         |
| Agent Coding Contract | `ceh-coding-agent`   | Behavioral contract for coding agents (always-on via SessionStart hook); write-less-code minimalism (always-on via hooks); retroactive refactoring (`shrink-diff`, `refactor-repo`); explaining code until it lands; whole-repo orientation (`explain-codebase`); the `CEH Coding Agent` output style (always-on via `force-for-plugin`) |
| Git Workflow          | `ceh-git-workflow`   | Branching, commits, pull requests from open to merge, changelog entries, releases including hotfixes, code review; a hook that blocks file edits on the default branch                                                                                                                                                                   |
| Testing               | `ceh-testing`        | Stack-agnostic testing technique: reproduce-first bug fixes (`test-a-bug-fix`), test-case design, suite audit (`audit-test-suite`), behavior-preservation checks, and the risk gaps a green suite misses                                                                                                                                 |
| Python Service        | `ceh-python-service` | FastAPI, asyncpg, PostgreSQL schema, Alembic, uv/ruff/mypy, pytest, observability, security, and domain modeling for web services; unit, integration, and system tester agents                                                                                                                                                           |
| Python Library        | `ceh-python-library` | Packaging and publishing, public API surface and semver, uv/ruff/mypy, and pytest for distributable libraries with no web dependencies                                                                                                                                                                                                   |
| Web Frontend          | `ceh-web-frontend`   | SvelteKit and React on Bun + Vite: TypeScript style and tooling, Vitest/Playwright testing, accessibility, UI visual design and themes, Cytoscape.js graphs; unit, integration, and system tester agents                                                                                                                                 |
| SEO                   | `ceh-seo`            | Discoverability for anything exposed to the internet: crawlable public web pages (head tags, structured data, sitemap, rendering), the `llms.txt` agent index, and the findability of README, package, and landing text                                                                                                                  |
| Blog                  | `ceh-blog`           | Blog posts in a personal, series-first voice: draft from a topic, repo, or notes (interviewing when material is thin), edit an existing draft, repurpose a finished post for X, LinkedIn, TL;DR, and newsletters                                                                                                                         |

### Categorization

| Tier                  | Loaded            | Plugins                                                           |
| --------------------- | ----------------- | ----------------------------------------------------------------- |
| **Scenario bundle**   | one per situation | —                                                                 |
| **Cross-cutting**     | most sessions     | `ceh-core`, `ceh-coding-agent`, `ceh-git-workflow`, `ceh-testing` |
| **Use-case workflow** | per activity      | `ceh-seo`, `ceh-blog`                                             |
| **Stack / build**     | per project type  | `ceh-python-service`, `ceh-python-library`, `ceh-web-frontend`    |

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

### Testing (`ceh-testing`)

| Skill                     | Invoke                                   | When                                                                                                                            |
| ------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Test a Bug Fix            | `/ceh-testing:test-a-bug-fix`            | A bug, crash, or regression is being fixed: failing test first, prove it goes red without the fix, bisect on it                 |
| Design Test Cases         | `/ceh-testing:design-test-cases`         | Deciding which inputs and scenarios to cover: partitions, boundaries, decision tables, state transitions, properties, fuzzing   |
| Audit Test Suite          | `/ceh-testing:audit-test-suite`          | Finding out whether a passing suite would catch a defect: assertion quality, mutation testing on the diff, flakiness            |
| Verify Behavior Preserved | `/ceh-testing:verify-behavior-preserved` | Before a refactor, extraction, dependency or runtime upgrade, or port: characterization tests, golden files, a differential run |
| Close Test Risk Gaps      | `/ceh-testing:close-test-risk-gaps`      | Pre-completion gate: concurrency, contract drift, performance, authorization, and migration/rollout gaps                        |

### Python Service (`ceh-python-service`)

| Skill                        | Invoke                                             | When                                                                                                   |
| ---------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Write FastAPI Endpoints      | `/ceh-python-service:write-fastapi-endpoints`      | Route handlers, dependencies, lifespan, exception handlers, REST API design                            |
| Write PostgreSQL Code        | `/ceh-python-service:write-postgresql-code`        | Schema design, asyncpg queries, transactions, tenant isolation, pool config, Alembic migrations        |
| Configure Python Service Env | `/ceh-python-service:configure-python-service-env` | Editing `pyproject.toml`, uv commands, type hints, ruff/mypy config                                    |
| Write pytest Service Tests   | `/ceh-python-service:write-pytest-service-tests`   | Creating or modifying test files, fixtures, or mocks                                                   |
| Add Observability            | `/ceh-python-service:add-observability`            | structlog logging, metrics, health checks, correlation IDs                                             |
| Secure Service Code          | `/ceh-python-service:secure-service-code`          | Secrets management, CORS, rate limiting, input validation                                              |
| Model Domain                 | `/ceh-python-service:model-domain`                 | Defining entities, prefixed IDs, status enums, state transitions, or route/service/db layer boundaries |

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
| Write SvelteKit Code            | `/ceh-web-frontend:write-sveltekit-code`          | Editing Svelte routes, stores, components, or the API client                                                                 |
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

| Agent                     | Invoke                                                  | When                                                       |
| ------------------------- | ------------------------------------------------------- | ---------------------------------------------------------- |
| Vitest Unit Tester        | `@"ceh-web-frontend:vitest-unit-tester (agent)"`        | Isolated unit tests for TypeScript functions or modules    |
| Vitest Integration Tester | `@"ceh-web-frontend:vitest-integration-tester (agent)"` | Components wired with real stores and MSW network handlers |
| Playwright System Tester  | `@"ceh-web-frontend:playwright-system-tester (agent)"`  | Playwright E2E or smoke tests against a running stack      |

---

## Installing in Claude Code

### Step 1 — Add the marketplace

```
/plugin marketplace add cheneeheng/ceh-claude-code-library
```

### Step 2 — Install plugins

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
```

### Manual installation (alternative)

```bash
git clone https://github.com/cheneeheng/ceh-claude-code-library.git ~/ceh-claude-code-library
```

Then add plugin paths to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "plugins": [
    { "path": "~/ceh-claude-code-library/plugins/ceh-core" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-coding-agent" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-git-workflow" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-testing" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-python-service" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-python-library" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-web-frontend" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-seo" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-blog" }
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
