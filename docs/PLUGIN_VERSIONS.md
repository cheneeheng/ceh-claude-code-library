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
| `ceh-ag-ui`                    | 1.1.3   | `2026-10-15` |
| `ceh-blog`                     | 1.0.9   | `2026-10-13` |
| `ceh-build-from-plan`          | 1.0.5   | `2026-10-18` |
| `ceh-build-planning`           | 1.1.5   | `2026-10-15` |
| `ceh-business-plan`            | 1.1.6   | `2026-10-15` |
| `ceh-check-build-against-plan` | 1.0.5   | `2026-10-15` |
| `ceh-codebase-explanation`     | 1.2.4   | `2026-10-11` |
| `ceh-coding-conduct`           | 2.2.12  | `2026-10-18` |
| `ceh-competitor-analysis`      | 1.1.8   | `2026-10-15` |
| `ceh-documentation`            | 1.0.5   | `2026-10-10` |
| `ceh-every-session`            | 2.8.4   | `2026-10-19` |
| `ceh-git-datastore`            | 1.0.6   | `2026-10-15` |
| `ceh-git-workflow`             | 1.4.0   | `2026-10-18` |
| `ceh-orchestration-lab`        | 1.0.3   | `2026-10-15` |
| `ceh-python-library`           | 1.0.4   | `2026-10-15` |
| `ceh-python-service`           | 1.1.4   | `2026-10-15` |
| `ceh-security-audit`           | 1.0.2   | `2026-10-16` |
| `ceh-seo`                      | 1.1.5   | `2026-10-16` |
| `ceh-session-diagnosis`        | 1.0.4   | `2026-10-16` |
| `ceh-session-to-skill`         | 1.0.2   | `2026-10-16` |
| `ceh-testing`                  | 1.4.8   | `2026-10-18` |
| `ceh-ui-design`                | 1.0.6   | `2026-10-16` |
| `ceh-usability-audit`          | 1.1.6   | `2026-10-16` |
| `ceh-web-frontend`             | 1.3.4   | `2026-10-16` |
| `ceh-workflow-builder`         | 1.3.7   | `2026-10-16` |
| `ceh-workflow-runner`          | 1.0.5   | `2026-10-16` |
