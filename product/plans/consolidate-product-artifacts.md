---
schema: plan/v2
generated_from: consolidate-product-artifacts.yaml
generated_note: "Do not edit. artifact.py renders this file from consolidate-product-artifacts.yaml: edit the YAML, then run artifact.py render."
title: Every product artifact a skill saves goes to .agents_workspace/product/
status: building
created: 2026-11-13
---

<!-- prettier-ignore-start -->

## Goal

Today a target project has two `product/` folders: root `product/` for committed handoff files
and `.agents_workspace/product/` for local output, and artifacts in one cite artifacts in the
other. After this plan every plugin skill, hook and script saves and reads product artifacts in
`.agents_workspace/product/` only, and every reference from one artifact or skill to a format
that has a YAML source names the `.yaml`, never its generated `.md`. The rule and the strategy
say so first, and a validator check keeps a root `product/` path or a `.md` reference from
coming back.

## Scope

**In:**

- `.claude/rules/decision-artifact-locations.md` and the "Where files live" and spine sections
  of `docs/STRATEGY.md` rewritten to one canonical `.agents_workspace/product/` tree, with the
  wording "committed beside it" in `decision-output-templates.md` and "that Markdown
  committed beside the YAML" in `docs/STRATEGY.md` changed to "saved beside".
- Hook scripts: the docstrings and comments of `build-record-guard.py` and the 13
  `artifact-render-hook.py` files name the one path, and fixtures in
  `tools/validate-plugins/checks/hooks.py` use it. The `ceh-build-plan` eval fixtures,
  graders and prompts use it too.
- The lookups that find an artifact through the source repo's git, in `pull-request`,
  `test-a-bug-fix` and `implement-from-plan`, find it in the workspace instead.
- Plans, vision, strategy, architecture and evidence: every skill, schema, template and README
  that writes or reads `product/plans/`, `product/VISION`, `product/STRATEGY`,
  `product/ARCHITECTURE` or `product/EVIDENCE` names the `.agents_workspace/product/` path.
- Fix records and retros: `product/fixes/` and `product/retros/` become
  `.agents_workspace/product/fixes/` and `.agents_workspace/product/retros/`, the period retro
  and the session retro become one file each instead of an in-repo file and a local file, and
  the fix record's "same commit" rule is replaced.
- References to a format with a YAML source name the `.yaml` in every skill body, schema,
  template, example and README, except the cases listed in Design under "References that stay
  Markdown".
- A check in `tools/validate-plugins/` that fails on a root `product/` artifact path, or a
  `.md` path of a YAML format, anywhere under `plugins/standalone/` outside an allowlist.
- `docs/CATALOG.md`, `docs/GETTING_STARTED.md`, `docs/RETRO_WORKFLOW.md`,
  `docs/CROSS_REFERENCES.md`, `docs/IDEAS.md`, the root `CLAUDE.md`, `plugins/CLAUDE.md` and
  the plugin READMEs brought in line, with
  a PATCH bump, changelog entry and `docs/PLUGIN_VERSIONS.md` row for every plugin touched.

**Out:**

- Moving this repo's own `product/` folder into its workspace: The discussion keeps migrating existing artifacts separate from changing the defaults.
  CI reads `product/plans/*.yaml` (`checks/artifact_models.py`), 14 rule and tool files cite
  plans by path, and `.agents_workspace/` is git-ignored here, so the move needs its own
  plan. Until then this repo's `CLAUDE.md` names `product/` as its location, which every
  skill honours once phases 3 and 4 have written the escape into each schema.
- A migration tool for consuming projects: A project moves its folder once with `git mv` or a file move. The READMEs say so in one
  line and the changelog entry marks it as a breaking change. A tool can be added if a real
  project needs one.
- Reading the old root `product/` path as a fallback: One path only is the request, and a second read path is a shim that keeps two folders
  alive. A project that has not moved names its location in `CLAUDE.md`.
- The session tools at the top of `.agents_workspace/`: The decision log, handoffs, research notes, questionnaires, `CODEBASE_EXPLAINED.md`,
  competitor analyses and `workflow/` are not product artifacts and already have one path.
  The user confirmed on 2026-11-13 that they stay at the top of `.agents_workspace/`.
- `GLOSSARY.yaml`, blog posts in a blog repo, `docs/`, `CHANGELOG.md`, `README.md` and `.claude/` files: These are what the project ships or what its users read, not lifecycle artifacts.
- Changing any YAML format's keys: The discussion asks for unchanged YAML schemas to contain the scope. Only the two
  Markdown retro formats change, because their two-file split cannot survive one folder.
