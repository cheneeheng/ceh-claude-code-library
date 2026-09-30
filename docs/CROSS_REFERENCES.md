# Cross-Reference Map

Tracks content duplicated word-for-word across multiple skills. When editing any entry,
update **all listed files**. Each block is intentionally inlined (zero file reads at runtime);
this map exists so edits don't get lost.

Add an entry when a migrated or new skill duplicates content from another, using the shape at the
bottom of this file.

## Auto-merge probe + enable (gh pr merge --auto)

**Canonical:** `plugins/ceh-git-workflow/skills/merge/SKILL.md` — § PR merge & cleanup

| Copy                                               | Section                                                            | Diverges                                                                                  |
| -------------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| `plugins/ceh-git-workflow/skills/open-pr/SKILL.md` | § Auto-merge + the `gh pr merge --auto` tail of § Procedure step 2 | Runs only the probe-and-enable half, right after `gh pr create`; no direct-merge fallback |

**Shared:** the `allow_auto_merge` probe (`gh api repos/{owner}/{repo} --jq .allow_auto_merge`)
guarding `gh pr merge --merge --auto`, the ban on `--delete-branch` (the permission classifier
blocks the whole command), and the `delete_branch_on_merge` check that tells the user whether the
remote branch survives. `merge` alone owns the direct-merge fallback and the "Reporting the remote
branch" wording. `release-flow` step 9 and `merge-flow` step 6 name the same `--auto` behavior but
delegate to `merge` — keep their wording consistent if the probe changes.

## PR checklist items

**Canonical:** `plugins/ceh-git-workflow/skills/open-pr/SKILL.md` — § PR description template

| Copy                                               | Section                                 | Diverges |
| -------------------------------------------------- | --------------------------------------- | -------- |
| `plugins/ceh-git-workflow/skills/open-pr/SKILL.md` | § Procedure step 2 (`body.md` template) | none     |

**Shared:** the seven checklist items, word-for-word: "All CI checks pass", "Tests added or updated
for new behavior", "No `any` / `@ts-ignore` / `# type: ignore` introduced", "No secrets or
credentials in code", "Migrations (if any) are backward-compatible", "ARCHITECTURE.md Key Decisions
updated (if a durable decision was made)", "Attribution included if AI tooling assisted".

## Coverage targets

**Canonical:** `plugins/ceh-git-workflow/skills/open-pr/SKILL.md` — § Coverage targets

| Copy                                   | Section | Diverges |
| -------------------------------------- | ------- | -------- |
| none yet in this repo — see note below |         |          |

**Shared:** `Python application package | 80%`, `Core business logic / domain services | 95%`.
In agent-skills the `python-service-testing` and `python-library-testing` skills carry these two
rows word-for-word (without the TypeScript row). Add them here as copies when `ceh-python-service`
and `ceh-python-library` migrate.

## Hotfix workflow

**Canonical:** `plugins/ceh-git-workflow/skills/hotfix/SKILL.md` — entire file

| Copy                                   | Section | Diverges |
| -------------------------------------- | ------- | -------- |
| none yet in this repo — see note below |         |          |

**Shared:** the 7-step process: branch `fix/critical-<description>` from `main`, minimal scope,
1-approval review, CI must pass, merge commit to `main`, bump PATCH + tag, staging → production.
In agent-skills `ceh-ops:incidents` carries the same steps without commands. Add it here as a copy
when `ceh-ops` migrates.

## Semver bump mapping

**Canonical:** `plugins/ceh-git-workflow/skills/release/SKILL.md` — bump table under the title

| Copy                                                        | Section                                          | Diverges                                                                          |
| ----------------------------------------------------------- | ------------------------------------------------ | --------------------------------------------------------------------------------- |
| `plugins/ceh-git-workflow/skills/release-flow/SKILL.md`     | § Procedure, pipeline step 1 cell                | Condensed into one cell; "Never lower a version" lives in the gate column instead |
| `plugins/ceh-git-workflow/skills/update-changelog/SKILL.md` | § Procedure, 2. Determine version and categorize | Keyed off commit prefixes, adds the Keep a Changelog section per level            |

**Shared:** breaking change → MAJOR, new backward-compatible feature → MINOR,
fixes/chores/docs/refactors → PATCH, and "when in doubt, PATCH". `release-flow` inlines this rather
than invoking `release` at step 1, because invocation injects the whole body, including the
push-and-tag sequence nine steps early.

## Release-commit message rule

**Canonical:** `plugins/ceh-git-workflow/skills/release-flow/SKILL.md` — § Step 7 detail

