---
title: Move lifecycle files to product/, and keep build plans as the audit trail of each change
status: built
created: 2026-10-11
---

## Goal

Make the build plan the one committed record of how a change went from idea to merge: what was
planned, how it was reviewed, how each phase was built and proven, how the build compared with
the plan, what evidence covered it, and which PR landed it. A reader who opens
`product/plans/<slug>.md` years later traces the whole change from that file alone, without
digging through git history. `product/EVIDENCE.md` keeps every run, so the evidence a plan cites
still reads the same later. All the files the lifecycle writes for the people and agents building
the product move to one `product/` folder, so `docs/` holds only what users of the product read.

## Scope

**In:**

- The lifecycle's committed files live in `product/`: `BUSINESS_PLAN.md`, `INVESTOR_DECK.md`,
  `INVESTOR_OUTREACH.md`, `ARCHITECTURE.md`, `EVIDENCE.md`, and `plans/<slug>.md`. `docs/` is left
  to user docs.
- Plans are never deleted. A built plan stays at `product/plans/<slug>.md` with `status: built`.
- Every plan ends with an append-only `## Record` section: one dated line per lifecycle event,
  never edited or removed.
- `write-build-plan` adds a Planned entry, `review-build-plan` adds a Reviewed entry,
  `implement-from-plan` adds a Built entry per phase and a Design changed entry per departure,
  `check-build-against-plan` adds a Checked entry, `write-evidence-report` adds an Evidence entry,
  and `pull-request` adds a PR entry.
- A Design change keeps the original decision: the Record entry quotes what it was, what it is
  now, and why.
- Planning stays cheap: `write-build-plan` reads only the frontmatter of `built` plans, and their
  full text only when the new work touches what they built.
- `product/EVIDENCE.md` becomes append-only: each run adds a dated section at the top, and
  earlier sections are never edited. Readers use the newest section.

**Out:**

- A fallback to the old paths (`docs/plans/`, `docs/EVIDENCE.md`, `docs/ARCHITECTURE.md`, root
  `BUSINESS_PLAN.md`). Skills look only in `product/`. A repo with files at the old paths moves
  them once with `git mv`, as the changelog entry says. A shim would stay in every skill forever,
  and a repo can still name another folder in its `CLAUDE.md`. The one exception predates this
  plan: `document-architecture` keeps its one-time move of a legacy
  `.agents_workspace/ARCHITECTURE.md`. (Decided by the user, 2026-10-11.)
- Committing QA, performance, or usability reports. They stay in `.agents_workspace/`, and
  `EVIDENCE.md` keeps carrying their figures. (Decided by the user, 2026-10-11.)
- Committing security audits. A committed audit of open vulnerabilities publishes them.
- Moving `.claude/rules/`, `GLOSSARY.md`, `CHANGELOG.md`, or `README.md`. Claude Code loads
  `.claude/rules/` from its path, and the other three are conventional files users read.
- Restoring plans deleted before this change. They stay in git history.
- A validator or hook that enforces the Record. Principle 7 asks for evidence that the prose fails
  first.
- Moving built plans to a subfolder. It would break every path that cites a plan: `derived_from`,
  PR bodies, changelog entries. (Decided by the user, 2026-10-11.)
- This library's own `docs/`, which mixes maintainer files (`VISION.md`, `STRATEGY.md`, `IDEAS.md`,
  `PLUGIN_VERSIONS.md`) with `GETTING_STARTED.md`. That is a separate change.
- `ceh-workflow-builder/docs/ARCHITECTURE.md`, which is that plugin's own maintainer doc, not a path
  a skill writes in a target repo.

## Design

- **Folder.** `product/` at the repo root, visible, not a dot folder. Reasons: a reader can tell
  from the name that it holds files about the product, and ripgrep, behind the Grep tool, skips
  hidden folders by default. That second reason is inferred from ripgrep's defaults, not tested.
  The test for what goes in: an agent or person building the product reads it, and a user of the
  product does not.
- **Paths.**

  | File          | Old                      | New                        |
  | ------------- | ------------------------ | -------------------------- |
  | Build plans   | `docs/plans/<slug>.md`   | `product/plans/<slug>.md`  |
  | Evidence      | `docs/EVIDENCE.md`       | `product/EVIDENCE.md`      |
  | Architecture  | `docs/ARCHITECTURE.md`   | `product/ARCHITECTURE.md`  |
  | Business plan | `BUSINESS_PLAN.md`       | `product/BUSINESS_PLAN.md` |
  | Investor docs | beside the business plan | `product/INVESTOR_*.md`    |

  The per-repo override stays: a path the repo's `CLAUDE.md` names wins, as `plan-format.md` and
  `document-architecture` already allow.

