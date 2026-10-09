# Plugin Dependencies

The current dependency graph between `ceh-*` plugins: every declared edge, the reference that
forces it, and what each scenario bundle installs. The rules for an edge are in `CLAUDE.md`
(Plugin Dependencies); this page holds the graph as it stands and the evidence behind each edge.

## How dependencies behave

- **Declared in `plugin.json` only.** The platform also accepts them in the `marketplace.json`
  entry, with no documented precedence when both are set, so this repo keeps one source of truth
  and `marketplace.json` mirrors only version and description.
- **Bare strings, no version ranges.** Ranges resolve against per-plugin `{name}--v{version}` tags,
  and this repo tags only repo-wide snapshots.
- **Installed and enabled automatically and transitively.** There is no optional dependency, and
  `defaultEnabled: false` does not keep a dependency out. The only way to not install a plugin is to
  leave it out of every `dependencies` list on the path.

## The graph

Arrow = "the left plugin cannot do its job unless the right plugin is installed".

```
ceh-python-service       ──► ceh-testing
ceh-python-library       ──► ceh-testing
ceh-web-frontend         ──► ceh-testing, ceh-ui-design
ceh-ag-ui                ──► ceh-ui-design
ceh-competitor-analysis  ──► ceh-ui-design
```

`ceh-testing` and `ceh-ui-design` are leaves. The worst-case closure is three plugins
(`ceh-web-frontend` → `ceh-testing` + `ceh-ui-design`). The cross-cutting rule holds: `ceh-testing`
is cross-cutting and depends on nothing.

The five `ceh-scenario-*` bundles sit above all of this. Each is a manifest that lists plugins and
adds no edge between them, so the worst-case closure of a bundle is its own list plus the stack
plugin's closure. See "What each scenario installs" below.

`ceh-usability-audit` declares no dependency. Its references to `ceh-web-frontend`, `ceh-ui-design`,
`ceh-documentation`, `ceh-seo`, `ceh-python-service` and `ceh-python-library` skills are all
conditional hand-offs or negative routing, which stay prose.

## Edge evidence

| From                                          | To            | Forcing reference                                                                                                                                                                                  |
| --------------------------------------------- | ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ceh-python-service` ──► `ceh-testing`        | every run     | `skills:` preload of `ceh-testing:design-test-cases` in `pytest-{unit,integration,system}-tester`, and an explicit invocation in `write-pytest-service-tests`                                      |
| `ceh-python-library` ──► `ceh-testing`        | every run     | Explicit invocation of `ceh-testing:design-test-cases` in `write-pytest-library-tests`                                                                                                             |
| `ceh-web-frontend` ──► `ceh-testing`          | every run     | `skills:` preload of `ceh-testing:design-test-cases` in `vitest-{unit,integration}-tester` and `playwright-system-tester`, and an explicit invocation in `write-vitest-playwright-tests`           |
| `ceh-ag-ui` ──► `ceh-ui-design`               | every run     | Explicit invocation of `ceh-ui-design:design-ui` in `build-ag-ui` (theme install) and `add-canvas-component` (token and class contract): every canvas and every component is built against it      |
| `ceh-competitor-analysis` ──► `ceh-ui-design` | every run     | Explicit invocation of `ceh-ui-design:design-ui` in `analyze-competitor` (step 7) and `compare-competitors` (step 6): every report and comparison is rendered as an HTML page                      |
| `ceh-web-frontend` ──► `ceh-ui-design`        | **exception** | No skill invokes it. Kept by user decision (2026-10-07) when `design-ui` moved out of `ceh-web-frontend`, so installing the web stack still installs the design skill. Do not cite it as precedent |

## What each scenario installs

| Bundle                   | Installs                                                                                                                                                                                                                                                                     |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ceh-scenario-service`   | `ceh-every-session`, `ceh-coding-conduct`, `ceh-codebase-explanation`, `ceh-git-workflow`, `ceh-testing`, `ceh-documentation`, `ceh-python-service`, `ceh-usability-audit`, `ceh-build-planning`, `ceh-build-from-plan`, `ceh-check-build-against-plan`, `ceh-git-datastore` |
| `ceh-scenario-library`   | `ceh-every-session`, `ceh-coding-conduct`, `ceh-codebase-explanation`, `ceh-git-workflow`, `ceh-testing`, `ceh-documentation`, `ceh-python-library`, `ceh-usability-audit`, `ceh-build-planning`, `ceh-build-from-plan`, `ceh-check-build-against-plan`                      |
| `ceh-scenario-webapp`    | `ceh-every-session`, `ceh-coding-conduct`, `ceh-codebase-explanation`, `ceh-git-workflow`, `ceh-testing`, `ceh-documentation`, `ceh-web-frontend`, `ceh-usability-audit`, `ceh-build-planning`, `ceh-build-from-plan`, `ceh-check-build-against-plan`, `ceh-ag-ui`           |
| `ceh-scenario-ideation`  | `ceh-every-session`, `ceh-git-workflow`, `ceh-business-plan`, `ceh-build-planning`                                                                                                                                                                                           |
| `ceh-scenario-editorial` | `ceh-every-session`, `ceh-git-workflow`, `ceh-blog`, `ceh-documentation`, `ceh-seo`                                                                                                                                                                                          |

