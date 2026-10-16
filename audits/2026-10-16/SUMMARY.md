# Model audit 2026-10-16

claude-code 2.1.301. Edits applied: no.

| Plugin | Report | Guides audited | Pinned files tuned | Strict validate |
| --- | --- | --- | --- | --- |
| ceh-security-audit | [ceh-security-audit.md](ceh-security-audit.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-seo | [ceh-seo.md](ceh-seo.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-session-diagnosis | [ceh-session-diagnosis.md](ceh-session-diagnosis.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | agents/transcript-analyst.md | pass |
| ceh-session-to-skill | [ceh-session-to-skill.md](ceh-session-to-skill.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-testing | [ceh-testing.md](ceh-testing.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-ui-design | [ceh-ui-design.md](ceh-ui-design.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-usability-audit | [ceh-usability-audit.md](ceh-usability-audit.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | agents/newcomer-simulator.md | pass |
| ceh-web-frontend | [ceh-web-frontend.md](ceh-web-frontend.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | agents/playwright-system-tester.md, agents/vitest-integration-tester.md, agents/vitest-unit-tester.md, agents/web-frontend-reviewer.md | pass |
| ceh-workflow-builder | [ceh-workflow-builder.md](ceh-workflow-builder.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-workflow-runner | [ceh-workflow-runner.md](ceh-workflow-runner.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |

`validate.py`: pass.

## Reviewer checklist

- Keep or drop each proposed edit. Without `--apply`, apply the kept ones from the reports.
- For each plugin whose edits you keep: PATCH-bump `plugin.json` and `marketplace.json`, and update its `docs/PLUGIN_VERSIONS.md` row.
- Before merging, add this PR's `CHANGELOG.md` entry under the date it was opened.
- For each pinned file whose tuning you accept: set its `tuned-for` to its `model` in `tuning.json`.
- Optional: run `claude plugin eval` from a plugin root before merging.