- **Record format.** The last section of the plan, after Open:

  ```markdown
  ## Record

  - 2026-10-11 Planned: write-build-plan, status ready
  - 2026-10-12 Reviewed: Revise first, 2 blocking (Phase 3 Check proves nothing; In item X unbuilt)
  - 2026-10-13 Built Phase 1: a1b2c3d, `uv run pytest tests/test_signup.py` 12 passed
  - 2026-10-13 Design changed: was "POST /items returns 200", now "returns 201", because the client
    needs the created id
  - 2026-10-14 Checked: 11 Built, 1 Deviation (`app/api/items.py:41`)
  - 2026-10-14 Evidence: product/EVIDENCE.md section 2026-10-14 at d4e5f6a, tests passed, 0 open
    issues
  - 2026-10-14 PR: #42 https://github.com/<owner>/<repo>/pull/42
  ```

  Oldest first, one line per event, an event word first so a reader can scan it. Entries are
  appended in any status, including after `built`. Evidence and PR entries usually land after the
  build. Reason: a log that is edited cannot be trusted as a trail, and a fixed event word makes
  each kind of entry easy to grep.

- **Phase Status vs Record.** Status keeps the current state of a phase. Record keeps the history,
  so a phase that is rebuilt shows both runs.
- **Close, not retire.** `implement-from-plan` step 5 becomes Close: copy each lasting Design
  decision to the Key Decisions log in `product/ARCHITECTURE.md`, add the changelog entry, and keep
  the plan file.
- **Report-only skills append to the Record.** `review-build-plan` and `check-build-against-plan`
  still never edit plan content unless asked to fix. A Record line is their one write, and it is
  allowed because it records the run without changing the plan.
- **Which plans the evidence report covers.** `write-evidence-report` reads plans with status
  `building`, plus `built` plans with no Evidence entry yet. Its Evidence entry goes to each of
  them.
- **PR entry timing.** `pull-request` adds the entry on the Open path, after `gh pr create`
  returns the number: one more commit on the branch, pushed to the open PR. The plan is found by a
  `product/plans/*.md` file in the branch diff. With none, the step is skipped. The merge itself
  gets no entry, because the PR link leads to it.
- **EVIDENCE.md layout.** A `# Evidence: <product>` title, then one `## YYYY-MM-DD at <short-sha>`
  section per run, newest first, each holding today's table, Open issues, Claims, and Not run.
  Newest first keeps the reader's job to "read the first section". Readers that bound claims
  (`ceh-blog:draft-post`, `ceh-seo:write-project-listing-text`) read only that section, mirrored
  per `docs/CROSS_REFERENCES.md`.
- **Shared formats.** `plan-format.md` stays word for word identical in its three copies, and the
  Tell stage's handoff paragraph stays identical in its two copies (`docs/CROSS_REFERENCES.md`).

## Phases

### Phase 0: Lifecycle files move to product/

- **Builds:** every stated path changes to the Paths table in Design, with no fallback to the old
  paths:
  - `ceh-build-planning`: `references/plan-format.md` (Location), `review-build-plan`,
    `write-build-plan`, `README.md`.
  - `ceh-build-from-plan` and `ceh-check-build-against-plan`: their `plan-format.md` copies,
    `implement-from-plan`.
  - `ceh-business-plan`: `references/business-plan-schema.md` (location, `derived_from` examples),
    `find-product-market-fit`, `write-investor-materials`, `README.md`.
  - `ceh-codebase-explanation`: `document-architecture` (the location section at lines 148-153).
    Its existing one-time move of a legacy `.agents_workspace/ARCHITECTURE.md` stays, now into
    `product/ARCHITECTURE.md`. It gains no move from `docs/ARCHITECTURE.md`. (Decided by the user,
    2026-10-11.)
  - `ceh-testing`: `write-evidence-report` (sources and output path), `README.md`.
  - `ceh-blog:draft-post` and `ceh-seo:write-project-listing-text`.
  - `ceh-every-session`: `whats-next` lines 23-25 and 53, `record-project-decisions` lines 55-56.
  - Repo docs: `docs/STRATEGY.md` (spine table and Where files live, which gains the
    `product/` vs `docs/` rule), `docs/GETTING_STARTED.md`, `docs/CROSS_REFERENCES.md`,
    `docs/CATALOG.md`, and `docs/IDEAS.md` (the Living product page paths).
- **Check:** `grep -rnE "docs/(plans|EVIDENCE|ARCHITECTURE)" plugins docs .claude --include=*.md`
  returns only the two `ceh-workflow-builder`/`ceh-workflow-runner` README links to that plugin's
  own `docs/ARCHITECTURE.md`. `grep -rn "repo root" plugins/standalone/ceh-business-plan` no longer
  places `BUSINESS_PLAN.md` at the root.
- **Status:** done. `grep -rnE "docs/(plans|EVIDENCE|ARCHITECTURE)"`: only the two workflow README links remain

### Phase 1: Plan format keeps plans and gains the Record

- **Builds:** in the canonical
  `plugins/standalone/ceh-build-planning/references/plan-format.md`, the Location and Changing a
  plan sections say that plans persist, the Record section and its rules are added, and the
  Design-departure rule records the original. The file is mirrored to the two copies, and the
  `docs/CROSS_REFERENCES.md` entry is updated if its description changes.
- **Check:** both of these produce no output:
  `diff plugins/standalone/ceh-build-planning/references/plan-format.md plugins/standalone/ceh-build-from-plan/skills/implement-from-plan/references/plan-format.md`
  and the same diff against the `ceh-check-build-against-plan` copy. A grep of the canonical file
  for `deleted` finds no deletion rule, and a grep for `## Record` finds the section.
