# Plugin Dependencies

The current dependency graph between `ceh-*` plugins: every declared edge, the reference that
forces it, and what each scenario bundle installs. The rules for an edge are in `CLAUDE.md`
(Plugin Dependencies); this page holds the graph as it stands and the evidence behind each edge.

## The graph

```
ceh-python-service  ──► ceh-testing
ceh-python-library  ──► ceh-testing
ceh-web-frontend    ──► ceh-testing
```

`ceh-testing` is a leaf. The three stack plugins sit above it, so the worst-case closure is two
plugins. The cross-cutting rule holds: `ceh-testing` is cross-cutting and depends on nothing.

## Edge evidence

| From                                   | To        | Forcing reference                                                                                                                                             |
| -------------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ceh-python-service` ──► `ceh-testing` | every run | `skills:` preload of `ceh-testing:design-test-cases` in `python-{unit,integration,system}-tester`, and an explicit invocation in `write-pytest-service-tests` |
| `ceh-python-library` ──► `ceh-testing` | every run | Explicit invocation of `ceh-testing:design-test-cases` in `write-pytest-library-tests`                                                                        |
| `ceh-web-frontend` ──► `ceh-testing`   | every run | `skills:` preload of `ceh-testing:design-test-cases` in `ts-{unit,integration,system}-tester`, and an explicit invocation in `write-vitest-playwright-tests`  |

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
