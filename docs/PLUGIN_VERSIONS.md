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
| `ceh-scenario-editorial` | 1.1.0   | `2026-10-08` |
| `ceh-scenario-ideation`  | 1.1.0   | `2026-10-08` |
| `ceh-scenario-library`   | 1.1.0   | `2026-10-08` |
| `ceh-scenario-service`   | 1.1.0   | `2026-10-08` |
| `ceh-scenario-webapp`    | 1.1.0   | `2026-10-08` |

## Standalone plugins

| Plugin                     | Version | Changed in   |
| -------------------------- | ------- | ------------ |
| `ceh-ag-ui`                | 1.1.1   | `2026-10-08` |
| `ceh-blog`                 | 1.0.3   | `2026-10-08` |
| `ceh-business-plan`        | 1.0.7   | `2026-10-08` |
| `ceh-codebase-explanation` | 1.0.2   | `2026-10-08` |
| `ceh-coding-conduct`       | 2.0.3   | `2026-10-08` |
| `ceh-competitor-analysis`  | 1.1.4   | `2026-10-08` |
| `ceh-documentation`        | 1.0.3   | `2026-10-08` |
| `ceh-every-session`        | 2.1.0   | `2026-10-08` |
| `ceh-git-datastore`        | 1.0.3   | `2026-10-08` |
| `ceh-git-workflow`         | 1.0.2   | `2026-10-08` |
| `ceh-plan-build-review`    | 1.1.1   | `2026-10-08` |
| `ceh-python-library`       | 1.0.1   | `2026-10-08` |
| `ceh-python-service`       | 1.0.1   | `2026-10-08` |
| `ceh-seo`                  | 1.1.1   | `2026-10-08` |
| `ceh-testing`              | 1.0.3   | `2026-10-08` |
| `ceh-ui-design`            | 1.0.2   | `2026-10-08` |
| `ceh-usability-audit`      | 1.1.2   | `2026-10-08` |
| `ceh-web-frontend`         | 1.1.2   | `2026-10-08` |
| `ceh-workflow-builder`     | 1.3.2   | `2026-10-08` |
| `ceh-workflow-runner`      | 1.0.1   | `2026-10-08` |
