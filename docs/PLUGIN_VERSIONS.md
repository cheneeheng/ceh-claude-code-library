# Plugin Versions

The version of every plugin as of the latest release, and the release that last changed it.

This repo carries two version layers. Each plugin has its own semantic version in `plugin.json`,
mirrored in `.claude-plugin/marketplace.json`, and that version drives auto-update. The repo
release is a date (`vYYYY.MM.DD`) that marks one consistent state of all plugins together. This
file maps the first layer onto the second.

`plugin.json` stays the source of truth: between releases a plugin may already be ahead of its row
here. Update this file in the release commit, never in a plugin commit: set **Version** for every
plugin bumped since the last release and set its **Changed in** to the new release. A new plugin
gains a row, and a removed plugin loses its row.

Latest release: `v2026.10.03`

## Scenario bundles

| Plugin                   | Version | Changed in    |
| ------------------------ | ------- | ------------- |
| `ceh-scenario-editorial` | 1.0.0   | `v2026.10.02` |
| `ceh-scenario-ideation`  | 1.0.0   | `v2026.10.02` |
| `ceh-scenario-library`   | 1.0.0   | `v2026.10.02` |
| `ceh-scenario-service`   | 1.0.0   | `v2026.10.02` |
| `ceh-scenario-webapp`    | 1.0.0   | `v2026.10.02` |

## Standalone plugins

| Plugin                  | Version | Changed in    |
| ----------------------- | ------- | ------------- |
| `ceh-ag-ui`             | 1.0.0   | `v2026.10.02` |
| `ceh-blog`              | 1.0.0   | `v2026.10.02` |
| `ceh-business-plan`     | 1.0.5   | `v2026.10.02` |
| `ceh-coding-agent`      | 1.0.0   | `v2026.10.02` |
| `ceh-core`              | 1.0.0   | `v2026.10.02` |
| `ceh-documentation`     | 1.0.0   | `v2026.10.02` |
| `ceh-git-datastore`     | 1.0.1   | `v2026.10.02` |
| `ceh-git-workflow`      | 1.0.0   | `v2026.10.02` |
| `ceh-plan-build-review` | 1.0.0   | `v2026.10.02` |
| `ceh-python-library`    | 1.0.0   | `v2026.10.02` |
| `ceh-python-service`    | 1.0.0   | `v2026.10.02` |
| `ceh-seo`               | 1.0.0   | `v2026.10.02` |
| `ceh-testing`           | 1.0.0   | `v2026.10.02` |
| `ceh-usability-audit`   | 1.0.0   | `v2026.10.02` |
| `ceh-web-frontend`      | 1.0.0   | `v2026.10.02` |
| `ceh-workflow-builder`  | 1.2.0   | `v2026.10.03` |
