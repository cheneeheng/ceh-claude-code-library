---
schema: plan/v2
generated_from: markdown-formats-yaml.yaml
generated_note: "Do not edit. artifact.py renders this file from markdown-formats-yaml.yaml: edit the YAML, then run artifact.py render."
title: The Markdown-only formats become YAML formats
status: built
created: 2026-11-14
---

<!-- prettier-ignore-start -->

## Goal

On 2026-11-13 the user decided that the formats left Markdown-only by
`product/plans/consolidate-product-artifacts.yaml` (Design, "References that stay Markdown") get
YAML formats later. On 2026-11-14 the user asked for that work first, before this repo's own
`product/` folder moves. After this plan, the thirteen formats listed under Scope In each have a
pydantic model, a YAML template and a renderer, like the twenty YAML formats already there. Each
skill that writes one saves checked YAML and renders its Markdown beside it. A plugin hook checks
every write and a guard denies hand edits to the Markdown. `checks/artifact_paths.py` rejects a
`.md` path of each one, so the allowlist case "Formats with no YAML source" is gone.

## Scope

**In:**

- plan-review/v2 (`review-build-plan`), with its hooks already in `ceh-build-plan`.
- business-plan-review/v2 (`review-business-plan`), investor-deck/v2 and investor-outreach/v2
  (`write-investor-materials`), with the hooks already in `ceh-product-direction`.
- refactor-report/v2 (`refactor-repo`, `ceh-coding-conduct`), test-audit/v2
  (`audit-test-suite`, `ceh-testing`) and stress-test/v2 (`stress-test-plan`,
  `ceh-every-session`), with the hooks already in each plugin.
- learning/v2 (`explain-until-understood`, `ceh-codebase-explanation`), blog-draft/v2
  (`draft-post` and `edit-post`) and repurposed-post/v2 (`repurpose-post`, `ceh-blog-and-seo`),
  with the hooks already in each plugin.
- code-review/v2 (`code-review`) and period-retro/v3 (`review-recent-work`), with
  `artifact.py`, `artifact-render-hook.py` and `generated-md-guard.py` added to
  `ceh-git-workflow` and wired in its `hooks/hooks.json`.
- session-retro/v3 (`diagnose-session`), with the same three scripts added to
  `ceh-session-learning` and a new `hooks/hooks.json`.
- Every skill that reads one of these formats by path names the `.yaml` and, where it reads the
  content, carries the model and `artifact.py`, per `decision-artifact-validation.md`.
- Per format: a `checks/artifact_paths.py` pattern for its `.md` path, render-hook fixtures in
  `checks/hooks.py`, its name in the lists of `decision-artifact-validation.md` and
  `decision-output-templates.md`, `docs/CROSS_REFERENCES.md` entries for each copied file,
  `docs/CATALOG.md`, `docs/ENVIRONMENT_VARIABLES.md` and plugin README wording, a PATCH bump, a changelog entry and
  `docs/PLUGIN_VERSIONS.md` rows.

**Out:**

- Design variants: `design-ui` writes them as throwaway static HTML files, not Markdown, so there is no format
  to move. The consolidate plan's allowlist list names them, and they leave it unchanged.
- The session retro's `<report>-shareable.md`: It is a scrubbed copy of the rendered Markdown, made only when a report leaves the machine,
  and is the file handed to a person. It stays a Markdown copy of the rendered `.md`, now
  `<report>-shareable.md` beside the YAML's Markdown, and is not a format of its own. It
  drops the `generated_from` and `generated_note` keys, because `generated-md-guard.py` denies
  an edit to a `.md` that holds `generated_from`, and the scrub fixes edit the copy.
- Converting files already saved in the Markdown formats: They are records. Every reader keeps reading a v1 file (v2 for the two retros) when no YAML
  sits beside it, as the earlier conversions did, and nothing rewrites past files.
