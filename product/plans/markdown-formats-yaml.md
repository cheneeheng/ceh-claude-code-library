---
schema: plan/v2
generated_from: markdown-formats-yaml.yaml
generated_note: "Do not edit. artifact.py renders this file from markdown-formats-yaml.yaml: edit the YAML, then run artifact.py render."
title: The Markdown-only formats become YAML formats
status: ready
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
  `docs/CATALOG.md` and plugin README wording, a PATCH bump, a changelog entry and
  `docs/PLUGIN_VERSIONS.md` rows.

**Out:**

- Design variants: `design-ui` writes them as throwaway static HTML files, not Markdown, so there is no format
  to move. The consolidate plan's allowlist list names them, and they leave it unchanged.
- The session retro's `<report>-shareable.md`: It is a scrubbed copy of the rendered Markdown, made only when a report leaves the machine,
  and is the file handed to a person. It stays a Markdown copy of the rendered `.md`, now
  `<report>-shareable.md` beside the YAML's Markdown, and is not a format of its own.
- A post written into a blog repo: `blog-draft-schema.md` already says such a post follows that repo's own front matter. It is
  what the user ships, out of `decision-output-templates.md` by its own scope.
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
- **How the hook finds each file:** By its `schema:` key alone, which every template writes as its first line. No `place_format`
  entry is added: these files have no fixed name to match, and the writing skill runs the render
  itself, so a file missing its key fails that run in the same turn.
- **Hooks in the two plugins that have none:** `ceh-git-workflow` and `ceh-session-learning` get `scripts/artifact.py`,
  `scripts/artifact-render-hook.py` and `scripts/generated-md-guard.py`, copied from
  `ceh-build-plan`, and `PreToolUse` and `PostToolUse` entries on `Edit|Write|MultiEdit` as the
  other plugins wire them. `ceh-git-workflow` adds them next to its existing sync hooks in the
  same `hooks/hooks.json`. Neither joins `READERS`, because both write their formats.
- **Readers:** Each phase starts with `grep -rn "<schema>\|<folder>/" plugins/standalone` for its formats. A
  reader that only names the path, such as `review-recent-work` taking the date from a period
  retro's file name, changes the path to the `.yaml`. A reader that reads the content carries
  the model and `artifact.py` and runs `artifact.py check` first, falling back to the `.md` when
  no YAML exists.
- **The validator:** Each phase adds its formats' `.md` paths to `YAML_FORMAT_MD` in `checks/artifact_paths.py`, so
  a stale `.md` path fails in the same PR that adds the YAML. The phase that adds the last one
  rewrites the module docstring, which today points at the consolidate plan's exceptions.
- **Rule text:** Each phase appends its formats to the lists in `decision-artifact-validation.md` and
  `decision-output-templates.md`, citing this plan, as each earlier format plan did.

## Phases

### Phase 1: Plan review, business plan review and investor materials

- **Builds:** plan-review/v2 in `review-build-plan`, business-plan-review/v2 in `review-business-plan`,
  investor-deck/v2 and investor-outreach/v2 in `write-investor-materials`, each with model,
  YAML template, schema update, `artifact.py` copy and skill-body steps. Their readers, found by
  the Readers grep. Hook fixtures in `checks/hooks.py` for each format: a good file renders, a
  bad key is reported. The four `.md` patterns in `checks/artifact_paths.py`. Rule lists,
  `docs/CROSS_REFERENCES.md`, `docs/CATALOG.md`, READMEs, changelog, PATCH bumps of
  `ceh-build-plan` and `ceh-product-direction` and every reader plugin.
- **Check:** `python tools/validate-plugins/validate.py` exits 0 with the new fixtures in its hooks output,
  and each new fixture failed once with its assertion inverted. With one skill line changed to
  `.agents_workspace/product/plan-reviews/<slug>.md` it exits 1 naming that line.
- **Status:** todo

### Phase 2: Refactor report, test audit and stress test