`ceh-testing` is listed by each stack bundle directly as well as through its stack plugin.
`ceh-ui-design` is in no bundle's list but reaches `ceh-scenario-webapp` through both
`ceh-web-frontend` and `ceh-ag-ui`.

## Not in every bundle

| Plugin                                                | Where it is                                          | Note                                                                                                             |
| ----------------------------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `ceh-workflow-builder`                                | no bundle, install it on its own                     | its agent-skills bundle (`ceh-scenario-agent-tooling`) was not migrated, because `ceh-evaluation` stays archived |
| `ceh-workflow-runner`                                 | no bundle, install it on its own                     | split from `ceh-workflow-builder` so a flow runs without the builder; neither depends on the other               |
| `ceh-seo`, `ceh-blog`                                 | `ceh-scenario-editorial` only                        |                                                                                                                  |
| `ceh-ag-ui`                                           | `ceh-scenario-webapp` only                           | it depends on `ceh-ui-design`                                                                                    |
| `ceh-ui-design`                                       | no bundle lists it                                   | installed through `ceh-web-frontend`, `ceh-ag-ui` or `ceh-competitor-analysis`, or on its own                    |
| `ceh-git-datastore`                                   | `ceh-scenario-service` only                          |                                                                                                                  |
| `ceh-business-plan`                                   | `ceh-scenario-ideation` only                         |                                                                                                                  |
| `ceh-build-from-plan`, `ceh-check-build-against-plan` | the three stack bundles, not `ceh-scenario-ideation` | ideation shapes the idea and plans the build, it builds nothing yet                                              |
| `ceh-coding-conduct`, `ceh-testing`                   | the three stack bundles, not the others              |                                                                                                                  |
| `ceh-orchestration-lab`                               | no bundle, install it on its own                     | experimental, so it never enters a bundle                                                                        |
| Anything under `archive/`                             | no bundle, not published                             | experimental plugins never enter a bundle                                                                        |

## Rules for an edge

`CLAUDE.md` (Plugin Dependencies) holds the first three. The validator enforces the last two.

1. **The reference fires on every run of the skill or agent.** A conditional handoff stays prose.
2. **Negative routing never counts.** It names an alternative, and an edge would install what the
   user steered away from.
3. **A cross-cutting plugin depends only on cross-cutting plugins.** This keeps the graph layered.
4. **A non-bundle plugin never depends on a scenario bundle.** A bundle is an install entry point,
   and depending on one drags a whole scenario into an unrelated install.