| Copy                                               | Section                     | Diverges                                          |
| -------------------------------------------------- | --------------------------- | ------------------------------------------------- |
| `plugins/ceh-git-workflow/skills/release/SKILL.md` | § Procedure, step 1 comment | Same intent, own wording: always multi-line, `-F` |

**Shared:** the version-bump commit is never subject-only: it carries what shipped, the bump level
and its reason, and the attribution footer, committed with `git commit -F`.

## Write-less-code ladder (skill + per-turn digest)

**Canonical:** `plugins/ceh-coding-agent/skills/write-less-code/SKILL.md` — § Procedure + § When not to be lazy

| Copy                                                    | Section                  | Diverges                                                                                |
| ------------------------------------------------------- | ------------------------ | --------------------------------------------------------------------------------------- |
| `plugins/ceh-coding-agent/scripts/less-code-payload.sh` | `additionalContext` text | compact digest of the ladder and the never-simplify list, injected per turn by the hook |

**Shared:** the six-rung ladder (YAGNI → stdlib → native platform feature → already-installed
dependency → one line → minimum that works) and the never-simplify-away list (trust-boundary
validation, data-loss handling, security, accessibility, anything explicitly requested). The
retroactive ladder below re-frames the same six rungs, so a rung change propagates there too.

## Retroactive ladder + behavior preservation

**Canonical:** `plugins/ceh-coding-agent/skills/shrink-diff/SKILL.md` — § The retroactive ladder + § Behavior preservation

| Copy                                                     | Section                                            | Diverges                                                                          |
| -------------------------------------------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------- |
| `plugins/ceh-coding-agent/skills/refactor-repo/SKILL.md` | § The retroactive ladder + § Behavior preservation | none in the text; applied per approved cluster rather than to the branch seed set |

**Shared:** both blocks word for word — the six retroactive rungs, and the behavior-preservation
bullets (no behavior change in a refactor, tests before and after, mechanical transforms only
without coverage, pin behavior with `ceh-testing:verify-behavior-preserved`, `refactor:` commits).

## Explanation honesty rules

**Canonical:** `plugins/ceh-coding-agent/skills/explain-codebase/SKILL.md` — § Rules

| Copy                                                                | Section | Diverges                                                                                 |
| ------------------------------------------------------------------- | ------- | ---------------------------------------------------------------------------------------- |
| `plugins/ceh-coding-agent/skills/explain-until-understood/SKILL.md` | § Rules | carries only the three rules that hold for a spoken explanation, not the file-bound ones |

**Shared:** three bullets word for word — "Evidence over inference", "Don't paste code" (with the
verbatim-literal exception), and "Describe what exists today".

## Bulk-read guard exemption list (`ALWAYS_ALLOW`)

**Canonical:** `plugins/ceh-coding-agent/scripts/bulk-read-guard.py` — `ALWAYS_ALLOW` tuple

| Copy                                                       | Section              | Diverges |
| ---------------------------------------------------------- | -------------------- | -------- |
| `plugins/ceh-coding-agent/scripts/bulk-read-bash-guard.py` | `ALWAYS_ALLOW` tuple | none     |

**Shared:** the glob tuple, verbatim. The two guards cover the same files by two routes (`Read` and
`cat`/`head`), so a pattern in one and not the other denies a file on one route and allows it on
the other. Each hook is a standalone script with no shared module, so the list is duplicated.

## Bulk-reader answer format (Answer / Not found / Coverage)

**Canonical:** `plugins/ceh-coding-agent/agents/bulk-reader.md` — § Output to parent session

| Copy                                                           | Section                            | Diverges                                                                            |
| -------------------------------------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------- |
| `plugins/ceh-coding-agent/skills/delegate-bulk-reads/SKILL.md` | § Trust the anchors, not the prose | names the sections only and carries the caller-side verification rules, no template |

**Shared:** the three fixed sections and their order — `## Answer` (every claim anchored
`path:line`), `## Not found / uncertain` (never omitted, `- Nothing outstanding.` when clean),
`## Coverage` (lines read per file, then the sum).

---

Entry shape:

```markdown
## <Shared block name>

**Canonical:** `plugins/ceh-<plugin>/skills/<skill>/SKILL.md` — § <section>

| Copy                                           | Section     | Diverges                               |
| ---------------------------------------------- | ----------- | -------------------------------------- |
| `plugins/ceh-<plugin>/skills/<skill>/SKILL.md` | § <section> | <what deliberately differs, or "none"> |

**Shared:** <what must stay identical across every copy>.
```