- The other report-only formats (research note, codebase explained, competitor comparison, decision log, questionnaire): The user's decision covers the list in the consolidate plan's Design, and these are not on
  it. They keep the rule in `product/plans/report-only-formats.yaml`: revisited when a session
  shows the format failing.
- Moving this repo's own `product/` folder: The next plan, after this one.
- Running eval cases: Real model calls, only on request per `decision-evaluation.md`.

## Design

- **One conversion rule for all thirteen:** Each format's model mirrors its current Markdown template field for field, so the builder
  derives the keys from the template and the schema file rather than from new design:
  - Every frontmatter field becomes a top-level key of the same name. A date is a YAML date, a
    `<a | b>` choice is a `Literal`, a count such as `score: <N>/14` or `pmf_gate: <N>/8` is an
    integer key with its bound, rendered back as `N/14`.
  - Every section becomes one key named for its heading in snake_case. A table becomes a list of
    objects with one key per column. A bullet list becomes a list of strings, or of objects when
    each bullet has labelled parts (`**Route:**`, `**Status:**`, `— <answer>. <reason>`). A
    bold-labelled line (`**Verdict:**`, `**Goal:**`) becomes a key. Free text, such as a blog
    body or a stress-test's plan, is one Markdown string.
  - A repeated block (the period retro's `### N. <Kind>: <issue>`, the session retro's root
    causes, the refactor report's `## <cluster>`, the investor deck's numbered slides) becomes a
    list of objects. Its number is the position in the list, never a stored key.
  - Strict pydantic: `extra="forbid"`, no empty strings, a non-empty list wherever the template
    shows a required row.
  - The renderer writes the current layout, so a rendered v2 file reads like a v1 file plus the
    generated frontmatter keys. The current `<schema>.template.md` stays as the layout template
    the renderer follows, and its schema line moves to the new version.
- **Versions:** Each format is renamed in its required keys, so its version goes up one: `/v1` to `/v2` for
  eleven, and `period-retro/v2` and `session-retro/v2` to `/v3`. The schema file keeps a short
  section on the old version, for files already saved.
- **Files per format:** In the skill that writes the format: `references/<schema>-model.py` beside
  `references/<schema>-schema.md`, `assets/<schema>.template.yaml`, and `scripts/artifact.py`,
  copied from `ceh-build-plan/scripts/artifact.py`. The model exports `NAME`, `VERSION`,
  `MODEL` and `render(doc, source) -> str`, as `repeat-mistake-model.py` does. The skill body
  saves the YAML, runs `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py render <file>.yaml`,
  and fixes the YAML until it exits 0. Each copy is registered in `docs/CROSS_REFERENCES.md`
  and kept identical by the `copies` check.
- **Paths and names:** Same folder and same name, `.yaml` instead of `.md`, with the Markdown rendered beside it:
  `.agents_workspace/product/plan-reviews/`, `code-reviews/`, `refactor/`, `stress-tests/`,
  `test-audits/`, `business-plan-reviews/`, `retros/` (period and session),
  `business/INVESTOR_DECK.yaml` and `business/INVESTOR_OUTREACH.yaml`, `blog/` and
  `learning/<subject>.yaml`. File names follow `decision-saved-file-names.md` unchanged,
  including the blog draft's exempt `<YYYY-MM-DD>-<slug>`.
- **Blog files saved outside the workspace:** The user decided on 2026-11-14 that the skills always create YAML, which then renders to
  Markdown, wherever the file is saved. So `edit-post` saves `<name>-edited.yaml` beside an
  untracked draft, and `repurpose-post` saves `<slug>-<format>.yaml` next to a post on disk,
  each with its rendered `.md`. For a git-tracked post, `edit-post` saves `<name>.yaml` beside
  it and renders over `<name>.md`, replacing the post's front matter with the format's. A post
  `draft-post` writes into a blog repo is YAML with its rendered `.md` too, so
  `blog-draft-schema.md` drops its sentence that such a post follows that repo's own front
  matter. A draft whose `.md` has a YAML beside it is revised through its YAML, never through
  the `.md`, which the guard denies.
