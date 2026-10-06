# model-audit

Keeps the `ceh-*` plugins aligned with Anthropic's
[prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).
Each per-model guide on that page is written as a diff from its predecessor, so the tooling only
tracks which guides each plugin has been checked against. It never compares model releases itself.

The entry point is this repo-local skill, `/model-audit`, or the weekly
`.github/workflows/model-audit.yml`, which calls the same scripts. Both produce a draft PR on `audit/<date>`. Nothing is
merged and no eval runs without the user.

## Files

Paths are relative to `.claude/skills/model-audit/`.

| File                             | Purpose                                                                                                                  |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `scripts/detect.py`              | Stdlib-only, no LLM. Fetches the guide slugs, diffs them against `known-model-guides.json`, lists stale plugins as JSON. |
| `scripts/audit.py`               | Runs the headless audits in parallel, writes `audits/<date>/`, updates each `tuning.json`, validates.                    |
| `assets/config.json`             | `default` model/effort for unpinned audits, `override` pair for pinned tuning and new generations, `jobs`.               |
| `assets/known-model-guides.json` | Every guide slug seen so far. `detect.py --write` adds new ones.                                                         |
| `assets/models-in-use.json`      | Optional. Slugs (`opus-5-5`) or family aliases (`opus` = newest opus guide). Other guides never trigger audits.          |
| `references/filter.md`           | Filter-pass prompt for unpinned files: general-page fixes, defects, and changes that help one model and hurt none.       |
| `references/tune.md`             | Tuning-pass prompt for a pinned agent or skill, from its last tuned guide up to its target.                              |

```bash
python .claude/skills/model-audit/scripts/detect.py [--write]
python .claude/skills/model-audit/scripts/audit.py [--plugins ceh-a ceh-b] [--model M --effort E] \
  [--tune-model M --tune-effort E] [--jobs N] [--apply]
```

`audit.py` needs Claude Code v2.1.283 or later, for `/doctor prompt-audit`, and the bundled
`/claude-api` skill must stay enabled: do not list it in `skillOverrides` or set
`disableBundledSkills`. Every audit is a real model call on your account.

## Per-plugin `.claude-plugin/tuning.json`

`audit.py` creates it on a plugin's first audit. A missing file means nothing has been checked.

```json
{
  "targets": "general",
  "checked-against": [
    "fable-5",
    "fable-5-1",
    "opus-5",
    "opus-5-5",
    "sonnet-5",
    "sonnet-5-5"
  ],
  "pinned": {
    "agents/novice-walker.md": {
      "model": "sonnet-5-5",
      "tuned-for": null,
      "proposed-for": "sonnet-5-5",
      "tuned-by-model": "opus-5-5",
      "tuned-by-model-effort": "high"
    }
  },
  "last-audited": "2026-10-06",
  "audited-with": "claude-code 2.1.291",
  "audit-model": "sonnet-5-5",
  "audit-model-effort": "medium"
}
```

- `checked-against`: guide slugs the unpinned skills were audited against. A plugin is stale when
  this misses an in-use slug.
- `pinned.<path>.model`: the frontmatter `model:` resolved to a guide slug. An alias such as
  `sonnet` resolves to the newest `sonnet-*` guide, so a new Sonnet guide makes the file stale.
  A model with no guide (`haiku` today) keeps its alias and is never tuned.
- `pinned.<path>.tuned-for`: the guide the file was last tuned for. Only the user sets it, after
  accepting a tuning edit. `audit.py` never changes it.
- `pinned.<path>.proposed-for`: the target of the last tuning proposal. A file whose
  `proposed-for` equals its target is not stale again, so an unreviewed or rejected proposal is
  not regenerated every week. `--plugins` forces a new proposal and ignores `checked-against`.
- `audit-model`, `tuned-by-model`: the model that actually ran, read from the run's
  `modelUsage`. `audit-model-effort`, `tuned-by-model-effort`: the `--effort` value passed. The CLI
  output does not report the applied effort, so this is the requested level.

The file passes `claude plugin validate <plugin-dir> --strict`.

## How a plugin is audited

Which guides: each in-use slug brings its same-generation predecessors, because a guide only lists
what changed since the one before it. `opus-5-5` brings `opus-5`, but not `opus-4-8`, which
belongs to an older generation and is treated as superseded. Slugs already in `checked-against`
are skipped.

1. `/doctor prompt-audit plugins/standalone/<plugin>`, saved raw as `<plugin>.doctor.md`.
2. The filter pass (unpinned files) starts from that report, adds anything it missed, and keeps a
   change only when the general page backs it, or a model guide says it benefits that model and
   no other in-use guide says it hurts theirs, or it fixes a missing reference or contradiction.
   Changes written for one model only are left out. General-page techniques are added only
   where the file's task needs them, and where a page disagrees with the `/doctor` report on the
   same instruction, the report wins. The report lists kept changes only.
3. A tuning pass for each stale pinned file, using the `override` pair. It adapts the file to the
   general page and to its model's guides, and model-specific wording is allowed there.
4. `claude plugin validate <plugin-dir> --strict`, then `validate.py` once for the repo.

Model choice: `default` (Sonnet) for unpinned audits, `override` (Opus) for pinned tuning and for
any audit triggered by a new generation, meaning an in-use slug with no minor version such as
`opus-6`. Predecessors pulled in alongside a point release, such as `opus-5`, do not count. To re-run a plugin whose Sonnet report looked weak, use
`--plugins <plugin> --model opus`. Effort levels are those `claude --help` lists
(`low, medium, high, xhigh, max`). Which levels each model honours is not checked here.

Calibrate before trusting the default. Audit the same 2–3 plugins with both models, using
`--plugins ... --model sonnet` and then `--model opus`, and compare the issues Opus finds that
Sonnet misses against the edits Sonnet proposes that you would reject. If they are close, keep
Sonnet. Otherwise change `config.json`.

## Reviewing the PR

`audits/<date>/SUMMARY.md` is the PR body and carries the checklist: keep or drop edits, bump
versions and write the changelog for kept edits, set `tuned-for` for accepted tuning, and optionally
run `claude plugin eval`.
