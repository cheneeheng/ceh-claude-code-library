---
schema: plan/v1
title: Deny a write whose owning skill was never started, in ceh-git-workflow, ceh-testing and ceh-coding-conduct
status: building
created: 2026-10-28
---

## Goal

Apply the drafted fix in `product/retros/2026-10-28-repeat-mistake.md`, so the misses of the
mcp-cassette session b5d9c329 do not repeat. An agent that runs `git commit`, edits a
`CHANGELOG.md` or `README.md`, writes a test file, or writes a new source file without having
started a skill that owns that moment is denied, and told which skill to invoke first. A skill that
another skill's steps only name ("following X") no longer gets followed from memory.

## Scope

**In:**

- `ceh-git-workflow` denies a Bash `git commit` until `ceh-git-workflow:commit` was started, an
  Edit, Write, or MultiEdit of a `CHANGELOG.md` until `update-changelog` or `release` was, and of a
  `README.md` until `update-readme` was.
- `ceh-testing` denies an Edit, Write, or MultiEdit of a test file (`test_*.py`, `*_test.py`,
  `*.test.*` or `*.spec.*` in JS or TS) until `write-test-first`, `test-a-bug-fix`,
  `verify-behavior-preserved`, or a stack test skill (`ceh-python-library:write-pytest-library-tests`,
  `ceh-python-service:write-pytest-service-tests`, `ceh-web-frontend:write-vitest-playwright-tests`)
  was started.
- `ceh-coding-conduct` denies a Write that creates a new `.py`, `.ts`, `.tsx`, or `.js` file outside
  a tests or `scripts/` folder until `ceh-coding-conduct:sketch-design` was started.
- A file outside the session's project (a scratch file) is never denied.
- `CEH_SKILL_STARTED_GUARD=off` and `CEH_DISABLED_HOOKS=skill-started-guard` turn the guard off in
  every plugin that ships it.
- The retro file marks the fix `applied`.

**Out:**

- The retro's keep-or-merge recommendations for the five skills: the user asked for the guard
  only, and each retirement is its own decision.
- A row for any other moment, such as a branch creation: the 2026-10-18 branch gate was rejected,
  and this fix covers the five measured misses only.
- A denial counter like `branch-guard.py`'s: the guard allows the call as soon as the skill is
  started, so one Skill call ends any loop.
- Subagents loading a skill their parent loaded: a subagent's transcript is its own, so it must
  start the skill itself, which is the rule either way.

## Design

- One script, `scripts/skill-started-guard.py`, copied into each of the three plugins with only
  that plugin's rows in `RULES`, so each plugin works installed alone. The body outside `RULES` is
  identical in all three and registered in `docs/CROSS_REFERENCES.md`, canonical in
  `ceh-git-workflow`. The script is the retro's draft, with `sys.exit(0)` after the fail-open as in
  `build-record-guard.py`.
- Each plugin's `hooks/hooks.json` runs it on `PreToolUse` with matcher `Bash|Edit|Write|MultiEdit`
  (`Edit|Write|MultiEdit` in `ceh-testing`, `Write` in `ceh-coding-conduct`, since their rules never
  match a Bash call), timeout 10. `ceh-testing` gets its first `hooks/` and `scripts/` folders.
- A skill counts as started only by its `Skill` tool call or its slash command in the transcript,
  never a mention, the same two records `build-record-guard.py` matches.
- The commit rule matches `git` at the start of a command or after `;`, `&`, `|`, or `(`, with any
  `-C <dir>` or `-c <k=v>` before `commit`, so `cd x && git -C y commit` is caught and
  `grep "git commit" f` is not.
- The new-source rule skips `scripts/` folders as well as tests: a script there is run, not called
  by other code, so it has no interface for `sketch-design` to sketch.
- The `ceh-testing` and `ceh-coding-conduct` READMEs say the new hook needs `python3`, as their
  existing scripts needed none.
- The root `CLAUDE.md` Landing section's changelog bullet changes from "do not run
  `update-changelog` in Unreleased mode" to "start `update-changelog` and write the entry in this
  repo's dated format", so it no longer contradicts the guard.
- `skill-started-guard.py` joins `NAMES_TO_DETECT` in `tools/validate-plugins/checks/repo_rules.py`,
  and `plugins/CLAUDE.md` names it beside `build-record-guard.py`: it names skills only to detect
  them, and each must keep its slash command.
- `tools/validate-plugins/checks/hooks.py` keys hook scripts by `<plugin>/<script>` as well as by
  name, so three copies with one name each get their own fixtures. A fixture naming a bare script
  name that more than one plugin ships fails as ambiguous, and the missing-fixture check compares
  script paths, not names.
