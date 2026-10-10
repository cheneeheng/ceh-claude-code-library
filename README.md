# ceh-claude-code-library

Claude Code plugins that guide autonomous agents through a product's life: shaping the idea,
building and proving the software, and getting it in front of the people who should find it. They
are written for agents first and people second. An agent follows them with no human watching, and a
person using Claude Code gets the same guidance and can override it with an explicit instruction.
Plugins are organized around **use cases**: load the ones that match what you are building.

> **For Claude Code, when a user asks you to set up this repo:** follow
> https://raw.githubusercontent.com/cheneeheng/ceh-claude-code-library/main/docs/GETTING_STARTED.md.
> Ask the user what they are about to do before you install anything. Then install the core and
> only the plugins that moment needs, running each install yourself with the `claude plugin` CLI,
> not the `/plugin` slash command. Do not install every plugin. When you finish, tell the user to
> run `/reload-plugins`.

**New here?** Start with [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md): which plugins to
install first, and which to leave until you need them.

**Catalog:** [`docs/CATALOG.md`](docs/CATALOG.md) — every skill and agent, with how to invoke it
and the moment it is for.

**Vision:** [`docs/VISION.md`](docs/VISION.md) — the identity, scope, and principles that settle
decisions about this repo.

**Guides:** [`docs/TESTING_WORKFLOW.md`](docs/TESTING_WORKFLOW.md) — how `ceh-testing` and the three
stack testing skills route between each other, with the trigger phrases and sequence for each moment.

**Versions:** each plugin keeps its own semantic version, and the repo has no releases.
[`CHANGELOG.md`](CHANGELOG.md) groups changes by the date each PR was opened, and
[`docs/PLUGIN_VERSIONS.md`](docs/PLUGIN_VERSIONS.md) lists every plugin's current version.

## Plugins