- The amendment of vision principle 2: `docs/STRATEGY.md` has the vision change first, in its own PR. It is one sentence, so it
  lands as its own small PR before Phase 1 and needs no plan.
- Cloud session setup for the workspace repo: Not investigated or tested in the discussion, and no skill depends on it.
- `docs/starlight/`: Its pages still name plugins retired before this plan (`ceh-build-planning`,
  `ceh-business-plan`), so it is already out of date and is not rebuilt from these files.

## Design

- **One path:** A product artifact lives at `.agents_workspace/product/<same sub-path as today>`:
  `plans/<slug>.yaml`, `VISION.yaml`, `STRATEGY.yaml`, `ARCHITECTURE.yaml`, `EVIDENCE.yaml`,
  `fixes/<slug>.yaml`, `retros/<name>`, and every folder already there (`business/`,
  `plan-reviews/`, `code-reviews/`, `qa/`, `perf/`, `security-audit/`, `ux-audits/`,
  `test-audits/`, `refactor/`, `stress-tests/`, `learning/`, `blog/`, `blog-voice.yaml`,
  `design-variants/`, `business-plan-reviews/`). File names do not change. The escape "unless
  the repo's `CLAUDE.md` names another location" is written in every schema that names a
  product path. Today only `plan-schema.md`, `document-architecture`,
  `write-vision-and-strategy` and `find-product-market-fit` carry it, so phases 3 and 4 add
  it, in the wording `plan-schema.md` uses, to `evidence-schema.md`, `fix-record-schema.md`,
  `period-retro-schema.md`, `session-retro-schema.md`, `repeat-mistake-schema.md` and step 3
  of `pull-request`.
- **An artifact left at the old path:** Plugins update on a version bump, so a project with a root `product/` gets the new path
  unannounced. The skills that find a plan, a vision or a strategy (`write-build-plan`,
  `implement-from-plan`, `write-vision-and-strategy`) gain one sentence: a file found at root
  `product/` with none at the new path is reported with the move command, never read and
  never written again beside it.
- **Lookups that used source git:** `pull-request` step 3 finds its plan with `git diff --name-only origin/main...HEAD --
  product/plans/` and commits the PR record to the branch. It takes the plan the user names,
  or the one in `.agents_workspace/product/plans/*.yaml` whose `record` has a Built Phase
  entry and no PR entry after it, appends the PR entry, and makes no source commit.
  `test-a-bug-fix` finds the diagnosed record with `git status --porcelain product/fixes/`.
  It finds it by `status: diagnosed` in `.agents_workspace/product/fixes/*.yaml`.
  `implement-from-plan` step 5 drops "in one commit" for the copy into `ARCHITECTURE.yaml`.
- **Rules whose reason was the commit:** `write-vision-and-strategy` keeps "neither doc carries pricing" with the reason that build
  skills read both docs and must not read business material. `document-architecture` keeps
  its ban on a git-ignored folder as a ban on any folder other than
  `.agents_workspace/product/`.
- **Works with or without a workspace repo:** No skill assumes `.agents_workspace/` is a nested git repo. Where it is one, its history
  versions the artifacts. Where it is a plain folder, the project decides whether to commit or
  ignore it. No skill adds `.agents_workspace/` to `.gitignore` for a product artifact. One
  limit, said in the README move note: a linked worktree gets a workspace only when the
  workspace is a git repo, so building in a worktree without one needs the plan's path passed
  by hand.
- **Hooks already match the path:** `place_format` in `artifact-render-hook.py` matches a plan by its parent folders `plans`
  and `product`, a spine file by a parent named `product` or `business`, and a repeat-mistake
  report in either retros folder. `build-record-guard.py` matches the substring
  `/product/plans/`. Each already accepts the `.agents_workspace/product/` path (read from the
  code, not yet run), so the matching logic stays and only docstrings and comments change.
  Phase 2 adds the fixtures that prove it. The copies stay byte-identical, edited in the
  canonical `ceh-build-plan/scripts/` and copied to the other 12.
- **Plans reach a linked worktree:** A linked worktree's workspace is a git worktree of the main workspace repo and holds only
  committed files, so a plan written in the main checkout and not yet committed there is
  missing in the worktree. `create()` in `sync-agents-workspace.py` commits the main
  workspace's pending changes before `git worktree add`, with the subject
  `chore(workspace): sync main before worktree <worktree folder>`, which the user approved
  on 2026-11-13, in the form the plan
  `workspace-sync-commit-message` sets, which is built first. It makes no commit while
  `merging(main_ws)` is true, so it never concludes the user's own merge. When the worktree
  already has its workspace, `create()` returns as today. When the branch
  `ceh-ws/<X>/<folder>` already exists, the worktree checks it out and then merges `<X>` into
  it, so the new commit is there too.
