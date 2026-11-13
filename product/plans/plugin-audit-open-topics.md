---
schema: plan/v2
generated_from: plugin-audit-open-topics.yaml
generated_note: "Do not edit. artifact.py renders this file from plugin-audit-open-topics.yaml: edit the YAML, then run artifact.py render."
title: Close the plugin audit topics the user decided on 2026-11-13
status: ready
created: 2026-11-13
---

<!-- prettier-ignore-start -->

## Goal

After `plugin-audit-findings` and `handoff-leftovers` were built, four topics of the 2026-11-11
plugin audit still waited on a choice from the user. The user answered all four on 2026-11-13.
Three answers need a change, and this plan makes them: the usage-limit guard stops telling
every user it is inactive, the install guide says how to raise the skill listing budget, and
the user's own rule about the remote branch agrees with `pull-request`. The flow that matters
most: a person who installed `ceh-every-session` and never set up the usage-limit guard works
a whole session without one line about a guard they did not ask for.

## Scope

**In:**

- `usage-limit-watch.py` prints nothing when no statusline quota export exists, unless the
  user set `CEH_USAGE_LIMIT_THRESHOLD` or `CEH_USAGE_STALE_MINUTES`, or the folder
  `~/.claude/statusline/` exists. In those cases, with no reading to use, it warns once per
  session that the guard is inactive, as today.
- The `ceh-every-session` README, `docs/ENVIRONMENT_VARIABLES.md` and
  `docs/GETTING_STARTED.md` say that the guard needs a statusline export, and that setting
  either variable is what makes a missing export a warning.
- `docs/GETTING_STARTED.md` has a short section that says why a skill can lose its
  description in the listing, how to see it, and how to raise the budget with
  `skillListingBudgetFraction`.
- The user's rule on branches after a merge, in `~/claude-meta/SOUL.md`, says to delete the
  local branch and any leftover worktree, and to delete the branch on origin only where
  GitHub did not already. The answer the rule was learned from, in
  `~/claude-meta/decisions/answered/issue-16.md`, carries a dated note of the change.

**Out:**

- The setup script that raises the listing budget for the user.: It has its own plan, `product/plans/setup-script.yaml`, a draft the user keeps adding
  to. The guide section of Phase 2 covers the time until it exists.
- Setting `skillListingBudgetFraction` on the user's own machine.: The user chose on 2026-11-13 to wait for the setup script.
- Shipping a statusline export script with `ceh-every-session`.: The user chose the quiet guard instead. A person has one statusline setting, so a
  shipped script would have to replace or wrap theirs.
- The cost of listing and sorting `~/.claude/statusline/` on every tool call, the second
  half of the audit's finding.: A user without the export has no such folder and returns at once. A user with it chose
  the guard, and the audit timed the script at 127 ms beside the other hooks, with no
  change needed.
- A change to `pull-request`, or to how the business plan specialists carry their model.: The user chose on 2026-11-13 to keep the skill as it is and reword the rule, and to keep
  the nine model copies and `decision-skill-bundled-files.md` unchanged.
- Moving `ceh-workflow-builder` and `ceh-workflow-runner` out of the repo.: Decided on 2026-11-11 for later, with no date. It gets its own plan when it starts.

## Design

- **Source of the topics** The open topics are listed in the user's workspace, in
  `.agents_workspace/plugin-audit/20261113-200012-76712160-e57c-4eac-8049-56902048bf82-open-topics.md`,
  which is not committed, so this plan restates each one it closes. The audit's numbers for
  them: finding 9 of the `ceh-every-session` report (the notice), SUMMARY 3.1 (the listing
  budget), and SUMMARY 3.7 with finding 2a of the `ceh-git-workflow` report (the remote
  branch).
- **Phase 1: when the guard speaks** In `main()` of `plugins/standalone/ceh-every-session/scripts/usage-limit-watch.py`, the
  branch `if reading is None:` calls `warn_once` only when
  `"CEH_USAGE_LIMIT_THRESHOLD" in os.environ or "CEH_USAGE_STALE_MINUTES" in os.environ`,
  or when `(Path.home() / ".claude" / "statusline").is_dir()`, and returns either way. The
  warning text is unchanged. The reason, written as the comment on that branch: a user who
  set a guard variable or has an export folder expects the guard to work, so a missing or
  broken export must not look like protection, and a user with neither never asked for the
  guard. The folder test covers an export that exists and holds no quota record, where
  `latest_reading()` also returns `None`. The stale-reading warning stays as it is, because
  a stale reading means an export exists, so that user set the guard up. No new variable is
  added: the two that exist are the opt-in, and a value equal to the default counts, since
  setting it is the act. The module docstring's Prerequisite paragraph, which says the hook
  "warns once per session rather than failing silently", is reworded to say the same.
