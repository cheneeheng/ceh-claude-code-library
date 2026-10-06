---
name: model-audit
description: >-
  Audit this repo's ceh-* plugins against Claude's per-model prompting guides and hand the results
  over as a draft PR. Runs the detector, a headless /doctor prompt-audit per stale plugin, the
  pinned-agent tuning passes, strict validation, then commits to audit/<date> and opens the PR.
  User-invoked only, because every audit is a billed model call.
argument-hint: "[--plugins plugins/standalone/ceh-a ...] [--model M --effort E] [--tune-model M --tune-effort E] [--apply]"
disable-model-invocation: true
user-invocable: true
license: Apache-2.0
---

# Model audit

Every step below runs inside this skill. The user reviews the draft PR and nothing else. The
scripts and their state files are documented in `${CLAUDE_SKILL_DIR}/README.md`.

Arguments: `$ARGUMENTS`. Pass them through to `audit.py` unchanged. `--plugins` audits the given
plugins even when they are not stale, each as its path from the repo root, and `--model`/`--effort` override the default audit pair in
`${CLAUDE_SKILL_DIR}/assets/config.json`. What each argument does is in the README's Arguments
section.

## 1. Branch

The working tree must be clean apart from untracked files. If it is not, stop and say so. From
`main`, create `audit/<YYYY-MM-DD>` with today's date. On another branch, ask before continuing.

## 2. Detect

```bash
python "${CLAUDE_SKILL_DIR}/scripts/detect.py" --write
```

It prints JSON. If `stale` is empty and `--plugins` was not passed, report "nothing stale",
delete the branch you created, and stop. Otherwise tell the user which plugins are stale and how
many runs that makes: two per plugin with missing guides (`/doctor` plus the filter pass), plus
one per pinned file with `"stale": true`.

## 3. Audit

```bash
python "${CLAUDE_SKILL_DIR}/scripts/audit.py" $ARGUMENTS
```

Run it in the background and wait for it to exit. It can take a long time. Do not read the
per-plugin reports into this session. Read only `audits/<date>/SUMMARY.md`. A non-zero exit means
a plugin errored or failed validation: the summary says which. Carry on to the PR anyway, so the
failure is reviewed with everything else.

## 4. Hand off

Stage `${CLAUDE_SKILL_DIR}/assets/known-model-guides.json`, `audits/`, and `plugins/`, then commit with
the message `chore(model-audit): audit reports for <date>` plus the attribution line. If the
pre-commit hook reformats files and aborts, stage them again and commit again. Then push and open
the draft PR, chaining with `&&`:

```bash
git push -u origin audit/<date> && gh pr create --draft --title "chore(model-audit): audit <date>" --body-file <body>
```

`<body>` is a scratch copy of `SUMMARY.md` with the PR attribution line appended. Do not bump
versions or write the changelog here: which edits survive is the user's decision, and the
summary's reviewer checklist covers both.

Reply with the PR URL, the summary table, any errors or validation failures, and the next steps
below, trimmed to what this run needs: drop the pinned-tuning step when nothing was tuned, the
version steps when no edit was kept.

## 5. Next steps for the user

1. **Review the reports.** Read each `audits/<date>/<plugin>.md` and check that every kept change
   cites a guide that actually backs it. `<plugin>.doctor.md` is the raw `/doctor` output it
   started from.
2. **Keep or drop edits.** With `--apply`, revert the hunks under `plugins/` you reject. Without
   it, apply the ones you keep by hand before merging: `tuning.json` already records the guides as
   checked, so the next run will not propose them again.
3. **Accept or reject pinned tuning.** For each accepted file, set `tuned-for` to its `model` in
   the plugin's `tuning.json`. For a rejected one, revert the edit and leave `tuned-for` alone:
   `proposed-for` stops the same proposal from coming back.
4. **Mirror shared content.** If a kept edit touches a section listed in
   `docs/CROSS_REFERENCES.md`, apply it to every copy in the same PR.
5. **Bump versions.** Each plugin with a kept edit gets a PATCH bump in both its `plugin.json` and
   `.claude-plugin/marketplace.json`, and its `docs/PLUGIN_VERSIONS.md` row. A plugin whose only
   change is `tuning.json` gets none.
6. **Changelog.** Add the PR's entry under the date it was opened, per the root `CLAUDE.md`
   Versioning section, with a `### Plugin versions` table if anything was bumped.
7. **Handle failures.** For an errored plugin or a failed validation, fix the cause, then re-run
   `/model-audit --plugins <plugin-path>`. A report that looks weak can be re-run with
   `--model opus`.
8. **Verify and merge.** Run `python tools/validate-plugins/validate.py`, optionally
   `claude plugin eval` from a plugin root, tick the PR checklist, mark it ready, and merge with a
   merge commit per the root `CLAUDE.md` "Landing a branch".