- **Fix record and its fix:** The record no longer rides in the fix's commit. The fix's commit message carries the footer
  `Refs: fixes/<slug>`, so `git log --grep "fixes/<slug>"` in the source repo finds the fix,
  and the record's keys stay as they are. `fix-record-schema.md` (canonical in
  `find-root-cause`, copied to `test-a-bug-fix`) replaces its "Same commit" rule with this.
  `fix-record-model.py` checks values too: `PlanPath` becomes
  `^(\.agents_workspace/)?product/plans/\S+$` and `FixPath`
  `^(\.agents_workspace/)?product/fixes/\S+\.(yaml|md)$`, so a record already saved still
  checks, with a model fixture for each form. The version stays `fix-record/v2`, because no
  key is renamed or removed. The old form in the regex goes on the validator allowlist.
- **One retro file:** `review-recent-work` and `diagnose-session` each save one file to
  `.agents_workspace/product/retros/` holding in-scope and out-of-scope issues, since the two
  files of today would share one name in one folder. The `other_file` frontmatter key goes,
  so the formats become `period-retro/v2` and `session-retro/v2`, per
  `decision-output-templates.md`. `diagnose-session` keeps its `-shareable.md` copy. A file
  saved under the old forms is still read. `prevent-repeat-mistake` has the same split in
  `repeat-mistake/v2`: it saves one report holding both kinds of fix, and its required key
  `other_file` stays in the format and is always `null` in a new report, which the schema
  says, so no YAML format changes. An older pair is still read.
- **References name the YAML:** For each format in `decision-output-templates.md` with a YAML source, a path written in a
  skill body, a schema's "where it is saved" line, a template value, an example or a README
  ends in `.yaml`. The schema files say once that the `.md` is rendered beside it. Template
  values change too: `plan: product/plans/<slug>.md` in `plan-review.template.md` and the fix
  record templates, `previous:` in the fix record templates, and `derived_from` in
  `business-plan-schema.md`.
- **References that stay Markdown:** These cannot name a YAML file and go on the validator allowlist. The user decided on
  2026-11-13 that the Markdown-only formats stay Markdown for now and get YAML formats
  later, each in its own plan, which then removes its allowlist entry.

  - Formats with no YAML source, where the Markdown is the file: plan review, code review,
    refactor report, stress-test outcome, test audit, business plan review, period retro,
    session retro and its shareable copy, investor deck and outreach, blog drafts and their
    edited and repurposed versions, learning record, design variants.
  - Legacy files with no YAML beside them: a `plan/v1` plan, a `fix-record/v1` record, and the
    `.md` of any spine file written before its YAML format. The skills keep their "the `.md`
    when no YAML exists" clause.
  - A `.md` passed as input and resolved through its `generated_from` key, as
    `write-build-plan` and `implement-from-plan` accept.
  - Sentences about the generated file itself: "never edit the generated `.md`", the render
    command's output, and the layout templates `*.template.md` that the renderer follows.
  - Notes on an older location that tell a skill to move a file: `product/BUSINESS_PLAN.md`,
    `.agents_workspace/ARCHITECTURE.md`, and the old root `product/plans/` in the sentence
    "An artifact left at the old path" adds.
- **The validator check:** `tools/validate-plugins/checks/artifact_paths.py`, called from `validate.py`, scans
  `plugins/standalone/**` except `evals/results/` and `archive/`. It fails on `product/`
  followed by a path when `.agents_workspace/` does not precede it, and on a path ending in
  `.md` whose stem and folder belong to a YAML format. The allowlist is a tuple of
  `(file glob, pattern)` pairs with one reason each, for the cases above. It is stdlib only,
  like the other checks.
- **Canonical first:** Every edited section listed in `docs/CROSS_REFERENCES.md` is changed in its canonical file
  and copied to each listed copy in the same phase, per
  `decision-shared-standards-duplication.md`: `plan-schema.md` (6 copies),
  `architecture-schema.md` (6), `evidence-schema.md` (3), `business-plan-schema.md` (11),
  `vision-schema.md` and `strategy-schema.md` (3 each), `fix-record-schema.md` and its
  templates and model (2), and the report schemas `write-evidence-report` copies.
