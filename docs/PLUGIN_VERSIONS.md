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
| `ceh-blog-and-seo`             | 2.0.3   | `2026-11-12` |
| `ceh-build-plan`               | 2.0.3   | `2026-11-12` |
| `ceh-product-direction`        | 2.0.3   | `2026-11-12` |
| `ceh-check-build-against-plan` | 1.1.13  | `2026-11-12` |
| `ceh-codebase-explanation`     | 1.3.7   | `2026-11-12` |
| `ceh-coding-conduct`           | 2.5.8   | `2026-11-12` |
| `ceh-competitor-analysis`      | 1.2.7   | `2026-11-12` |
| `ceh-documentation`            | 1.0.9   | `2026-11-12` |
| `ceh-every-session`            | 2.9.11  | `2026-11-12` |
| `ceh-git-workflow`             | 1.5.10  | `2026-11-12` |
| `ceh-python-library`           | 1.0.4   | `2026-10-15` |
| `ceh-python-service`           | 1.1.6   | `2026-11-12` |
| `ceh-security-audit`           | 1.1.7   | `2026-11-12` |
| `ceh-session-learning`         | 2.0.1   | `2026-11-12` |
| `ceh-testing`                  | 1.6.15  | `2026-11-12` |
| `ceh-ui-design`                | 1.0.11  | `2026-11-12` |
| `ceh-usability-audit`          | 1.2.8   | `2026-11-12` |
| `ceh-web-frontend`             | 1.3.4   | `2026-10-16` |
| `ceh-workflow-builder`         | 1.4.7   | `2026-11-12` |
| `ceh-workflow-runner`          | 1.1.6   | `2026-11-12` |