- **Living files saved before this plan:** A learning record, an investor deck or an investor outreach file saved as `.md` with no YAML
  beside it is still edited in place when its skill next updates it, as `plan-schema.md` says
  for a `plan/v1` plan. Nothing converts it.
- **How the hook finds each file:** By its `schema:` key alone, which every template writes as its first line. No `place_format`
  entry is added: the writing skill runs the render itself, so a file missing its key fails
  that run in the same turn.
- **Hooks in the two plugins that have none:** `ceh-git-workflow` and `ceh-session-learning` get `scripts/artifact.py`,
  `scripts/artifact-render-hook.py` and `scripts/generated-md-guard.py`, copied from
  `ceh-build-plan`, and `PreToolUse` and `PostToolUse` entries on `Edit|Write|MultiEdit` as the
  other plugins wire them. `ceh-git-workflow` adds them next to its existing sync hooks in the
  same `hooks/hooks.json`. Neither joins `READERS`, because both write their formats. Each
  README says the check needs uv, and `docs/ENVIRONMENT_VARIABLES.md` adds both plugins to its
  `CEH_ARTIFACT_CHECK` row and `ceh-session-learning` to its `CEH_DISABLED_HOOKS` row.
- **Readers:** A grep of `plugins/standalone` on 2026-11-14 found no skill in another plugin that names any
  of these formats, so no plugin joins a phase as a reader. Inside a plugin,
  `review-recent-work` takes the date from a period retro's file name and changes the path to
  the `.yaml`, and `edit-post` and `repurpose-post` read a draft's content, so each carries the
  blog-draft model and `artifact.py` and runs `artifact.py check` first, falling back to the
  `.md` when no YAML exists. Each phase reruns
  `grep -rn "<schema>\|<folder>/" plugins/standalone` for its formats to confirm, and a reader
  it finds follows the same two rules.
- **The validator:** Each phase adds its formats' `.md` paths to `YAML_FORMAT_MD` in `checks/artifact_paths.py`, so
  a stale `.md` path fails in the same PR that adds the YAML. The phase that adds the last one
  rewrites the module docstring, which today points at the consolidate plan's exceptions.
- **Rule text:** Each phase appends its formats to the lists in `decision-artifact-validation.md` and
  `decision-output-templates.md`, citing this plan, as each earlier format plan did. In
  `decision-artifact-validation.md` the text names the user's decision of 2026-11-13 as the
  basis, because these formats are not handoff files another stage reads, which is what that
  rule's opening and its Why cover.

## Phases

### Phase 1: Plan review, business plan review and investor materials

- **Builds:** plan-review/v2 in `review-build-plan`, business-plan-review/v2 in `review-business-plan`,
  investor-deck/v2 and investor-outreach/v2 in `write-investor-materials`, each with model,
  YAML template, schema update, `artifact.py` copy and skill-body steps. Their readers, found by
  the Readers grep. Hook fixtures in `checks/hooks.py` for each format: a good file renders, a
  bad key is reported. The four `.md` patterns in `checks/artifact_paths.py`. Rule lists,
  `docs/CROSS_REFERENCES.md`, `docs/CATALOG.md`, `docs/ENVIRONMENT_VARIABLES.md`, READMEs, changelog, PATCH bumps of
  `ceh-build-plan` and `ceh-product-direction`.
- **Check:** `python tools/validate-plugins/validate.py` exits 0 with the new fixtures in its hooks output,
  and each new fixture failed once with its assertion inverted. With one skill line changed to
  `.agents_workspace/product/plan-reviews/<slug>.md` it exits 1 naming that line.