- **Vision:** `docs/VISION.md` names no artifact path. Principle 2 says "a decision that shapes the repo
  for others belongs in a committed file", and `implement-from-plan` copies a plan's lasting
  decisions into `ARCHITECTURE.yaml`, which moves to the workspace. Where the workspace is a
  plain ignored folder those decisions are in no committed file, so the plan conflicts with
  the principle as written. `decision-vision-governs.md` then requires the vision to change
  or the plan not to land, and the vision changes in its own PR first. The user decided on
  2026-11-13 to amend principle 2 to read "a committed file or the versioned workspace", in
  its own PR, and Phase 1 starts only after that PR has merged. `docs/STRATEGY.md` drops its
  claim that every handoff file follows from that principle.

## Phases

### Phase 1: The rule and the strategy name one path

- **Builds:** `decision-artifact-locations.md` rewritten with its new Why (two folders confuse a person
  reviewing them, and cross-references break across them). `docs/STRATEGY.md`: the spine
  table, "Where files live", the lifecycle bullets, and one line under "Where the repo does
  not match yet" saying the plugins follow in later phases and this repo's own `product/`
  stays until its own plan. The "committed beside" wording in `decision-output-templates.md`
  and `docs/STRATEGY.md`. Root `CLAUDE.md` Structure block and a line
  naming `product/` as this repo's location until it migrates. Changelog entry.
- **Check:** `python tools/validate-plugins/validate.py` exits 0, and
  `grep -n "Committed in the target repo" docs/STRATEGY.md` prints nothing.
- **Status:** done, python tools/validate-plugins/validate.py: OK: all plugin checks passed; the STRATEGY.md grep printed nothing

### Phase 2: Hooks and fixtures prove the path

- **Builds:** Docstrings and comments in `build-record-guard.py` and `artifact-render-hook.py` (canonical,
  then 12 copies). Fixtures in `checks/hooks.py`: a plan, a spine file and a repeat-mistake
  report under `.agents_workspace/product/` each render, and a hand-written Built Phase entry
  in `.agents_workspace/product/plans/x.yaml` is denied. `create()` in
  `sync-agents-workspace.py` commits the main workspace before adding a worktree, with three
  fixtures: an uncommitted plan in the main workspace exists in the new worktree's workspace,
  the same holds when the `ceh-ws/` branch already existed, and a main workspace with a merge
  in progress gets no commit. PATCH bumps for the 13 hook plugins and `ceh-git-workflow`.
- **Check:** `python tools/validate-plugins/validate.py` exits 0 with the new fixtures listed in its
  hooks output, and each new fixture was seen failing once with its assertion inverted.
- **Status:** done, python tools/validate-plugins/validate.py: OK: all plugin checks passed; the 7 new fixtures failed inverted (wt3 and wt4 against the old create(), the other 5 with their assertion flipped)

### Phase 3: Plans, vision, strategy, architecture and evidence move

- **Builds:** Writers: `write-build-plan`, `implement-from-plan`, `review-build-plan`,
  `check-build-against-plan`, `write-vision-and-strategy`, `document-architecture`,
  `write-evidence-report`, `pull-request`. Readers: `record-project-decisions`, `whats-next`,
  `hand-off-session`, `draft-post`, `write-project-listing-text`, `write-concept-docs`,
  `write-fastapi-endpoints`, `find-product-market-fit` and the other ten
  `ceh-product-direction` skills through `business-plan-schema.md`. Their schemas, templates,
  descriptions, examples and plugin READMEs, with each reference to these five formats naming
  the `.yaml`. The `CLAUDE.md` escape in `evidence-schema.md` and `pull-request` step 3, the
  three lookups under "Lookups that used source git" except the fix record's, the old-path
  sentence, and the two reworded rules. The `ceh-build-plan` eval `fixture.sh` and
  `scaffold.sh` files, graders and `prompt.md` files use the new path. PATCH bumps.
- **Check:** `python tools/validate-plugins/validate.py` exits 0, and
  `grep -rnE "(^|[^/a-z_])product/(plans|VISION|STRATEGY|ARCHITECTURE|EVIDENCE|architecture)" plugins/standalone --exclude-dir=results --exclude="fix-record*"`
  prints only lines the Design lists under "References that stay Markdown". The fix record
  files are Phase 4's.
- **Status:** done, python tools/validate-plugins/validate.py: OK: all plugin checks passed; the grep printed one line, the old-path move note in implement-from-plan step 1 The three descriptions that would have named a path (implement-from-plan,
  write-evidence-report, write-vision-and-strategy) name none, because the paths took
  write-vision-and-strategy over 300 characters and the total over its ratchet.

