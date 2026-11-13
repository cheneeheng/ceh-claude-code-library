---
schema: plan/v2
generated_from: workspace-sync-commit-message.yaml
generated_note: "Do not edit. artifact.py renders this file from workspace-sync-commit-message.yaml: edit the YAML, then run artifact.py render."
title: Workspace sync commits follow the commit skill's message rules
status: ready
created: 2026-11-13
---

<!-- prettier-ignore-start -->

## Goal

`sync-agents-workspace.py` commits a linked worktree's workspace with the subject
`ceh-ws: <worktree folder>`. `ceh-ws` is not a type `ceh-git-workflow:commit` allows, and the
subject names a folder, not a change. A script never loads the skill, so the script itself
writes a subject the skill would accept: `chore(workspace): sync worktree <worktree folder>`.

## Scope

**In:**

- `commit()` in `plugins/standalone/ceh-git-workflow/scripts/sync-agents-workspace.py` writes
  the subject `chore(workspace): sync worktree <worktree folder>`, cut to 72 characters.
- The fixture in `tools/validate-plugins/checks/hooks.py` that reads the last subject expects
  the new one.
- The `ceh-git-workflow` README names the subject, with a PATCH bump, changelog entry and
  `docs/PLUGIN_VERSIONS.md` row.

**Out:**

- The branch prefix `ceh-ws/`: It is a branch name, which the commit skill does not govern, and merges depend on it.
- Staging by logical change instead of `git add -A`: The commit is a snapshot of one worktree's session output, which is one logical change for
  a workspace: it is merged back and reverted as a unit. Splitting it needs judgement a
  script does not have.
- An attribution line: The skill takes it from the session's Git instructions and omits it when none is supplied,
  and a hook script is supplied none.
- A body explaining why: The subject says everything a sync commit has to say.
- Rewriting earlier `ceh-ws:` commits: Rewriting workspace history that the remote already holds is a one-way door.
- The daily `agents-workspace-sync: <date>` commits: The user's own scheduler writes them, outside this repo. They break the same rule and are
  left to the user, who was told when this plan was written.
- The merge commits `merge()` makes with `git merge --no-edit`: They keep git's default `Merge branch '<name>'` subject, which every git tool recognises
  as a merge, and the commit skill's types describe changes, not merges.
- A new rule in the commit skill about scripted commits: A script cannot read it, so the rule would have no reader.

## Design

- **The change:** In `commit()`, `git(path, "commit", "-q", "-m", f"ceh-ws: {top.name}")` becomes
  `git(path, "commit", "-q", "-m", f"chore(workspace): sync worktree {top.name}"[:72])`.
  `chore` is the skill's type for maintenance, `workspace` the scope, the summary is
  imperative and lowercase with no trailing period. A folder name with capitals is kept as it
  is, because it is a name. The cut only acts on a folder name over 40 characters and gets no
  fixture of its own, because a slice has no branch to get wrong.
- **The README:** In `plugins/standalone/ceh-git-workflow/README.md`, the "After every turn" bullet gains one
  sentence: "The commit's subject is `chore(workspace): sync worktree <worktree folder>`."
- **Version:** `ceh-git-workflow` goes from 1.5.11, its version on `main` on 2026-11-13, to 1.5.12, or
  the next PATCH above whatever `main` holds when this is built, in `plugin.json`,
  `marketplace.json` and
  `docs/PLUGIN_VERSIONS.md`, with the entry under the PR's dated section of `CHANGELOG.md`.
- **The fixture:** `checks/hooks.py` line 971 compares `git log -1 --format=%s` with `ceh-ws: wt`. It compares
  with `chore(workspace): sync worktree wt` and its failure text says
  `no workspace sync commit`.
- **Order:** This plan is built before `workspace-checkpoint-on-pr-merge` and before phase 2 of
  `consolidate-product-artifacts`, which both add commits to the same script and reuse the
  `chore(workspace):` form.

## Phases

### Phase 1: The sync commit gets a Conventional Commits subject

- **Builds:** The fixture first, seen red on the current script, then the one-line change, the README
  line, the version bump in `plugin.json` and `marketplace.json`, the changelog entry and the
  `docs/PLUGIN_VERSIONS.md` row.
- **Check:** Before the script change, `python tools/validate-plugins/validate.py` fails with
  `no workspace sync commit`. After it, the same command exits 0, and
  `grep -n '"ceh-ws: ' plugins/standalone/ceh-git-workflow/scripts/sync-agents-workspace.py`
  prints nothing. `grep -c "chore(workspace): sync worktree"` prints 1 for the plugin's
  `README.md` and at least 1 for `CHANGELOG.md`, and
  `grep -n "ceh-git-workflow" docs/PLUGIN_VERSIONS.md` shows the new version.
- **Status:** todo

## Open

None

## Record

- 2026-11-13 Planned: status ready
- 2026-11-13 Reviewed: Ready to build, 0 blocking

<!-- prettier-ignore-end -->