| Plugin                   | Install as                     | Contents                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ------------------------ | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Every Session            | `ceh-every-session`            | Standards every session loads, however Claude Code is used: session save and load (`hand-off-session`); questions for someone outside the session (`write-questionnaire`); cited research notes (`write-research-note`); plan stress-tests (`stress-test-plan`); fixes for repeated mistakes (`prevent-repeat-mistake`); usage-limit guard + handoff (`usage-limit-handoff`); context economy (`delegate-bulk-reads`, `bulk-reader`, opt-in read guards) |
| Coding Conduct           | `ceh-coding-conduct`           | Behavioral contract for coding agents (always-on via SessionStart hook); write-less-code minimalism (always-on via hooks); retroactive refactoring (`shrink-diff`, `refactor-repo`); debugging before fixing (`find-root-cause`); design before code (`sketch-design`); the `CEH Coding Conduct` output style (always-on via `force-for-plugin`)                                                                                                         |
| Codebase Explanation     | `ceh-codebase-explanation`     | Leave a codebase understood: explaining a subsystem, design, or diff until it lands (`explain-until-understood`); whole-repo orientation (`explain-codebase`); the living architecture document (`document-architecture`); why code is the way it is, from history (`trace-code-rationale`); a committed glossary (`maintain-glossary`)                                                                                                                  |
| Git Workflow             | `ceh-git-workflow`             | Branching, commits, pull requests from open to merge, changelog entries, README upkeep (`update-readme`), releases including hotfixes, code review and addressing review comments (`address-review-comments`), engineering retros (`write-engineering-retro`); a hook that blocks file edits on the default branch                                                                                                                                       |
| Testing                  | `ceh-testing`                  | Stack-agnostic testing technique: reproduce-first bug fixes (`test-a-bug-fix`), test-first new code (`write-test-first`), test-case design, suite audit (`audit-test-suite`), behavior-preservation checks, performance measurement (`measure-performance`), exploring the running app for bugs (`explore-app-for-bugs`), the risk gaps a green suite misses, and the committed evidence report a launch reads (`write-evidence-report`)                 |
| Python Service           | `ceh-python-service`           | FastAPI, asyncpg, PostgreSQL schema, Alembic, uv/ruff/mypy, and pytest for web services; unit, integration, and system tester agents                                                                                                                                                                                                                                                                                                                     |
| Python Library           | `ceh-python-library`           | Packaging and publishing, public API surface and semver, uv/ruff/mypy, and pytest for distributable libraries with no web dependencies                                                                                                                                                                                                                                                                                                                   |
| Web Frontend             | `ceh-web-frontend`             | SvelteKit and React on Bun + Vite: TypeScript style and tooling, Vitest/Playwright testing, screenshot parity checks, accessibility, Cytoscape.js graphs; unit, integration, and system tester agents. Brings `ceh-ui-design` for visual design                                                                                                                                                                                                          |
| UI Design                | `ceh-ui-design`                | Framework-agnostic visual design for any UI or HTML page: layout archetypes, hierarchy, navigation and in-page contents, states, finishing recipes, and the Meridian and Tidewater themes                                                                                                                                                                                                                                                                |
| SEO                      | `ceh-seo`                      | Discoverability for anything exposed to the internet: crawlable public web pages (head tags, structured data, sitemap, rendering), the `llms.txt` agent index, and the findability of README, package, and landing text                                                                                                                                                                                                                                  |
| Blog                     | `ceh-blog`                     | Blog posts in a personal, series-first voice: draft from a topic, repo, or notes (interviewing when material is thin), edit an existing draft, repurpose a finished post for X, LinkedIn, TL;DR, and newsletters                                                                                                                                                                                                                                         |
| Build Planning           | `ceh-build-planning`           | Decide how to build a new app or one feature before any code: one committed plan file with scope, the design decisions the build needs, and phases that each end in a runnable check                                                                                                                                                                                                                                                                     |
| Build From Plan          | `ceh-build-from-plan`          | Build a written plan phase by phase: the failing test first, only what the phase names, the phase's check run, and the evidence recorded in the plan                                                                                                                                                                                                                                                                                                     |
| Check Build Against Plan | `ceh-check-build-against-plan` | Check whether finished code is what its plan said to build: gaps, deviations, and unplanned extras with quoted evidence, and each phase's check rerun                                                                                                                                                                                                                                                                                                    |
| Documentation            | `ceh-documentation`            | User-facing documentation: a full docs set under `docs/`, user guides and operator runbooks, an exhaustive API reference, concept pages with sourced design rationale, and runnable examples                                                                                                                                                                                                                                                             |
| AG-UI                    | `ceh-ag-ui`                    | Generative-UI canvases for AG-UI agents: the agent places components from a fixed, Tidewater-styled catalogue and can never restyle them; catalogue components, a Claude-backed FastAPI agent server, live shared state, and human approval steps. Worked examples: [`examples/ceh-ag-ui/`](examples/ceh-ag-ui/)                                                                                                                                         |
| Usability Audit          | `ceh-usability-audit`          | Measure whether a non-expert can actually use what you built: cold persona-constrained walkthroughs (`newcomer-simulator`), a five-question interface audit across web UI/CLI/library/app surfaces, error-message rewrites, and a plain-language pass                                                                                                                                                                                                    |
| Business Plan            | `ceh-business-plan`            | Turn a product idea or an existing app plan into a validated business plan: a product-market-fit interview loop that interrogates the weakest assumption until a readiness gate passes, then a board-style review and six specialist passes on strategy, unit economics, go-to-market, premortem, the 90-day operating plan, and investor materials                                                                                                      |
| Git Datastore            | `ceh-git-datastore`            | Run an app on a bare git repo instead of a database while that still fits: a gate that talks you out of it when it does not, a plumbing-only store, and the pinned-snapshot migration to Postgres or SQLite                                                                                                                                                                                                                                              |
| Workflow Builder         | `ceh-workflow-builder`         | Turn product work that repeats in the same shape (a weekly SEO pass, a pre-release check) into a runnable artifact: interview it into a spec, then emit one skill or a gated workflow skill with handoff schemas into the target repo                                                                                                                                                                                                                    |
| Session to Skill         | `ceh-session-to-skill`         | Turn the task just finished into a reusable skill, built from the steps that worked in the session, with your corrections as rules and per-run values as arguments                                                                                                                                                                                                                                                                                       |
| Session Diagnosis        | `ceh-session-diagnosis`        | Find why a session went wrong from its transcript: four parallel `transcript-analyst` lenses, every finding citing a transcript line, each root cause routed to a fix, and a scrubbed copy for sharing                                                                                                                                                                                                                                                   |
| Security Audit           | `ceh-security-audit`           | Audit a whole codebase, not one diff: map the attack surface, trace each entry point to its sinks, and report every exploitable finding with its attacker, severity, and fix                                                                                                                                                                                                                                                                             |
| Workflow Runner          | `ceh-workflow-runner`          | Run a built `flow.yaml` workflow for repeated product work, interactive or headless: stages on Claude Code's native tools, plus approvals, re-run checks, run state and resume. Install it wherever a flow runs, without the builder                                                                                                                                                                                                                     |
| Competitor Analysis      | `ceh-competitor-analysis`      | Study a competitor's repo or product and learn from it: one evidence-anchored report each (breakdown, inventory, "oh wow" mechanisms, what to incorporate), then a side-by-side comparison with your own work. Repos are read as untrusted data, never run                                                                                                                                                                                               |
| Orchestration Lab        | `ceh-orchestration-lab`        | **Experimental.** Run real coding tasks under one of two orchestration strategies (plan then implement, or a supervised orchestrate loop) with a cheaper worker model, and log every run with its base commit, token usage by model, and your verdict                                                                                                                                                                                                    |