5. **An explicit invocation needs its edge.** `Invoke the Skill tool with skill="ceh-x:y"` must
   target a skill in the same plugin or a declared dependency, and the target must not set
   `disable-model-invocation: true`. A call to such a target fails silently.

Do not convert every backtick-quoted skill name into an invocation. Most references are advisory,
and a sweep would pull a multi-plugin closure into a single install.

References that look like edges but deliberately are not:

| Reference                                                                                                                               | Why it stays prose                                                                                                                           |
| --------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `ceh-coding-conduct:shrink-diff` / `refactor-repo` → `ceh-testing:verify-behavior-preserved`                                            | Conditional, only past a mechanical transform                                                                                                |
| `ceh-coding-conduct:shrink-diff` / `refactor-repo` → `ceh-git-workflow` (`code-review`, `pull-request`, `branch`)                       | Negative routing and advisory pointers                                                                                                       |
| `ceh-codebase-explanation:document-architecture` → `ceh-python-service:write-postgresql-code`                                           | Advisory ("mirrors"), and a cross-cutting plugin cannot depend on a stack plugin                                                             |
| `ceh-testing:verify-behavior-preserved` → `ceh-coding-conduct:shrink-diff` / `refactor-repo`                                            | Advisory pointer to the skills it pairs with                                                                                                 |
| `ceh-testing:design-test-cases` → the three stack testing skills                                                                        | Names the owner of the tooling. An edge would create a cycle                                                                                 |
| `ceh-usability-audit` → `ceh-web-frontend`, `ceh-ui-design`, `ceh-documentation`, `ceh-seo`, `ceh-git-workflow`, the two Python plugins | Conditional hand-offs and negative routing, for example WCAG only when there is a UI                                                         |
| `ceh-documentation` → `ceh-git-workflow:update-readme`, `ceh-codebase-explanation:document-architecture` / `explain-codebase`           | Negative routing                                                                                                                             |
| `ceh-seo:write-project-listing-text` → `ceh-git-workflow:update-readme`                                                                 | Negative routing                                                                                                                             |
| `ceh-build-planning` ↔ `ceh-build-from-plan` ↔ `ceh-check-build-against-plan`                                                           | Conditional hand-offs between stages ("when installed") and negative routing. An edge would install every stage for a user who enters at one |
| `ceh-check-build-against-plan` → `ceh-git-workflow:code-review`, `ceh-testing:explore-app-for-bugs`                                     | Negative routing                                                                                                                             |
| `ceh-build-from-plan:implement-from-plan` → `ceh-testing:write-test-first`                                                              | Conditional, "when `ceh-testing` is installed"                                                                                               |
| `ceh-python-library` → `ceh-python-service` (testing and environment skills)                                                            | Negative routing                                                                                                                             |
| `ceh-web-frontend:visualize-graph-cytoscape` → `ceh-codebase-explanation:document-architecture`                                         | Negative routing                                                                                                                             |
| `ceh-git-datastore` README → `ceh-python-service:write-postgresql-code`, `ceh-codebase-explanation:document-architecture`               | README pointers only, no skill body names them                                                                                               |
| `ceh-business-plan:find-product-market-fit` → the `ceh-build-planning` plan format                                                      | It reads only the plans folder and three section names (see `docs/CROSS_REFERENCES.md`, "Build plan format")                                 |

## Checking and changing the graph

```bash
# Every declared edge
grep -H '"dependencies"' plugins/*/*/.claude-plugin/plugin.json

# Every cross-plugin agent preload
grep -A6 '^skills:' plugins/standalone/*/agents/*.md | grep -- '- ceh-'

# Resolution, acyclicity, bundle shape, and rules 4 and 5
python tools/validate-plugins/validate.py
```

Adding or removing a `dependencies` entry is a **MINOR** bump for that plugin, in both `plugin.json`
and `.claude-plugin/marketplace.json`. Update this page in the same commit.
