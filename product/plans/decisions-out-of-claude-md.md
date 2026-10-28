---
schema: plan/v1
title: Settle where a decision lives, then move this repo's CLAUDE.md decisions into rule files
status: building
created: 2026-10-28
---

## Goal

`ceh-every-session:record-project-decisions` writes decisions to `.claude/rules/decision-<topic>.md`
but never says what happens when `CLAUDE.md` already covers the area, so this repo keeps decisions
in both homes: four `decision-` files, and dozens more inside the root `CLAUDE.md` and
`plugins/CLAUDE.md`. The user asked on 2026-10-28 for the skill to state the boundary and for this
repo's `CLAUDE.md` decisions to move out. After the build, a choice someone could have made
differently lives in its own `decision-` file, with its own `git log`, and each `CLAUDE.md`
describes the repo and its procedures and points to the decisions instead of restating them.

## Scope

**In:**

- The skill states the boundary: a choice between alternatives goes in a `decision-` file even
  when `CLAUDE.md` covers the area, and `CLAUDE.md` keeps the description and procedures.
- Record mode, on a decision `CLAUDE.md` already states, stops and reports it as a candidate to
  move. Seed mode reports every decision `CLAUDE.md` states as a candidate to move, and writes none
  of them.
- The 150-line warning counts only unscoped `decision-` files, the ones that load in every session.
- The decision-rule schema documents the optional `paths` key.
- The root `CLAUDE.md` decisions listed under Design move into unscoped `decision-` files.
- The `plugins/CLAUDE.md` decisions listed under Design move into `decision-` files scoped with
  `paths` `plugins/**` and `.claude/skills/**`.
- Every live file that cites a moved section by name points to its new file.

**Out:**

- `.agents_workspace/competitor-analysis/CLAUDE.md`: it lives in the private, git-ignored
  workspace repo and scopes rules to one folder. Moving it into the committed `.claude/rules/`
  would publish private-workspace rules.
- `docs/starlight/node_modules/sitemap/CLAUDE.md`: a third-party package file.
- Historical files that cite `CLAUDE.md` sections (`audits/`, `CHANGELOG.md`, `built` plans,
  retros): they record what was true then and are never edited.
- `docs/starlight/src/content/docs/`: generated and git-ignored, rebuilt from `docs/` by
  `docs/starlight/scripts/sync-docs.mjs`.
- Rewording a decision while moving it: the move keeps each rule's meaning, so a review of the
  diff checks placement, not policy.
- Adding the `schema:` line to the four existing `decision-` files: the skill already adds it when
  a file is next edited.
- A validator check for the boundary: wait for a measured miss first.
- Editing `docs/VISION.md`: line 257 lists the files a vision change must update, and does not name
  `.claude/rules/`. `VISION.md:256` requires any change to it to land in its own PR, and the vision
  is adapted to last, not first. `decision-vision-governs.md` already makes every file that
  disagrees with the vision get fixed in the same PR, rule files included.

## Design

- **The boundary test.** A statement goes in a `decision-` file when someone could reasonably have
  chosen differently and it should stick across sessions. `CLAUDE.md` keeps what the project is,
  its layout, its commands, and its procedures. A procedure step that depends on a decision
  names the decision file rather than restating it. Reason: one decision, one file, one history,
  per the skill's existing "one decision per file" rule.
- **Skill edits** (`plugins/standalone/ceh-every-session/skills/record-project-decisions/`):
  - A new Rule, "A choice goes in a `decision-` file, a description in `CLAUDE.md`", with the test
    above.
  - Record step 2: "Already stated in a `decision-` file in the same terms: stop and say so.
    Already stated in `CLAUDE.md`: stop and report it as a candidate to move into its own file."
    The skill still edits only `decision-` files. Moving text out of `CLAUDE.md` is a separate
    request, because `CLAUDE.md` is not this skill's to change.
  - Seed step 1 and step 4: decisions `CLAUDE.md` already states are listed in the report as
    candidates to move, never written as duplicates.
  - The "Keep the set small" rule counts lines in `decision-` files without `paths`, because its
    reason is "every line costs context in every session", and a scoped file loads only when its
    paths are read.
  - `SKILL.md:20-21` and the description: say that a rule file without `paths` loads in every
    session and one with `paths` loads when a matching file is read, instead of "every session
    loads" for all of them. The description stays under 300 characters.
  - `references/decision-rule-schema.md`: a Frontmatter entry for the optional `paths` key, a list
    of globs, set only when the decision concerns one part of the tree. The Source entry gains a
    third form, `<file> (<short commit hash>)`, for a decision moved out of an existing file.
  - The template stays as it is: `paths` is optional, and the template carries no comments.
