# Plugin Versions

The current version of every plugin, and the `CHANGELOG.md` section that last changed it.

Each plugin has its own semantic version in `plugin.json`, mirrored in
`.claude-plugin/marketplace.json`, and that version drives auto-update. The repo has no releases.
`CHANGELOG.md` groups changes into one section per date a PR was opened (`YYYY-MM-DD`).

`plugin.json` stays the source of truth. Update this file in the same PR that bumps a plugin: set
**Version** and set **Changed in** to the PR's changelog section date. A new plugin gains a row, and
a removed plugin loses its row.

## Scenario bundles

| Plugin                   | Version | Changed in   |
| ------------------------ | ------- | ------------ |
| `ceh-scenario-editorial` | 1.0.0   | `2026-10-02` |
| `ceh-scenario-ideation`  | 1.0.0   | `2026-10-02` |
| `ceh-scenario-library`   | 1.0.0   | `2026-10-02` |
| `ceh-scenario-service`   | 1.0.0   | `2026-10-02` |
| `ceh-scenario-webapp`    | 1.0.0   | `2026-10-02` |

## Standalone plugins

| Plugin                    | Version | Changed in   |
| ------------------------- | ------- | ------------ |
| `ceh-ag-ui`               | 1.1.0   | `2026-10-07` |
| `ceh-blog`                | 1.0.1   | `2026-10-06` |
| `ceh-business-plan`       | 1.0.5   | `2026-10-02` |
| `ceh-coding-agent`        | 1.0.1   | `2026-10-06` |
| `ceh-competitor-analysis` | 1.1.0   | `2026-10-07` |
| `ceh-core`                | 1.0.0   | `2026-10-02` |
| `ceh-documentation`       | 1.0.1   | `2026-10-06` |
| `ceh-git-datastore`       | 1.0.1   | `2026-10-02` |
| `ceh-git-workflow`        | 1.0.1   | `2026-10-06` |
| `ceh-plan-build-review`   | 1.0.0   | `2026-10-02` |
| `ceh-python-library`      | 1.0.0   | `2026-10-02` |
| `ceh-python-service`      | 1.0.0   | `2026-10-02` |
| `ceh-seo`                 | 1.0.0   | `2026-10-02` |
| `ceh-testing`             | 1.0.0   | `2026-10-02` |
| `ceh-ui-design`           | 1.0.0   | `2026-10-07` |
| `ceh-usability-audit`     | 1.0.1   | `2026-10-07` |
| `ceh-web-frontend`        | 1.1.0   | `2026-10-07` |
| `ceh-workflow-builder`    | 1.3.0   | `2026-10-05` |
| `ceh-workflow-runner`     | 1.0.0   | `2026-10-05` |
