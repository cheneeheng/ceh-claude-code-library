# Plugin Versions

The current version of every plugin, and the `CHANGELOG.md` section that last changed it.

Each plugin has its own semantic version in `plugin.json`, mirrored in
`.claude-plugin/marketplace.json`, and that version drives auto-update. The repo has no releases.
`CHANGELOG.md` groups changes into one section per date a PR was opened (`YYYY-MM-DD`).

`plugin.json` stays the source of truth. Update this file in the same PR that bumps a plugin: set
**Version** and set **Changed in** to the PR's changelog section date. A new plugin gains a row, and
a removed plugin loses its row.

## Standalone plugins

| Plugin                         | Version | Changed in   |
| ------------------------------ | ------- | ------------ |
| `ceh-ag-ui`                    | 1.1.5   | `2026-11-12` |
| `ceh-blog-and-seo`             | 2.0.10  | `2026-11-14` |
| `ceh-build-plan`               | 2.0.10  | `2026-11-14` |
| `ceh-product-direction`        | 2.0.9   | `2026-11-14` |
| `ceh-check-build-against-plan` | 1.1.17  | `2026-11-14` |
| `ceh-codebase-explanation`     | 1.3.13  | `2026-11-14` |
| `ceh-coding-conduct`           | 2.5.15  | `2026-11-14` |
| `ceh-competitor-analysis`      | 1.2.12  | `2026-11-14` |
| `ceh-documentation`            | 1.0.11  | `2026-11-14` |
| `ceh-every-session`            | 2.9.20  | `2026-11-14` |
| `ceh-git-workflow`             | 1.5.18  | `2026-11-14` |
| `ceh-python-library`           | 1.0.5   | `2026-11-12` |
| `ceh-python-service`           | 1.1.9   | `2026-11-14` |
| `ceh-security-audit`           | 1.1.12  | `2026-11-14` |
| `ceh-session-learning`         | 2.0.4   | `2026-11-14` |
| `ceh-testing`                  | 1.6.23  | `2026-11-14` |
| `ceh-ui-design`                | 1.0.12  | `2026-11-13` |
| `ceh-usability-audit`          | 1.2.14  | `2026-11-14` |
| `ceh-web-frontend`             | 1.3.6   | `2026-11-13` |
| `ceh-workflow-builder`         | 1.4.11  | `2026-11-14` |
| `ceh-workflow-runner`          | 1.1.10  | `2026-11-14` |