- **Version.** `ceh-every-session` PATCH bump, content only, in `plugin.json`,
  `marketplace.json`, and `docs/PLUGIN_VERSIONS.md`, with a `CHANGELOG.md` entry under
  `## 2026-10-28`. Phases 2 and 3 change no plugin and bump nothing.
- **PRs.** One PR per phase, staged. Each PR adds its own `CHANGELOG.md` entry under the date it is
  opened. Phases 2 and 3 have no `### Plugin versions` table because they bump nothing.
- **Moved file shape.** Each moved file fills the skill's `decision-rule.template.md`. Its Why line
  takes the reason from the moved text, `Decided` is the date the rule first entered its file (from
  `git log -S "<phrase>" --format=%as -- <file>`, oldest), and `Source:` reads
  `CLAUDE.md (<short hash>)` or `plugins/CLAUDE.md (<short hash>)` for that commit. Any
  explanation longer than one line stays in the `CLAUDE.md` it came from or its source doc.
- **Root `CLAUDE.md` decisions → unscoped `.claude/rules/` files:**

  | File                                       | Source in `CLAUDE.md`                                                                                                                            |
  | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
  | `decision-vision-governs.md`               | Lines 9-14: every change holds up against `docs/VISION.md`, and a disagreement is fixed in the same PR                                           |
  | `decision-plugin-boundaries.md`            | Organizing Principle bullets (moments not topics, names declare scope) and rules of thumb at lines 42-43, 46-48, 52-56                           |
  | `decision-no-bundles.md`                   | The "There are no bundles" paragraph                                                                                                             |
  | `decision-every-session-admission.md`      | Line 49-51, what `ceh-every-session` admits                                                                                                      |
  | `decision-shared-standards-duplication.md` | Line 44-45, Cross-Reference Rule, and Shared-Standards Duplication Policy                                                                        |
  | `decision-plugin-dependencies.md`          | Plugin Dependencies section                                                                                                                      |
  | `decision-evaluation.md`                   | Evaluation: Anthropic's tools only, workspace in `.agents_workspace/skill-evals/`, eval only when asked, never run the archived `ceh-evaluation` |
  | `decision-version-levels.md`               | Versioning: where versions live, PATCH/MINOR/MAJOR, bump at commit time                                                                          |
  | `decision-no-releases.md`                  | "This repo has no releases" paragraph                                                                                                            |
  | `decision-changelog-sections.md`           | "Every PR adds its own `CHANGELOG.md` entry" paragraph                                                                                           |

  Stays in `CLAUDE.md`: the intro, the tier table (`tools/validate-plugins/checks/repo_rules.py`
  parses its **Cross-cutting** row), Structure, Plugins, the Skills pointer, the Adding a Component checklist, Commands, the
  Evaluation commands and costs, Landing a branch, and Key Files. Each section that lost its rules
  keeps one line naming the decision file. Key Files gains a row:
  `.claude/rules/decision-*.md` | One file per project decision, loaded in every session.

- **`plugins/CLAUDE.md` decisions → `.claude/rules/` files with `paths` `plugins/**` and
  `.claude/skills/**`**, the same scope as `decision-skill-references.md`, because the authoring
  rules also govern the repo-local skills and the templates in `.claude/skills/add-plugin-component/`:

  | File                              | Source in `plugins/CLAUDE.md`                                                                         |
  | --------------------------------- | ----------------------------------------------------------------------------------------------------- |
  | `decision-component-templates.md` | Lines 7-11: start from the templates, official frontmatter fields only                                |
  | `decision-skill-bundled-files.md` | Lines 13-25 and 46-62: content inline, `references/` for two cases, migrated exceptions, scaffolds    |
  | `decision-output-templates.md`    | Lines 27-44: every saved file has a versioned template and a schema                                   |
  | `decision-component-names.md`     | Lines 64-77: verb phrase or noun, framework in the name                                               |
  | `decision-frontmatter-scalars.md` | Lines 79-115: `>-` descriptions, 300 characters, quoting other keys, `compatibility`                  |
  | `decision-invocation-flags.md`    | Lines 117-150: the three invocation cases, user-only rows in `whats-next`, one-line hook descriptions |

  Stays in `plugins/CLAUDE.md`: the explanation of why `>-` needs no escaping and the two folding
  rules (how to write the scalar, not a choice), and one pointer line per moved section. If nothing
  else remains, `plugins/CLAUDE.md` is cut to its heading, its scope line, and the pointer lines.