- **Status:** done, `python tools/validate-plugins/validate.py`: "OK: all plugin checks passed". With good and
  bad swapped, fixtures 154-155, 157-158, 160-161 and 163-164 each failed. With
  `.agents_workspace/product/plan-reviews/<slug>.md` appended to `review-build-plan/SKILL.md`
  it failed once: "SKILL.md:118: the .md path of a YAML format". Keys taken from body lines the frontmatter does not hold: `product` and `verdict_reason` in
  business-plan-review/v2, and `draft` in both investor formats (with `pmf_gate` in the
  outreach notes too) for the `Draft: gate <N>/8` line. A plan review's `findings` may be `[]`,
  since a clean plan has none, and render as `No findings.`. The eval grader
  `rbp-outcome-flawed-plan/graders/review-saved.md` now matches the `.yaml`.

### Phase 2: Refactor report, test audit and stress test

- **Builds:** refactor-report/v2 in `refactor-repo`, test-audit/v2 in `audit-test-suite`, stress-test/v2 in
  `stress-test-plan`, each with model, YAML template, schema update, `artifact.py` copy and
  skill-body steps. Their readers. Hook fixtures, `.md` patterns, rule lists,
  `docs/CROSS_REFERENCES.md`, `docs/CATALOG.md`, `docs/ENVIRONMENT_VARIABLES.md`, READMEs, changelog, PATCH bumps of
  `ceh-coding-conduct`, `ceh-testing`, `ceh-every-session`.
- **Check:** `python tools/validate-plugins/validate.py` exits 0 with the new fixtures in its hooks output,
  and each new fixture failed once with its assertion inverted. With one
  skill line changed to a `.md` path in one of this phase's folders it exits 1 naming that line.
- **Status:** done, `python tools/validate-plugins/validate.py`: "OK: all plugin checks passed". With good and
  bad swapped, all eight render and block pairs failed, among them 154-155, 157-158, 160-161
  and 163-164 for this phase. With `.agents_workspace/product/stress-tests/<topic>.md`
  appended to `stress-test-plan/SKILL.md` it failed once: "SKILL.md:71: the .md path of a
  YAML format". The Readers grep found no reader of the three formats. `test-audit/v2` keeps the findings
  worst first and `fixed` present only in fix mode, both checked. `stress-test/v2` splits
  each open question into `state` (`assumed` or `blocked`) and `detail`. `docs/CATALOG.md` and
  the READMEs name no path of these formats, so they needed no change.

### Phase 3: Learning record, blog draft and repurposed post

- **Builds:** learning/v2 in `explain-until-understood`, blog-draft/v2 in `draft-post` and `edit-post` (the
  model copied into both, as `blog-voice-model.py` is), repurposed-post/v2 in `repurpose-post`.
  Their readers. Hook fixtures, `.md` patterns, rule lists, `docs/CROSS_REFERENCES.md`,
  `docs/CATALOG.md`, `docs/ENVIRONMENT_VARIABLES.md`, READMEs, changelog, PATCH bumps of `ceh-codebase-explanation`,
  `ceh-blog-and-seo`.
- **Check:** `python tools/validate-plugins/validate.py` exits 0 with the new fixtures in its hooks output,
  and each new fixture failed once with its assertion inverted. With one
  skill line changed to a `.md` path in one of this phase's folders it exits 1 naming that line.
- **Status:** done, `python tools/validate-plugins/validate.py`: "OK: all plugin checks passed". With good and
  bad swapped, all eleven render and block pairs failed (22 failures), the three new pairs
  among them. With `.agents_workspace/product/blog/<slug>-thread.md` appended to
  `repurpose-post/SKILL.md` it failed once: "SKILL.md:157: the .md path of a YAML format". `repurpose-post` also carries the blog-draft schema, model and both templates, since it
  reads a post's content, per the Readers decision, and `explain-until-understood` checks its
  record on load. `blog-draft/v2` allows `status: published` beside `draft`, because
  `edit-post` now replaces a tracked live post's front matter with the format's. A learning
  record's self-test `date` is null exactly while the question is `not asked`, rendered `—`.
  `docs/CATALOG.md` names no path of these formats, so it needed no change.