- **Phase 1: the texts that describe it**
  - `plugins/standalone/ceh-every-session/README.md`, the Prerequisite note under
    "Usage-limit guard": "Without the export the guard warns once per session that it is
    inactive, rather than failing silently" becomes: without the export the guard does
    nothing and says nothing, unless `CEH_USAGE_LIMIT_THRESHOLD` or
    `CEH_USAGE_STALE_MINUTES` is set or the export folder exists, in which case it warns
    once per session that it is inactive. The sentence after it, on stale readings, loses
    "for the same reason", which pointed at the clause this edit removes, and keeps its
    own reason.
  - The same README's table of guards, where the usage-limit guard's Default reads `on`:
    the row says the guard acts only once a statusline export feeds it.
  - `docs/GETTING_STARTED.md`, the `ceh-every-session` row of the core table: "a
    usage-limit guard" becomes "a usage-limit guard once a statusline export feeds it".
  - `docs/ENVIRONMENT_VARIABLES.md`: the Effect cell of both variables gains "Setting it
    also makes a missing statusline export a once-per-session warning."

  The kill-switch block at the top of `main()` is a copy registered in
  `docs/CROSS_REFERENCES.md` and is not touched.
- **Phase 1: fixtures** In `tools/validate-plugins/checks/hooks.py`, the fixture that runs `usage-limit-watch.py`
  with `home("home-empty")` and expects exit 1 and `INACTIVE` becomes three, and the
  comment above them is reworded to match:

  - The same run with no guard variable, written as `"out": ""` with no `code` key, so the
    runner expects exit 0. The warning goes to stderr, so the exit code, 1 before the
    script edit and 0 after it, is what fails and then passes.
  - The run with `CEH_USAGE_LIMIT_THRESHOLD` set to `90`: `"code": 1, "err": "INACTIVE"`.
  - A run with a new home folder that holds an empty `.claude/statusline/` and no guard
    variable: `"code": 1, "err": "INACTIVE"`.

  The first is written before the script edit and seen failing. The runner's `base_env`
  already strips every `CEH_*` variable of the builder's own environment, and a fixture's
  `env` only adds keys, so the quiet fixture does not depend on the machine.
- **Phase 2: the guide section** A new section in `docs/GETTING_STARTED.md`, after "5. Check it worked", titled
  "If a skill stops triggering, raise the listing budget". The heading carries no number,
  because the guide calls steps 1 to 5 the install route and tells Claude to follow steps 1
  to 4, and this section is not a step of that route. It says, in this order:

  - Claude Code lists every skill's name and description so it can match a request to a
    skill. The listing has a budget of 1% of the model's context window. Over it, Claude
    Code keeps every name and drops descriptions, starting with the skills invoked least,
    and a skill without its description is not matched to a request.
  - How to see it: `/doctor` estimates the listing's cost, and `/skill-doctor` (Claude Code
    v2.1.252 or later) shows what each skill costs and how often it is used.
  - The fix, as a JSON block for `~/.claude/settings.json`:
    `"skillListingBudgetFraction": 0.02`, which is 2%. One sentence names the other route:
    set a rarely used skill to `"name-only"` in `skillOverrides`.

  The section does not mention the setup script, which is an undated draft. That plan adds
  its own line when the script ships. Every statement was checked on 2026-11-13 against "Skill descriptions are cut short" on
  https://code.claude.com/docs/en/skills, and the section links to that page. The block for
  Claude Code at the top of the guide is not changed: an agent running the setup does not
  edit the user's settings, which is the setup script's job. Only `docs/` changes, so no
  plugin version changes.
- **Phase 3: the reworded rule** `~/claude-meta/SOUL.md` is the user's own always-loaded rule file, in the user's own
  repository, outside this one. Under "Scope" it holds one rule that starts "When a PR has
  merged". Its "prefer" clause becomes: prefer deleting its local branch and any leftover
  worktree without asking, and deleting the branch on origin only where GitHub did not
  already delete it. Its "because" clause keeps what it has and gains one reason: that
  `ceh-git-workflow:pull-request` leaves remote cleanup to the repository's "Automatically
  delete head branches" setting. The rule stays one sentence, in the file's
  "When ..., prefer ..., because ..." form.

  How an agent tells the two cases apart is not written into the rule, because it is one
  command: `git ls-remote --exit-code --heads origin <branch>` exits 2 when the branch is
  gone. Where it is still there, `git push origin --delete <branch>` removes it, run as its
  own command after the merge, which the permission classifier does not block as it blocks
  `--delete-branch` on the merge command.

  That repository also keeps the answer the rule was learned from, in
  `decisions/answered/issue-16.md`, and a weekly lessons job there rewrites parts of
  `SOUL.md`. So the same commit appends a note to that file, under a new heading
  `### Amended <date>` after its last section: the rule in `SOUL.md` was reworded on that
  date, what it says now, and why, naming `ceh-git-workflow:pull-request` and the GitHub
  setting. The file's existing lines stay as they are. The note goes into the local file
  only, never as a comment on the GitHub issue, which the rule file forbids. The user chose
  this on 2026-11-13, so the answer and the rule are read together and a later reader, or
  the weekly job, sees that the rule was changed on purpose. The builder does not need to
  read the weekly job first.

  The two edits are one commit in that repository with the subject prefix `soul:`, as its
  history has for an earlier hand edit, and the builder pushes it to that repository's
  remote, which the user approved on 2026-11-13. Nothing in this repository changes but
  this plan's record.