- **Status:** done. `diff` of the three plan-format.md copies: SAME

### Phase 2: The plan-lifecycle skills write Record entries

- **Builds:**
  - `write-build-plan`: step 2 reads built plans' frontmatter only. Save adds the Planned entry.
    The rule "Never rewrite a built plan" is kept.
  - `review-build-plan`: adds the Reviewed entry after the verdict, in report mode too.
  - `implement-from-plan`: Built and Design changed entries. Step 5 becomes Close. Output lists
    the decisions copied, not moved.
  - `check-build-against-plan`: adds the Checked entry after the report.
- **Check:** `grep -rn "Retire\|delete the plan\|deleted" plugins/standalone/ceh-build-*/skills plugins/standalone/ceh-check-build-against-plan/skills`
  returns nothing, and each of the four SKILL.md files names its Record event word.
- **Status:** done. `grep` for Retire/delete wording and `grep -c Record`: wording empty, Record named in all four skills

### Phase 3: Append-only evidence and the PR entry

- **Builds:**
  - `ceh-testing:write-evidence-report`: step 6 prepends a dated section instead of rewriting the
    file, and its Output shows the new layout. The Plan area follows the Design rule on which
    plans it covers. A new step appends the Evidence entry to each plan covered.
  - `ceh-blog:draft-post` and `ceh-seo:write-project-listing-text`: read the newest section only,
    mirrored per `docs/CROSS_REFERENCES.md`.
  - `ceh-git-workflow:pull-request`: the Open path adds the PR entry.
- **Check:** `grep -rn "whole\|never append" plugins/standalone/ceh-testing/skills/write-evidence-report/SKILL.md`
  finds no rewrite-whole rule, and the two reader skills say "newest section".
- **Status:** done. `grep` for rewrite-whole rule and "newest section": rule gone, newest section in both Tell readers

### Phase 4: Deletion wording, strategy, and registration

- **Builds:** fixes every statement that a built plan is deleted:
  - `ceh-codebase-explanation:document-architecture` lines 20-22
  - `ceh-business-plan:find-product-market-fit` lines 54-56 and `business-plan-schema.md` lines
    26-28
  - `ceh-testing:write-evidence-report` line 45
  - `docs/STRATEGY.md` handoff lifecycle (lines 84-95)

  Then `docs/CATALOG.md` rows whose description changed, a PATCH bump in `plugin.json` and
  `marketplace.json` for each of the 10 plugins touched (`ceh-build-planning`,
  `ceh-build-from-plan`, `ceh-check-build-against-plan`, `ceh-testing`, `ceh-git-workflow`,
  `ceh-blog`, `ceh-seo`, `ceh-codebase-explanation`, `ceh-business-plan`, `ceh-every-session`),
  the `CHANGELOG.md` 2026-10-11 section with the `git mv` commands for existing repos, and
  `docs/PLUGIN_VERSIONS.md`.

- **Check:** `python tools/validate-plugins/validate.py` passes, and
  `grep -rn "plan is deleted\|plans are deleted\|Built plans are\|deleted plans\|retired to" plugins docs --include=*.md`
  returns nothing.
- **Status:** done. `python tools/validate-plugins/validate.py` and `grep` for deletion wording: OK: all plugin checks passed, grep empty

## Open

- None blocking. Assumptions taken, each open to change in review:
  - The PR entry is added on Open (PR number known), not on merge, which would need a commit on
    `main` after the merge.
  - `EVIDENCE.md` is newest first, so readers stop at the first section.
  - An existing `EVIDENCE.md` in the old single-run layout becomes the first dated section on the
    next run, with no migration step.
  - `ceh-business-plan:develop-business-plan` finds the plan with a `**/BUSINESS_PLAN.md` glob, so
    it would still find a root file. Only where a new plan is written changes.
  - This plan carries a Record before the format defines one, to try the format on itself.

## Record

- 2026-10-11 Planned: written by hand in the plan format (ceh-build-planning is not installed in
  this session), status ready
- 2026-10-11 Design changed: was "plans at `docs/plans/`", now "all lifecycle files under
  `product/`", because `docs/` is for users of the product only (user decision)
- 2026-10-11 Built Phase 0: grep for old docs/ lifecycle paths, only the two workflow README links remain
- 2026-10-11 Built Phase 1: diff of the three plan-format.md copies, SAME
- 2026-10-11 Built Phase 2: grep for Retire and delete wording empty, Record named in all four skills
- 2026-10-11 Built Phase 3: rewrite-whole rule gone, newest section in both Tell readers
- 2026-10-11 Built Phase 4: validate.py, OK: all plugin checks passed
- 2026-10-11 Checked: 31 Built, 2 Deviation (Design Record example lines for Planned and Evidence
  differ from the plan format's line shapes), 2 Extra (Record sentence added to the
  ceh-build-from-plan and ceh-check-build-against-plan READMEs)
- 2026-10-11 PR: #92 https://github.com/cheneeheng/ceh-claude-code-library/pull/92
