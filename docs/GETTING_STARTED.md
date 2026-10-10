# Getting started

Which plugins to install the first time, and which to leave out until you need them. Do not install
all of them: every installed plugin adds its skill descriptions to every session, and the ones
with hooks run on every session too. Install a small core once, then add one plugin when you reach
the moment it serves.

The route below follows the product lifecycle in [`STRATEGY.md`](STRATEGY.md): Shape, Build, Prove,
Tell. You can start at any stage. Each plugin works installed alone, and with several installed they
chain through the committed files each one writes.

## 1. Add the marketplace

```
/plugin marketplace add cheneeheng/ceh-claude-code-library
```

## 2. Install the core once, at user scope

| Plugin               | Install when                  | What you get                                                                                                          |
| -------------------- | ----------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `ceh-git-workflow`   | you work in git repos         | branches, commits, pull requests from open to merge, changelog, code review, and a hook that blocks edits on `main`   |
| `ceh-coding-conduct` | you write code with Claude    | the coding contract, write-less-code, root-cause debugging, design before code. Always on, through hooks              |
| `ceh-every-session`  | optional, any kind of session | session handoff, research notes, questionnaires, plan stress-tests, and a usage-limit guard. Always on, through hooks |

```
/plugin install ceh-git-workflow@ceh-claude-code-library --scope user
/plugin install ceh-coding-conduct@ceh-claude-code-library --scope user
```

Skip `ceh-coding-conduct` if you only write business plans or posts: its hooks and output style
are for coding sessions.

## 3. Add the plugin for what you are about to do, at project scope

`--scope project` keeps a plugin to the repo that needs it, so a repo that is only being planned
does not load the build and launch plugins.

| Stage | You are about to...                           | Install                                             | Skill that fires                                                        | It writes                                  |
| ----- | --------------------------------------------- | --------------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------ |
| Shape | test whether an idea is worth building        | `ceh-business-plan`                                 | `ceh-business-plan:find-product-market-fit`                             | `BUSINESS_PLAN.md`                         |
| Shape | learn from a competitor's repo or product     | `ceh-competitor-analysis`                           | `ceh-competitor-analysis:analyze-competitor`                            | reports in `.agents_workspace/`            |
| Build | plan a new app or one feature                 | `ceh-build-planning`                                | `ceh-build-planning:write-build-plan`                                   | `docs/plans/<slug>.md`                     |
| Build | build from that plan                          | `ceh-build-from-plan` and your stack plugin (below) | `ceh-build-from-plan:implement-from-plan`                               | the code, the plan's evidence              |
| Build | write the user and operator docs              | `ceh-documentation`                                 | `ceh-documentation:write-project-docs`                                  | `docs/`                                    |
| Prove | check the code is what the plan said          | `ceh-check-build-against-plan`                      | `ceh-check-build-against-plan:check-build-against-plan`                 | a report in the session                    |
| Prove | test it and roll up the evidence              | `ceh-testing` (a stack plugin already brings it)    | `ceh-testing:explore-app-for-bugs`, `ceh-testing:write-evidence-report` | `docs/EVIDENCE.md`                         |
| Prove | check a stranger can use it                   | `ceh-usability-audit`                               | `ceh-usability-audit:simulate-newcomer-first-run`                       | a report in `.agents_workspace/`           |
| Prove | audit the whole codebase for security         | `ceh-security-audit`                                | `ceh-security-audit:audit-codebase-security`                            | a report                                   |
| Tell  | write a launch post                           | `ceh-blog`                                          | `ceh-blog:draft-post`                                                   | a post                                     |
| Tell  | make it findable: README, listings, web pages | `ceh-seo`                                           | `ceh-seo:write-project-listing-text`, `ceh-seo:make-page-crawlable`     | README first screen, listings, page markup |

Pick one stack plugin for the build. Each brings `ceh-testing`, and the web one also brings
`ceh-ui-design`:

| You are building           | Install              |
| -------------------------- | -------------------- |
| a Python backend service   | `ceh-python-service` |
| a distributable Python lib | `ceh-python-library` |
| a web frontend             | `ceh-web-frontend`   |

```
/plugin install ceh-build-planning@ceh-claude-code-library --scope project
```

The Tell stage reads `BUSINESS_PLAN.md` and `docs/EVIDENCE.md` when they exist. Without them it
still runs, and says which claims rest on nothing proven.

## 4. Add these only when the moment arrives

| Plugin                     | Install when                                                                              |
| -------------------------- | ----------------------------------------------------------------------------------------- |
| `ceh-codebase-explanation` | you inherit a repo, or need an architecture doc, a glossary, or why code is the way it is |
| `ceh-ui-design`            | you design a UI or HTML page without `ceh-web-frontend`                                   |
| `ceh-ag-ui`                | you build a generative-UI canvas for an AG-UI agent                                       |
| `ceh-git-datastore`        | you want an app to run on a bare git repo instead of a database                           |
| `ceh-workflow-builder`     | the same product work repeats and an agent should run it                                  |
| `ceh-workflow-runner`      | a built `flow.yaml` must run, here or headless                                            |
| `ceh-session-to-skill`     | a task just went well and you want it as a reusable skill                                 |
| `ceh-session-diagnosis`    | a session went wrong and you want to know why from its transcript                         |
| `ceh-orchestration-lab`    | experimental: you want to compare orchestration strategies on real tasks                  |

## 5. Check it worked

```
/help
```

The `ceh-*:` skills you installed should appear in the skills list. To drop a plugin you no longer
need, `/plugin uninstall <name>@ceh-claude-code-library`. Prerequisites (Python for hooks, `uv`,
Bun, the GitHub CLI) are in the root [`README.md`](../README.md#prerequisites).
