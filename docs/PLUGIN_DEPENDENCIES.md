# Plugin Dependencies

The current dependency graph between `ceh-*` plugins: every declared edge, the reference that
forces it, and what each scenario bundle installs. The rules for an edge are in `CLAUDE.md`
(Plugin Dependencies); this page holds the graph as it stands and the evidence behind each edge.

## The graph

```
ceh-python-service  ──► ceh-testing
ceh-python-library  ──► ceh-testing
ceh-web-frontend    ──► ceh-testing
ceh-ag-ui           ──► ceh-web-frontend
```

`ceh-testing` is a leaf. Three stack plugins sit directly above it, and `ceh-ag-ui` sits above
`ceh-web-frontend`, so the worst-case closure is three plugins (`ceh-ag-ui` → `ceh-web-frontend` →
`ceh-testing`). The cross-cutting rule holds: `ceh-testing` is cross-cutting and depends on nothing.

The five `ceh-scenario-*` bundles sit above all of this. Each is a manifest that lists plugins and
adds no edge between them, so the worst-case closure of a bundle is its own list plus the stack
plugin's closure. See "What each scenario installs" below.

`ceh-usability-audit` declares no dependency. Its references to `ceh-web-frontend`,
`ceh-documentation`, `ceh-seo`, `ceh-python-service` and `ceh-python-library` skills are all
conditional hand-offs or negative routing, which stay prose.

## Edge evidence

| From                                   | To        | Forcing reference                                                                                                                                                                                |
| -------------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ceh-python-service` ──► `ceh-testing` | every run | `skills:` preload of `ceh-testing:design-test-cases` in `pytest-{unit,integration,system}-tester`, and an explicit invocation in `write-pytest-service-tests`                                    |
| `ceh-python-library` ──► `ceh-testing` | every run | Explicit invocation of `ceh-testing:design-test-cases` in `write-pytest-library-tests`                                                                                                           |
| `ceh-web-frontend` ──► `ceh-testing`   | every run | `skills:` preload of `ceh-testing:design-test-cases` in `vitest-{unit,integration}-tester` and `playwright-system-tester`, and an explicit invocation in `write-vitest-playwright-tests`         |
| `ceh-ag-ui` ──► `ceh-web-frontend`     | every run | Explicit invocation of `ceh-web-frontend:design-ui` in `build-ag-ui` (theme install) and `add-canvas-component` (token and class contract): every canvas and every component is built against it |

## What each scenario installs

| Bundle                   | Installs                                                                                                                                                                                                           |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ceh-scenario-service`   | `ceh-core`, `ceh-coding-agent`, `ceh-git-workflow`, `ceh-testing`, `ceh-documentation`, `ceh-python-service`, `ceh-usability-audit`, `ceh-plan-build-review`, `ceh-git-datastore`, `ceh-ag-ui`, `ceh-web-frontend` |
| `ceh-scenario-library`   | `ceh-core`, `ceh-coding-agent`, `ceh-git-workflow`, `ceh-testing`, `ceh-documentation`, `ceh-python-library`, `ceh-usability-audit`, `ceh-plan-build-review`                                                       |
| `ceh-scenario-webapp`    | `ceh-core`, `ceh-coding-agent`, `ceh-git-workflow`, `ceh-testing`, `ceh-documentation`, `ceh-web-frontend`, `ceh-usability-audit`, `ceh-plan-build-review`, `ceh-ag-ui`                                            |
| `ceh-scenario-ideation`  | `ceh-core`, `ceh-git-workflow`, `ceh-business-plan`, `ceh-plan-build-review`                                                                                                                                       |
| `ceh-scenario-editorial` | `ceh-core`, `ceh-git-workflow`, `ceh-blog`, `ceh-documentation`, `ceh-seo`                                                                                                                                         |

`ceh-web-frontend` reaches the service bundle only through `ceh-ag-ui`, and `ceh-testing` is
listed by each stack bundle directly as well as through its stack plugin.

## Checking the graph

```bash
# Every declared edge
grep -H '"dependencies"' plugins/*/.claude-plugin/plugin.json

# Resolution, acyclicity, and bundle shape
python tools/validate-plugins/validate.py
```