### Phase 4: Code review and period retro, with hooks in ceh-git-workflow

- **Builds:** The three scripts in `ceh-git-workflow/scripts/` and their two hook entries. code-review/v2 in
  `code-review`, period-retro/v3 in `review-recent-work`, each with model, YAML template, schema
  update, `artifact.py` copy and skill-body steps. Their readers, among them
  `review-recent-work` itself and `docs/RETRO_WORKFLOW.md`. Hook fixtures for both formats and
  for the guard denying an edit to a rendered `.md` in this plugin. `.md` patterns, rule lists,
  `docs/CROSS_REFERENCES.md`, `docs/CATALOG.md`, `docs/ENVIRONMENT_VARIABLES.md`, README, changelog, PATCH bump of
  `ceh-git-workflow`.
- **Check:** `python tools/validate-plugins/validate.py` exits 0 with the new fixtures in its hooks output,
  the existing workspace sync fixtures still pass, and each new fixture failed once with its
  assertion inverted. With one
  skill line changed to a `.md` path in one of this phase's folders it exits 1 naming that line.
- **Status:** done, `python tools/validate-plugins/validate.py`: "OK: all plugin checks passed", the workspace
  sync fixtures among the passing hooks fixtures (only `.sh` fixtures skip without Git Bash).
  With good and bad swapped, the code-review and period-retro pairs (154-155, 157-158)
  failed, and the guard fixture failed with its expected text changed. With
  `.agents_workspace/product/retros/<YYYYMMDD-HHMMSS>-<session-id>-period.md` appended to
  `review-recent-work/SKILL.md` it failed once: "SKILL.md:93: the .md path of a YAML format". `code-review/v2` keeps the summary, with its Against the spec and Dismissed lists, as one
  Markdown block, and adds `verdict_detail` for the text after the verdict. `period-retro/v3`
  stores `status` and `status_detail` apart, and caps `issues` at three. The README gains an
  Artifact hooks section and the uv prerequisite, and `docs/RETRO_WORKFLOW.md` names the
  `.yaml` for the period retro. `docs/CATALOG.md` names no path of these formats.

### Phase 5: Session retro, with hooks in ceh-session-learning

- **Builds:** The three scripts in `ceh-session-learning/scripts/` and a new `hooks/hooks.json`.
  session-retro/v3 in `diagnose-session`, with model, YAML template, schema update, `artifact.py`
  copy and skill-body steps, and the Sharing step scrubbing the rendered `.md` into
  `<report>-shareable.md` without the `generated_from` and `generated_note` keys. Its readers
  and `docs/RETRO_WORKFLOW.md`. Hook fixtures, among them the guard allowing an edit to that
  copy, the `.md`
  pattern, the rewritten `checks/artifact_paths.py` docstring, rule lists,
  `docs/CROSS_REFERENCES.md`, `docs/CATALOG.md`, `docs/ENVIRONMENT_VARIABLES.md`, README, changelog, PATCH bump of
  `ceh-session-learning`.
- **Check:** `python tools/validate-plugins/validate.py` exits 0 with the new fixtures in its hooks output,
  each new fixture failed once with its assertion inverted, with one skill line changed to
  `.agents_workspace/product/retros/<name>-session.md` it exits 1 naming that line, and
  `grep -rnE "schema: (plan-review|code-review|refactor-report|stress-test|test-audit|business-plan-review|investor-deck|investor-outreach|blog-draft|repurposed-post|learning)/v1|schema: (period|session)-retro/v2" plugins/standalone --include=*.template.md`
  prints nothing.