- **Live citations to update** (found with `grep -rn "CLAUDE.md"` on 2026-10-28):
  `docs/PLUGIN_DEPENDENCIES.md:4` and `:54`, `docs/STRATEGY.md:191`, `CONTRIBUTING.md:4`,
  `.claude/skills/model-audit/SKILL.md:74` and `:81`, `.claude/skills/add-plugin-component/SKILL.md:79`
  and `:196`, root `CLAUDE.md:99`, `plugins/CLAUDE.md:3` and `:22`,
  `tools/validate-plugins/README.md:37`, the `repo_rules.py:1-7` docstring, and the
  "see CLAUDE.md" message in `tools/validate-plugins/checks/scalars.py:38`. A citation that means
  `CLAUDE.md` as a whole ("the rules every change follows") names both `CLAUDE.md` and
  `.claude/rules/`. Each phase updates the citations of the file it moves from.
  `docs/VISION.md:8` ("`CLAUDE.md` says how the repo works") stays true and is not edited.
- **Line budget.** The unscoped `decision-` files total 39 lines today
  (`decision-skill-references.md` is already scoped). Phase 2 adds 130, ending at 169, over the
  150-line warning, so the Phase 2 report names the decisions that bind least, as the skill says.
  The scoped files of Phase 3 do not count. Context per session grows by 66 lines (285 to 351),
  because each file carries its own frontmatter, title, and Why line.

## Phases

### Phase 1: The skill states the boundary

- **Builds:** the Skill edits and the Version bump from Design, and this plan file.
- **Check:** `python tools/validate-plugins/validate.py` passes, and
  `grep -n "candidate to move" plugins/standalone/ceh-every-session/skills/record-project-decisions/SKILL.md`
  shows the Record and Seed lines.
- **Status:** done, `python tools/validate-plugins/validate.py` in a clean worktree: "OK: all
  plugin checks passed"; the grep shows lines 40 and 70.

### Phase 2: Move the root CLAUDE.md decisions

- **Builds:** the ten unscoped files from the root table, the root `CLAUDE.md` pointer lines and
  Key Files row, and the live citations that name a root `CLAUDE.md` section.
- **Check:** `python tools/validate-plugins/validate.py` passes (the tier-table parse included);
  `ls .claude/rules/decision-{vision-governs,plugin-boundaries,no-bundles,every-session-admission,shared-standards-duplication,plugin-dependencies,evaluation,version-levels,no-releases,changelog-sections}.md`
  lists all ten; `grep -n "no version ranges\|no version tags\|PATCH\*\* —" CLAUDE.md` prints
  nothing; `grep -rn "CLAUDE.md. (Plugin Dependencies\|Duplication Policy in .CLAUDE\|Versioning in .CLAUDE\|CLAUDE.md. Versioning" --include=*.md docs .claude/skills CONTRIBUTING.md tools`
  prints nothing; `cat $(grep -L "^paths:" .claude/rules/decision-*.md) | wc -l` prints the
  unscoped total, reported against the 150-line warning.
- **Status:** done, `python tools/validate-plugins/validate.py` in a clean worktree: "OK: all
  plugin checks passed"; `ls` lists 10, both greps print nothing; unscoped total 169, over the
  warning. The least-binding decisions are `decision-no-bundles.md` and `decision-evaluation.md`.
  Design changed: the budget check said "under 150", which the move cannot meet without rewording.

### Phase 3: Move the plugins/CLAUDE.md decisions

- **Builds:** the six scoped files from the `plugins/CLAUDE.md` table, the `plugins/CLAUDE.md` cut,
  and the live citations that name a `plugins/CLAUDE.md` section.
- **Check:** `python tools/validate-plugins/validate.py` passes;
  `grep -c "^paths:" .claude/rules/decision-{component-templates,skill-bundled-files,output-templates,component-names,frontmatter-scalars,invocation-flags}.md`
  prints 1 for each; `grep -rn "plugins/CLAUDE.md. (Skills\|Skills in .plugins/CLAUDE" --include=*.md docs .claude/skills tools`
  prints nothing. Manual, because only a live session shows what loaded: in a fresh session,
  `/context` lists none of the six files under Memory files, and after reading
  `plugins/CLAUDE.md` it lists all six.
- **Status:** todo

## Open

None

## Record

- 2026-10-28 Planned: status ready
- 2026-10-28 Reviewed: Revise first, 2 blocking (live-citation list misses six citations; VISION.md edit violates its own-PR rule)
- 2026-10-28 Built Phase 1: python tools/validate-plugins/validate.py, OK: all plugin checks passed
- 2026-10-28 PR: #179 https://github.com/cheneeheng/ceh-claude-code-library/pull/179
- 2026-10-28 Design changed: was "Phase 2 adds roughly 70 ... Context per session does not grow", now "Phase 2 adds 130, ending at 169 ... grows by 66 lines", because each moved file carries frontmatter, title and Why line
- 2026-10-28 Built Phase 2: python tools/validate-plugins/validate.py, OK: all plugin checks passed