### Phase 4: Fix records and retros move

- **Builds:** `find-root-cause` and `test-a-bug-fix`: path, the `Refs: fixes/<slug>` footer rule, schema,
  templates, the `PlanPath` and `FixPath` patterns in both copies of `fix-record-model.py`
  with their fixtures, and the `status: diagnosed` lookup in `test-a-bug-fix`.
  `prevent-repeat-mistake`: one report, `other_file` always `null`. `review-recent-work` and
  `diagnose-session`: one file, `period-retro/v2` and `session-retro/v2` templates and
  schemas. The `CLAUDE.md` escape in the fix record, retro and repeat-mistake schemas.
  `docs/RETRO_WORKFLOW.md`. PATCH bumps for `ceh-coding-conduct`, `ceh-testing`,
  `ceh-every-session`, `ceh-git-workflow`, `ceh-session-learning`.
- **Check:** `python tools/validate-plugins/validate.py` exits 0.
  `grep -rnE "(^|[^/a-z_])product/(fixes|retros)" plugins/standalone docs/RETRO_WORKFLOW.md`
  prints only the old form inside the two `fix-record-model.py` patterns, and Phase 3's grep
  run without its `--exclude` prints only the lines under "References that stay Markdown".
- **Status:** todo

### Phase 5: Remaining YAML references, the validator check and the docs

- **Builds:** The `.md` paths of the formats that already live in the workspace change to `.yaml` in
  their schemas and readers: business plan, QA report, performance file, security audit, the
  three usability audits, handoff, repeat-mistake report. `checks/artifact_paths.py` with its
  allowlist, wired into `validate.py` and `tools/validate-plugins/README.md`.
  `docs/CATALOG.md`, `docs/GETTING_STARTED.md`, `docs/CROSS_REFERENCES.md`, `docs/IDEAS.md`,
  the `templates` check description in `plugins/CLAUDE.md`, the one-line move note in each
  affected plugin README, the breaking-change note in the changelog, and the "does not match
  yet" line in
  `docs/STRATEGY.md` reduced to this repo's own folder. PATCH bumps.
- **Check:** `python tools/validate-plugins/validate.py` exits 0. With one skill line changed back to
  `product/plans/<slug>.md` it exits 1 naming that file and line, and exits 0 again once the
  line is restored.
- **Status:** todo

## Open

- Does a subagent started with `isolation: "worktree"` get a workspace? The sync hooks fire on
  SessionStart and on `EnterWorktree` only.: It gets none. Tested on 2026-11-14 in Phase 2: a subagent started with
  `isolation: "worktree"` in this repo, whose `.agents_workspace` is a nested git repo, found
  no `.agents_workspace` in its worktree. So such a subagent is given the plan's content, or
  the artifact it needs, by its caller.
- Should fix records gain a key for the source commit or PR?: No. The `Refs: fixes/<slug>` commit footer links the two and keeps `fix-record/v2`
  unchanged.

## Record

- 2026-11-13 Planned: status draft
- 2026-11-13 Reviewed: Revise first, 6 blocking (pull-request and test-a-bug-fix find artifacts through source git, fix-record model path patterns, CLAUDE.md escape missing for fixes, retros and evidence, repeat-mistake other_file in one folder, phase 3 check hits phase 4 files, vision principle 2)
- 2026-11-13 PR: #270 https://github.com/cheneeheng/ceh-claude-code-library/pull/270
- 2026-11-14 Built Phase 1: tools/validate-plugins/validate.py: OK: all plugin checks passed. The STRATEGY.md grep printed nothing.
- 2026-11-14 PR: #288 https://github.com/cheneeheng/ceh-claude-code-library/pull/288
- 2026-11-14 Built Phase 2: tools/validate-plugins/validate.py: OK: all plugin checks passed. The fixtures wt3 and wt4
  failed against the old create(), and wt5, the build-record-guard workspace fixture and the
  three workspace render fixtures failed with their assertions inverted.
- 2026-11-14 PR: #289 https://github.com/cheneeheng/ceh-claude-code-library/pull/289
- 2026-11-14 Design changed: was "Notes on an older location that tell a skill to move a file: `product/BUSINESS_PLAN.md`
  and `.agents_workspace/ARCHITECTURE.md`.", now also names the old root `product/plans/` in
  the old-path sentence, because that sentence must name the old folder to report it.
- 2026-11-14 Built Phase 3: tools/validate-plugins/validate.py: OK: all plugin checks passed. The Phase 3 grep printed
  only the old-path move note in implement-from-plan step 1.

<!-- prettier-ignore-end -->