- **Status:** done, `python tools/validate-plugins/validate.py`: "OK: all plugin checks passed". With good and
  bad swapped, the session-retro pair (154-155) failed, and the two guard fixtures (157-158,
  rendered `.md` denied, `-shareable.md` allowed) failed with their expected text changed.
  With `.agents_workspace/product/retros/<name>-session.md` appended to
  `diagnose-session/SKILL.md` it failed once: "SKILL.md:102: the .md path of a YAML format".
  The template grep printed nothing (exit 1). The `.md` pattern skips a path ending `-shareable.md`, since that copy is Markdown on
  purpose. `session-retro/v3` names the root cause class `kind`, as `period-retro/v3` does,
  and needs at least two chain steps. `docs/CROSS_REFERENCES.md` "Retro routing and report
  location" still named `.md` and the v2 templates after Phase 4, and is fixed here.

## Open

- A blog draft's and an investor email's rendered Markdown carry `generated_from`, a
  `generated_note` and a prettier-ignore range, which a person copying the text out must leave
  behind. Is that acceptable for text meant to be pasted elsewhere?: Yes. The body sits between the markers unchanged, and the user decided on 2026-11-14 that a
  post in a blog repo is rendered this way too, its front matter replaced by the format's. If
  pasting or a blog's site build proves awkward, the renderer can emit the body alone, in a
  later plan.

## Record

- 2026-11-14 Planned: status ready. The user reviews it, so no review-build-plan run.
- 2026-11-14 PR: #294 https://github.com/cheneeheng/ceh-claude-code-library/pull/294
- 2026-11-14 Reviewed: Revise first, 2 blocking (blog files saved beside a post on disk have no decided format; the
  shareable retro copy keeps `generated_from`, so the guard denies its scrub fixes)
- 2026-11-15 Built Phase 1: plan-review/v2, business-plan-review/v2, investor-deck/v2 and investor-outreach/v2, with
  their `.md` patterns and hook fixtures. validate.py passes.
- 2026-11-15 Built Phase 2: refactor-report/v2, test-audit/v2 and stress-test/v2, with `artifact.py` copied into each
  skill, their `.md` patterns and hook fixtures. validate.py passes.
- 2026-11-15 Built Phase 3: learning/v2, blog-draft/v2 (in `draft-post`, `edit-post` and `repurpose-post`) and
  repurposed-post/v2, with their `.md` patterns and hook fixtures. validate.py passes.
- 2026-11-15 Built Phase 4: The artifact hooks in `ceh-git-workflow`, code-review/v2 and period-retro/v3, with their
  `.md` patterns and hook fixtures. validate.py passes.
- 2026-11-15 Built Phase 5: The artifact hooks in `ceh-session-learning`, session-retro/v3 and the shareable copy
  without generated keys, with the `.md` pattern and hook fixtures. validate.py passes. Plan
  built. The user checks the build against the plan, so no Checked line from this session.
- 2026-11-15 PR: #296 https://github.com/cheneeheng/ceh-claude-code-library/pull/296
- 2026-11-15 Checked: 27 Built, 1 Gap, 1 Deviation, 1 Cannot verify, 2 Extra. Gap: the hook sections of the
  `ceh-coding-conduct`, `ceh-testing`, `ceh-every-session`, `ceh-product-direction` and
  `ceh-codebase-explanation` READMEs did not name their new formats. Deviation:
  `explain-until-understood` read its saved learning record without `artifact.py check`.
  Cannot verify: Out "Running eval cases", which the code cannot show. Extra: the Key Decision
  "Every format a skill saves has a YAML source" in `product/ARCHITECTURE.yaml`, and
  `status: published` in `blog-draft/v2`. The Gap and the Deviation are fixed on the branch
  `docs/markdown-formats-yaml-check-fixes`, on the user's request.
- 2026-11-15 Checked: 29 Built, 1 Cannot verify, 2 Extra, on `docs/markdown-formats-yaml-check-fixes`. The five
  READMEs now name their new formats, and `explain-until-understood` runs `artifact.py check`
  before reading a saved record. Cannot verify: Out "Running eval cases". Extra, unchanged:
  the Key Decision "Every format a skill saves has a YAML source" in
  `product/ARCHITECTURE.yaml`, and `status: published` in `blog-draft/v2`.

<!-- prettier-ignore-end -->