- The replay check runs on this machine only, against
  `<home>/.claude/projects/<project>/b5d9c329-bbd8-4ddb-8cd4-b909aa41ff82.jsonl` cut to its first
  2476 lines (line 2477 starts `test-a-bug-fix`), with payloads piped into each copy of the script.
- Three PRs, one per plugin, each a MINOR bump, as a new hook was for `ceh-build-from-plan`.

## Phases

### Phase 1: ceh-git-workflow guard

- **Builds:** the `hooks.py` keying change, `ceh-git-workflow`'s script and hook entry, the
  `NAMES_TO_DETECT` entry and `plugins/CLAUDE.md` sentence, fixtures (deny `git commit`, a
  `CHANGELOG.md` edit and a `README.md` write without the skill; allow each after its `Skill` call;
  allow `CHANGELOG.md` after `release`; allow after a slash command; deny `cd x && git -C y commit`;
  allow `git status` and `grep "git commit" f`; allow a `README.md` outside the project; allow with
  each off switch), the `CEH_SKILL_STARTED_GUARD` row and the `CEH_DISABLED_HOOKS` row in
  `docs/ENVIRONMENT_VARIABLES.md`, the `docs/CROSS_REFERENCES.md` entry and kill-switch table row,
  the root `CLAUDE.md` Landing bullet, the plugin README row, the MINOR bump, changelog and
  versions rows, and commit the retro with this plan.
- **Check:** the new fixtures fail before the script exists and pass after, `validate.py` shows no
  failure outside `docs/starlight/node_modules/`, and the session b5d9c329 transcript, cut before
  `test-a-bug-fix` was loaded, gets a deny for `git commit`, `Edit CHANGELOG.md` and
  `Write README.md`.
- **Status:** done. The 14 fixtures failed first ("no hooks.json runs this script") and pass now
  ("OK: hooks check passed"); the cut transcript gets a deny for all three calls and none for
  `git status`. `validate.py`'s only failures are git-ignored files (`docs/starlight/node_modules/`,
  `evals/results/`). The `docs/CROSS_REFERENCES.md` whole-script entry moves to Phase 2, where its
  first copy exists; this phase adds only the kill-switch table row.

### Phase 2: ceh-testing guard

- **Builds:** `ceh-testing`'s script, its new `hooks/hooks.json`, fixtures (deny a test-file write
  without the skill; allow after each owning skill's `Skill` call; allow a non-test file; allow a
  test file outside the project; allow with each off switch), `ceh-testing` added to the
  `CEH_SKILL_STARTED_GUARD` and `CEH_DISABLED_HOOKS` rows and the cross-reference entries, the
  plugin README row and `python3` note, the MINOR bump, changelog and versions rows.
- **Check:** the fixtures fail first and pass after, `validate.py` as in Phase 1, and the cut
  transcript gets a deny for `Write tests/integration/test_check.py`.
- **Status:** done. The 12 fixtures failed first ("no hooks.json runs this script") and pass now
  ("OK: hooks check passed"); the cut transcript gets a deny for the `test_check.py` write; the body
  outside `RULES` matches `ceh-git-workflow`'s copy; `validate.py` fails only on git-ignored files.

### Phase 3: ceh-coding-conduct guard

- **Builds:** `ceh-coding-conduct`'s script and hook entry, fixtures (deny a new source file
  without `sketch-design`; allow after it; allow an existing file; allow a new file under
  `tests/` or `scripts/`; allow a new file outside the project; allow with each off switch), the
  plugin added to the same doc rows, the plugin README row and `python3` note, the MINOR bump,
  changelog and versions rows, and the retro row set to `applied`.
- **Check:** the fixtures fail first and pass after, `validate.py` as in Phase 1, and the cut
  transcript gets a deny for a Write of a new `src/mcp_cassette/check_new.py`.
- **Status:** todo

## Open

- The test-file rule also fires on a one-line fixture tweak to an existing test. Assumed
  acceptable, softened by accepting `verify-behavior-preserved`, per the retro.
- The new-source rule also fires on a new one-off module outside `scripts/`, such as a config
  loader. Assumed acceptable: starting `sketch-design` costs one call.
- A subagent's hook reads its own transcript, assumed as in `skill-loading-guards.md`.

## Record

- 2026-10-28 Planned: status ready
- 2026-10-28 Reviewed: Ready to build, 0 blocking
- 2026-10-28 Built Phase 1: `python tools/validate-plugins/checks/hooks.py`, OK: hooks check passed
- 2026-10-28 PR: #173 https://github.com/cheneeheng/ceh-claude-code-library/pull/173
- 2026-10-28 Built Phase 2: `python tools/validate-plugins/checks/hooks.py`, OK: hooks check passed