- **Builds:** refactor-report/v2 in `refactor-repo`, test-audit/v2 in `audit-test-suite`, stress-test/v2 in
  `stress-test-plan`, each with model, YAML template, schema update, `artifact.py` copy and
  skill-body steps. Their readers. Hook fixtures, `.md` patterns, rule lists,
  `docs/CROSS_REFERENCES.md`, `docs/CATALOG.md`, READMEs, changelog, PATCH bumps of
  `ceh-coding-conduct`, `ceh-testing`, `ceh-every-session` and every reader plugin.
- **Check:** `python tools/validate-plugins/validate.py` exits 0 with the new fixtures in its hooks output,
  and each new fixture failed once with its assertion inverted.
- **Status:** todo

### Phase 3: Learning record, blog draft and repurposed post

- **Builds:** learning/v2 in `explain-until-understood`, blog-draft/v2 in `draft-post` and `edit-post` (the
  model copied into both, as `blog-voice-model.py` is), repurposed-post/v2 in `repurpose-post`.
  Their readers. Hook fixtures, `.md` patterns, rule lists, `docs/CROSS_REFERENCES.md`,
  `docs/CATALOG.md`, READMEs, changelog, PATCH bumps of `ceh-codebase-explanation`,
  `ceh-blog-and-seo` and every reader plugin.
- **Check:** `python tools/validate-plugins/validate.py` exits 0 with the new fixtures in its hooks output,
  and each new fixture failed once with its assertion inverted.
- **Status:** todo

### Phase 4: Code review and period retro, with hooks in ceh-git-workflow

- **Builds:** The three scripts in `ceh-git-workflow/scripts/` and their two hook entries. code-review/v2 in
  `code-review`, period-retro/v3 in `review-recent-work`, each with model, YAML template, schema
  update, `artifact.py` copy and skill-body steps. Their readers, among them
  `review-recent-work` itself and `docs/RETRO_WORKFLOW.md`. Hook fixtures for both formats and
  for the guard denying an edit to a rendered `.md` in this plugin. `.md` patterns, rule lists,
  `docs/CROSS_REFERENCES.md`, `docs/CATALOG.md`, README, changelog, PATCH bump of
  `ceh-git-workflow` and every reader plugin.
- **Check:** `python tools/validate-plugins/validate.py` exits 0 with the new fixtures in its hooks output,
  the existing workspace sync fixtures still pass, and each new fixture failed once with its
  assertion inverted.
- **Status:** todo

### Phase 5: Session retro, with hooks in ceh-session-learning

- **Builds:** The three scripts in `ceh-session-learning/scripts/` and a new `hooks/hooks.json`.
  session-retro/v3 in `diagnose-session`, with model, YAML template, schema update, `artifact.py`
  copy and skill-body steps, and the Sharing step scrubbing the rendered `.md` into
  `<report>-shareable.md`. Its readers and `docs/RETRO_WORKFLOW.md`. Hook fixtures, the `.md`
  pattern, the rewritten `checks/artifact_paths.py` docstring, rule lists,
  `docs/CROSS_REFERENCES.md`, `docs/CATALOG.md`, README, changelog, PATCH bump of
  `ceh-session-learning` and every reader plugin.
- **Check:** `python tools/validate-plugins/validate.py` exits 0 with the new fixtures in its hooks output,
  each new fixture failed once with its assertion inverted, and
  `grep -rnE "schema: (plan-review|code-review|refactor-report|stress-test|test-audit|business-plan-review|investor-deck|investor-outreach|blog-draft|repurposed-post|learning)/v1|schema: (period|session)-retro/v2" plugins/standalone --include=*.template.md`
  prints nothing.
- **Status:** todo

## Open

- A blog draft's and an investor email's rendered Markdown carry `generated_from`, a
  `generated_note` and a prettier-ignore range, which a person copying the text out must leave
  behind. Is that acceptable for text meant to be pasted elsewhere?: Yes. The body sits between the markers unchanged, and `blog-draft-schema.md` already sends a
  post meant for a blog repo to that repo's front matter. If pasting proves awkward, the
  renderer can emit the body alone, in a later plan.
- Does any reader skill read one of these formats' content, not only its path?: Unknown until each phase's Readers grep. The design covers both cases, so the answer changes
  the files a phase copies, not the plan.

## Record

- 2026-11-14 Planned: status ready. The user reviews it, so no review-build-plan run.

<!-- prettier-ignore-end -->
