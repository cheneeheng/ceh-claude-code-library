# Model audit 2026-10-23

claude-code 2.1.309. Edits applied: no.

| Plugin             | Report                                         | Guides audited                                                        | Pinned files tuned | Strict validate |
| ------------------ | ---------------------------------------------- | --------------------------------------------------------------------- | ------------------ | --------------- |
| ceh-build-planning | [ceh-build-planning.md](ceh-build-planning.md) | fable-5, fable-5-1, haiku-5-5, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | -                  | pass            |

`validate.py`: pass.

## Run cost

| Run                        | Turns | Input | Output | Cache read | Cache write | Cost (USD) |
| -------------------------- | ----: | ----: | -----: | ---------: | ----------: | ---------: |
| ceh-build-planning /doctor |    19 |    16 |  6,115 |    510,224 |     107,960 |       0.54 |
| ceh-build-planning filter  |    20 |    12 |  4,244 |    183,400 |     109,695 |       0.50 |
| **all**                    |    39 |    28 | 10,359 |    693,624 |     217,655 |       1.04 |

## Reviewer checklist

- Keep or drop each proposed edit. Without `--apply`, apply the kept ones from the reports.
- For each plugin whose edits you keep: PATCH-bump `plugin.json` and `marketplace.json`, and update its `docs/PLUGIN_VERSIONS.md` row.
- Before merging, add this PR's `CHANGELOG.md` entry under the date it was opened.
- For each pinned file whose tuning you accept: set its `tuned-for` to its `model` in `tuning.json`.
- Optional: run `claude plugin eval` from a plugin root before merging.
