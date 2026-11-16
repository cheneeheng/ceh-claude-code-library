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
| `ceh-ag-ui`                    | 1.1.6   | `2026-11-16` |
| `ceh-blog-and-seo`             | 2.0.12  | `2026-11-16` |
| `ceh-build-plan`               | 2.0.13  | `2026-11-16` |
| `ceh-product-direction`        | 2.0.13  | `2026-11-16` |
| `ceh-check-build-against-plan` | 1.1.18  | `2026-11-16` |
| `ceh-codebase-explanation`     | 1.3.16  | `2026-11-16` |
| `ceh-coding-conduct`           | 2.5.18  | `2026-11-16` |
| `ceh-competitor-analysis`      | 1.2.13  | `2026-11-16` |
| `ceh-documentation`            | 1.0.11  | `2026-11-14` |
| `ceh-every-session`            | 2.9.24  | `2026-11-16` |
| `ceh-git-workflow`             | 1.5.21  | `2026-11-16` |
| `ceh-python-library`           | 1.0.5   | `2026-11-12` |
| `ceh-python-service`           | 1.1.9   | `2026-11-14` |
| `ceh-security-audit`           | 1.1.14  | `2026-11-16` |
| `ceh-session-learning`         | 2.0.6   | `2026-11-16` |
| `ceh-testing`                  | 1.6.27  | `2026-11-16` |
| `ceh-ui-design`                | 1.0.12  | `2026-11-13` |
| `ceh-usability-audit`          | 1.2.16  | `2026-11-16` |
| `ceh-web-frontend`             | 1.3.6   | `2026-11-13` |
| `ceh-workflow-builder`         | 1.4.12  | `2026-11-16` |
| `ceh-workflow-runner`          | 1.1.11  | `2026-11-16` |
