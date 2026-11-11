---
schema: plan/v2
generated_from: repeat-mistake-yaml.yaml
generated_note: "Do not edit. artifact.py renders this file from repeat-mistake-yaml.yaml: edit the YAML, then run artifact.py render."
title: The repeat-mistake report as a YAML format, repeat-mistake/v2
status: ready
created: 2026-11-11
---

<!-- prettier-ignore-start -->

## Goal

Finish the repeat-mistake slice of Phase 6 of `product/plans/report-only-formats.yaml`.
`ceh-every-session:prevent-repeat-mistake` saves checked YAML and later sessions find every fix
still awaiting approval by key. Full drafts, evidence and proof stay with their mistakes as
statuses change, and repository fixes remain separate from machine-local fixes.

## Scope

**In:**

- repeat-mistake/v2, its model, YAML template, schema and renderer in prevent-repeat-mistake,
  preserving the table, rung reasons, full drafts, evidence and committed/local split.
- YAML-first pending-draft intake and append/update instructions, validation, legacy reads
  and lossless amendment conversion, without changing which fixes require approval.
- Existing artifact hooks extended to recognize schema-less report paths, fixtures,
  registered copies and documentation/version bookkeeping.

**Out:**

- Applying pending fixes, changing approval policy or bulk-converting past retros.: This plans a report format and grants no authority to apply its recorded fixes.
- Period/session retros, cross-session recurrence detection and plugin consolidation.: These are separate formats or workflows with independent goals.

## Design

- **Format and interface** Canonical skill is plugins/standalone/ceh-every-session/skills/prevent-repeat-mistake/.
  Add references/repeat-mistake-model.py, assets/repeat-mistake.template.yaml and
  scripts/artifact.py. Extend references/repeat-mistake-schema.md with v2, retaining v1
  and the Markdown layout template. Export NAME = "repeat-mistake", VERSION = 2, MODEL and
  render(doc, source) -> str. Strict pydantic types forbid extra keys and empty text.
  Required keys: schema (repeat-mistake/v2), date (a YAML date), other_file (null or a nonempty
  single-line path) and fixes (a nonempty list). A fix has id (unique positive integer within
  the file), mistake (nonempty single line), evidence (nonempty Markdown), rung (integer 1 to
  5), fix (nonempty Markdown), proof (the string "yes" or "not provable"), status (applied,
  awaiting approval or rejected), why_rung (nonempty text) and optional draft (nonempty
  Markdown). Awaiting approval requires a draft. Applied and rejected fixes may retain drafts
  for history. Rung 5 requires proof "not provable" because guidance cannot be proven by replay.
  Other rungs allow either proof value, preserving the v1 vocabulary without inventing proof.
  Optional top-level notes holds context or legacy prose unrelated to one fix. No pending count
  is stored. Quote "yes" in YAML so it remains a string.
- **Rendering, status and retries** Render the date title from doc.date, never the wall clock, then the seven-column table and
  Why this rung section. Escape pipes
  and line breaks in table cells while preserving source values. Reasons show id, mistake
  and why_rung. Pending drafts contains only awaiting approval fixes, heading <id>: <mistake>
  and full draft, or None. when empty. Retained applied/rejected drafts go under ## Previous
  drafts with status and id, never under pending. notes renders under ## Context before the
  table. Frontmatter has date, other_file (none for null), schema, generated_from and
  generated_note. Use the prettier-ignore wrapper and preserve draft code fences verbatim.
  Append with max(existing ids) + 1. Applying or rejecting updates that id's status while
  retaining draft and evidence. Retry updates the same id; retrying an append checks existing
  mistake and evidence first to avoid duplicates. The skill owns these writes. Concurrent
  agents must serialize updates to the same dated report, as for the current Markdown append
  workflow. Introduce no lock API.
- **Paths, intake and migration** Keep the split: product/retros/<YYYY-MM-DD>-repeat-mistake.yaml for repo fixes,
  .agents_workspace/product/retros/<YYYY-MM-DD>-repeat-mistake.yaml for outside fixes, with
  same-stem Markdown. When both exist, other_file is the repo-relative path of the other YAML,
  rendered as its Markdown counterpart. The skill checks existence and reciprocal links after
  both saves, not in the per-file model: the first save cannot require an uncreated second file.
  A local report does not authorize committing it or its drafts.
  Step 1 scans both folders, grouping YAML and Markdown by full stem within each folder.
  YAML wins. Check it, then select fixes with status awaiting approval and list id, mistake,
  fix and full draft before taking a new mistake. Markdown-only v1 remains readable.
  Before amending v1, carry all rows, reasons, drafts and context into v2, assigning ids in
  row order. Keep applied/rejected drafts too, as real reports do. Attach shared rung reasons
  to each relevant fix, and keep unmatched prose in notes. Never infer approval or proof from
  a draft's presence. A v1 status explicitly beginning applied, awaiting approval or rejected
  maps to that exact enum; preserve the full annotated legacy status in notes keyed by fix id.
  Match a differently worded draft heading to its row by the actual mistake and target files,
  not by exact heading equality. If its association or status is ambiguous, report it and
  leave the source untouched. Missing full drafts for pending v1 rows block conversion with a report,
  leaving the original untouched. Validate complete YAML before rendering. No bulk migration.
  Mask secrets as <secret> in committed evidence, drafts, notes and every other text field,
  preserving the existing rule. Shape validation cannot prove prose contains no secrets.
  Exit 1 stops use of that report and leaves intake explicitly incomplete, never claiming no
  pending work remains. Stale Markdown alone is rendered and reading continues. Exit 2 or 3,
  absent uv or denied execution is reported as unchecked. Writers render/check after final
  updates when hooks are disabled and report unavailable rendering. Reuse atomic Markdown
  replacement. An interrupted linked-pair update is reported as incomplete, not silently lost.
