# Model audit 2026-10-15

claude-code 2.1.301. Edits applied: no.

| Plugin | Report | Guides audited | Pinned files tuned | Strict validate |
| --- | --- | --- | --- | --- |
| ceh-ag-ui | [ceh-ag-ui.md](ceh-ag-ui.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-build-from-plan | [ceh-build-from-plan.md](ceh-build-from-plan.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-build-planning | [ceh-build-planning.md](ceh-build-planning.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-business-plan | [ceh-business-plan.md](ceh-business-plan.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-check-build-against-plan | [ceh-check-build-against-plan.md](ceh-check-build-against-plan.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-competitor-analysis | [ceh-competitor-analysis.md](ceh-competitor-analysis.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-git-datastore | [ceh-git-datastore.md](ceh-git-datastore.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-orchestration-lab | [ceh-orchestration-lab.md](ceh-orchestration-lab.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | agents/implementer.md | pass |
| ceh-python-library | [ceh-python-library.md](ceh-python-library.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | - | pass |
| ceh-python-service | [ceh-python-service.md](ceh-python-service.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | agents/pytest-integration-tester.md, agents/pytest-system-tester.md, agents/pytest-unit-tester.md, agents/python-service-reviewer.md | pass |

`validate.py`: pass.

## Reviewer checklist

- Keep or drop each proposed edit. Without `--apply`, apply the kept ones from the reports.
- For each plugin whose edits you keep: PATCH-bump `plugin.json` and `marketplace.json`, and update its `docs/PLUGIN_VERSIONS.md` row.
- Before merging, add this PR's `CHANGELOG.md` entry under the date it was opened.
- For each pinned file whose tuning you accept: set its `tuned-for` to its `model` in `tuning.json`.
- Optional: run `claude plugin eval` from a plugin root before merging.