- **Versions and landing** Phase 1 is one PR: a PATCH bump of `ceh-every-session` in `plugin.json`,
  `marketplace.json` and `docs/PLUGIN_VERSIONS.md`, from whatever `main` holds when it is
  built (2.9.15 on 2026-11-13), with its `CHANGELOG.md` entry under the PR's dated section.
  Phase 2 is one PR with a `CHANGELOG.md` entry and no version change. Phase 3 has no PR
  here.

## Phases

### Phase 1: The usage-limit guard is quiet without the export

- **Builds:** "Phase 1: fixtures" first, with the quiet fixture seen failing. Then "Phase 1: when the
  guard speaks" and "Phase 1: the texts that describe it", with the bump under "Versions
  and landing".
- **Check:** `python tools/validate-plugins/validate.py` fails on the quiet fixture before the script
  edit and prints `OK: all plugin checks passed` after it.
  `git grep -n "rather than failing silently" -- plugins/standalone/ceh-every-session`
  and
  `git grep -n "warns once per session rather than" -- plugins/standalone/ceh-every-session/scripts`
  each print nothing, the second because the docstring splits the phrase over two lines.
  `git grep -c "once-per-session warning" -- docs/ENVIRONMENT_VARIABLES.md` prints a count
  of 2, and
  `git grep -c "once a statusline export feeds it" -- docs/GETTING_STARTED.md` a count of 1.
- **Status:** todo

### Phase 2: The install guide says how to raise the listing budget

- **Builds:** "Phase 2: the guide section", with its `CHANGELOG.md` entry.
- **Check:** `git grep -c "skillListingBudgetFraction" -- docs/GETTING_STARTED.md` prints a count of
  at least 1,
  `git grep -n "^## If a skill stops triggering" -- docs/GETTING_STARTED.md` shows the new
  heading, `git grep -n "^## 6" -- docs/GETTING_STARTED.md` prints nothing, and
  `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`.
- **Status:** todo

### Phase 3: The user's branch rule agrees with pull-request

- **Builds:** "Phase 3: the reworded rule".
- **Check:** `grep -c "When a PR has merged" ~/claude-meta/SOUL.md` prints 1, and that line holds
  "only where GitHub did not already" and no longer holds "both locally and on origin".
  `grep -c "^### Amended" ~/claude-meta/decisions/answered/issue-16.md` prints 1.
  `git -C ~/claude-meta log -1 --format=%s -- SOUL.md` shows the `soul:` commit, and
  `git -C ~/claude-meta status -sb` shows the branch not ahead of its remote. No command
  in this repository proves it, because the files live outside it.
- **Status:** todo

## Open

- Does the weekly lessons job in `~/claude-meta` read the note in
  `decisions/answered/issue-16.md`, or could it still put the old wording back?: Not checked. The user chose the note as the record on 2026-11-13. If a later weekly run
  restores the old rule, the note shows the change was made on purpose, and the fix is
  then in that job, which is the user's own tool.

## Record

- 2026-11-13 Planned: status ready
- 2026-11-13 Reviewed: Ready to build, 0 blocking. All eight advisory findings fixed in the plan the same day,
  among them a warning kept for an export folder that holds no quota record, and the
  guide section's heading left unnumbered.
- 2026-11-13 PR: #282 https://github.com/cheneeheng/ceh-claude-code-library/pull/282
- 2026-11-13 Design changed: was "The edit is one commit in that repository with the subject prefix `soul:`", now
  the same commit also appends an `### Amended <date>` note to
  `decisions/answered/issue-16.md` and is pushed, because the user asked on 2026-11-13
  for the note beside the answer the rule was learned from, and approved the push. The
  user also confirmed that the guard warns when the export folder exists and holds no
  quota record, which Phase 1 already says. Both answered questions leave Open.
- 2026-11-13 PR: #283 https://github.com/cheneeheng/ceh-claude-code-library/pull/283

<!-- prettier-ignore-end -->