- **Hooks, copies and upkeep** ceh-every-session already carries both hooks. Extend canonical
  plugins/standalone/ceh-build-planning/scripts/artifact-render-hook.py place_format to match
  the exact dated repeat-mistake basename in either supported retros path relative to payload
  cwd, even without schema or Markdown. Preserve glossary and blog-voice matching if landed.
  Mirror every registered script copy, retain model_names gating and reuse the generic guard.
  Resolve relative tool_input.file_path against payload cwd before file-existence checks,
  format detection and CLI invocation; missing cwd retains process-cwd resolution. Match the
  resolved path against the two allowed directories rather than matching only the basename.
  Register the new skill CLI in docs/CROSS_REFERENCES.md. Update its split-retro-save entry
  for this skill's YAML behavior, leaving period/session formats unchanged. Add fixtures in
  tools/validate-plugins/checks/hooks.py. Update ceh-every-session/README.md, skill compatibility,
  docs/ENVIRONMENT_VARIABLES.md's format list, .claude/rules/decision-artifact-validation.md
  and decision-output-templates.md, dated CHANGELOG.md, the ceh-every-session PATCH version in
  plugin.json and .claude-plugin/marketplace.json, and docs/PLUGIN_VERSIONS.md.
  Every other plugin whose registered hook copy changes gets a PATCH bump in its manifest,
  marketplace entry and version table, with dated changelog coverage. Resolve versions at
  commit time. The core plugin already has hooks, so it gains no new hook-triggered MINOR.
  No new hook wiring or plugin dependency.

## Phases

### Phase 1: Build the report contract and approval-preserving intake

- **Builds:** All Scope In: format and render, writer and later-session reads, legacy amendment and
  deduplication instructions, hook location matching, fixtures and upkeep.
- **Check:** A scratch repeat-mistake/v2 fixture with pending, applied and rejected fixes passes
  `uv run --script plugins/standalone/ceh-every-session/skills/prevent-repeat-mistake/scripts/artifact.py render <fixture.yaml>`
  and check through that CLI. Assert only the pending id is under Pending drafts, history
  is under Previous drafts, fences survive and pipes do not split table cells. Changing the
  pending id to applied and rendering removes it from pending without losing draft/evidence;
  a repeat update adds no duplicate. Missing pending draft, duplicate id, rung 0, rung 5 with
  proof "yes", unknown status and extra-key copies exit 1 naming the field.
  Convert a scratch copy of product/retros/2026-11-11-repeat-mistake.md: both applied rows,
  shared reasons, context and historical drafts survive. Also convert a scratch copy of
  product/retros/2026-10-28-repeat-mistake.md: its annotated applied status maps to applied,
  the full annotation survives in notes and its differently worded draft heading attaches
  to the correct row. Assert the same doc.date renders identically on different days.
  A v1 pending row with no full draft
  refuses conversion without overwriting the original. A scratch intake assertion groups
  stems once, reads both locations and finds exactly the pending ids through MODEL.model_validate;
  resolve step 1's stated key paths through model_json_schema(), with a planted typo failing.
  Check reciprocal other_file links after both scratch files exist. Add and run hook fixtures
  for both schema-less paths, invalid status, valid render, generated-Markdown denial and
  unrelated retros YAML skipped. `python tools/validate-plugins/validate.py` is green as the
  implementation integration gate. No actual pending fix is applied by these checks.
  Include absolute and relative report paths with payload cwd different from process cwd,
  and a correctly named schema-less dated report outside both supported directories that
  must be skipped.
- **Status:** todo

## Open

- Should applied or rejected drafts be discarded during conversion?: No. Existing files retain them. Preserve them as history and select pending work strictly
  by status, avoiding evidence loss or accidental revival of an old approval request.

## Record

- 2026-11-11 Planned: status ready
- 2026-11-11 Reviewed: Revise first, 1 blocking (version policy) and 3 advisory (date determinism, decorated legacy
  statuses and draft associations, cwd/location fixtures). All fixed. Independent recheck:
  Ready to build, 0 residual findings.
  Review: .agents_workspace/product/plan-reviews/repeat-mistake-yaml-2026-11-11.md.

<!-- prettier-ignore-end -->
