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
| `ceh-ag-ui`                    | 1.1.4   | `2026-10-23` |
| `ceh-blog`                     | 1.0.16  | `2026-10-23` |
| `ceh-build-from-plan`          | 1.0.12  | `2026-10-23` |
| `ceh-build-planning`           | 1.1.13  | `2026-10-23` |
| `ceh-business-plan`            | 1.1.12  | `2026-10-23` |
| `ceh-check-build-against-plan` | 1.0.11  | `2026-10-23` |
| `ceh-codebase-explanation`     | 1.2.9   | `2026-10-23` |
| `ceh-coding-conduct`           | 2.2.16  | `2026-10-23` |
| `ceh-competitor-analysis`      | 1.1.11  | `2026-10-22` |
| `ceh-documentation`            | 1.0.5   | `2026-10-10` |
| `ceh-every-session`            | 2.8.13  | `2026-10-24` |
| `ceh-git-datastore`            | 1.0.6   | `2026-10-15` |
| `ceh-git-workflow`             | 1.4.5   | `2026-10-23` |
| `ceh-orchestration-lab`        | 1.0.6   | `2026-10-22` |
| `ceh-python-library`           | 1.0.4   | `2026-10-15` |
| `ceh-python-service`           | 1.1.4   | `2026-10-15` |
| `ceh-security-audit`           | 1.0.6   | `2026-10-23` |
| `ceh-seo`                      | 1.1.7   | `2026-10-23` |
| `ceh-session-diagnosis`        | 1.0.8   | `2026-10-23` |
| `ceh-session-to-skill`         | 1.0.2   | `2026-10-16` |
| `ceh-testing`                  | 1.4.12  | `2026-10-23` |
| `ceh-ui-design`                | 1.0.7   | `2026-10-23` |
| `ceh-usability-audit`          | 1.1.10  | `2026-10-23` |
| `ceh-web-frontend`             | 1.3.4   | `2026-10-16` |
| `ceh-workflow-builder`         | 1.3.11  | `2026-10-23` |
| `ceh-workflow-runner`          | 1.0.9   | `2026-10-23` |
