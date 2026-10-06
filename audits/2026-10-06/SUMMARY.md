# Model audit 2026-10-06

claude-code 2.1.291. Edits applied: yes.

| Plugin           | Report                                     | Guides audited                                             | Pinned files tuned | Strict validate |
| ---------------- | ------------------------------------------ | ---------------------------------------------------------- | ------------------ | --------------- |
| ceh-core         | [ceh-core.md](ceh-core.md)                 | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | -                  | pass            |
| ceh-coding-agent | [ceh-coding-agent.md](ceh-coding-agent.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | -                  | pass            |
| ceh-git-workflow | [ceh-git-workflow.md](ceh-git-workflow.md) | fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5 | -                  | pass            |

`validate.py`: pass.

## Reviewer checklist

- Keep or drop each proposed edit. Without `--apply`, apply the kept ones from the reports.
- For each plugin whose edits you keep: PATCH-bump `plugin.json` and `marketplace.json`, and update its `docs/PLUGIN_VERSIONS.md` row.
- Before merging, add this PR's `CHANGELOG.md` entry under the date it was opened.
- For each pinned file whose tuning you accept: set its `tuned-for` to its `model` in `tuning.json`.
- Optional: run `claude plugin eval` from a plugin root before merging.