### By lifecycle stage

| Stage      | Question it answers                                    | Plugins                                                                                                                                                                                                         |
| ---------- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Shape      | What should exist, for whom, and is it worth building? | `ceh-business-plan`, `ceh-competitor-analysis`                                                                                                                                                                  |
| Build      | How is it built? Then build it: code, UI, docs         | `ceh-build-planning`, `ceh-build-from-plan`, `ceh-python-service`, `ceh-python-library`, `ceh-web-frontend`, `ceh-ui-design`, `ceh-ag-ui`, `ceh-git-datastore`, `ceh-documentation`, `ceh-codebase-explanation` |
| Prove      | Does it work, is it safe, and can a person use it?     | `ceh-testing`, `ceh-usability-audit`, `ceh-check-build-against-plan`, `ceh-security-audit`                                                                                                                      |
| Tell       | Who should find it, and what do they read?             | `ceh-blog`, `ceh-seo`                                                                                                                                                                                           |
| Every step | How the agent behaves, commits, and runs repeated work | `ceh-every-session`, `ceh-coding-conduct`, `ceh-git-workflow`, `ceh-workflow-builder`, `ceh-workflow-runner`, `ceh-session-to-skill`, `ceh-session-diagnosis`, `ceh-orchestration-lab` (experimental)           |

Each plugin is self-contained: a foundational standard needed by more than one plugin is duplicated
into each instead of extracted into a shared base, so you install only the stage you are in. The
every-step plugins hold a discipline that applies whatever you are building, so they load
_alongside_ a stage plugin, not instead of one. Which to install first is in
[`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md).

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

### Step 2 — Install what you need now

Do not install everything. Follow [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md): a small
core once at user scope, then one plugin per stage at project scope as you reach it. The guide has
the commands, and every plugin is listed in the [Plugins](#plugins) table above.

Dependencies install automatically: each stack plugin brings `ceh-testing`, and `ceh-web-frontend`,
`ceh-ag-ui` and `ceh-competitor-analysis` bring `ceh-ui-design`. Install `ceh-workflow-builder`
where you author a flow and `ceh-workflow-runner` wherever a flow runs: neither brings the other.
`ceh-orchestration-lab` is experimental: install it only in the projects where you want to try
orchestration strategies.

### Step 3 — Verify

```
/reload-plugins
/help
```

Installed plugins load after `/reload-plugins` or in a new session. Then the `ceh-*:` skills appear
in the skills list.

### From a local clone (alternative)

Clone the repo and add the clone as the marketplace in Step 1, then install as in Step 2:

```bash
git clone https://github.com/cheneeheng/ceh-claude-code-library.git ~/ceh-claude-code-library
```

```
/plugin marketplace add ~/ceh-claude-code-library
```

Plugins from a marketplace added by local path load in place, so a `git pull` takes effect at the
next session or `/reload-plugins`. To try one plugin for a single session without installing it,
start Claude Code with
`claude --plugin-dir ~/ceh-claude-code-library/plugins/standalone/ceh-<plugin>`.

---

## Contributing

The repo tools, the CI gate, and the formatting setup are in [`CONTRIBUTING.md`](CONTRIBUTING.md).
