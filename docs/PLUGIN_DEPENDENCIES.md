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

| Bundle | Installs |
| ------ | -------- |

## Checking the graph

```bash
# Every declared edge
grep -H '"dependencies"' plugins/*/.claude-plugin/plugin.json

# Resolution, acyclicity, bundle shape, and that every bundle reaches ceh-scenario-core
python tools/validate-plugins/validate.py
```
