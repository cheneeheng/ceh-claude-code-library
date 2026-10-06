---
name: model-audit
description: >-
  Audit this repo's ceh-* plugins against Claude's per-model prompting guides and hand the results
  over as a draft PR. Runs the detector, a headless /doctor prompt-audit per stale plugin, the
  pinned-agent tuning passes, strict validation, then commits to audit/<date> and opens the PR.
  User-invoked only, because every audit is a billed model call.
argument-hint: "[--plugins ceh-a ceh-b] [--model M --effort E] [--tune-model M --tune-effort E] [--apply]"
disable-model-invocation: true
user-invocable: true
license: Apache-2.0
---

# Model audit

Every step below runs inside this skill. The user reviews the draft PR and nothing else. The
scripts and their state files are documented in `${CLAUDE_SKILL_DIR}/README.md`.

Arguments: `$ARGUMENTS`. Pass them through to `audit.py` unchanged. `--plugins` audits the named
plugins even when they are not stale, and `--model`/`--effort` override the default audit pair in
`${CLAUDE_SKILL_DIR}/assets/config.json`.

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

Reply with the PR URL, the summary table, and any errors or validation failures.
