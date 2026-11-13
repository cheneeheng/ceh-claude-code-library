---
schema: plan/v2
generated_from: handoff-leftovers.yaml
generated_note: "Do not edit. artifact.py renders this file from handoff-leftovers.yaml: edit the YAML, then run artifact.py render."
title: Close the leftovers the 2026-11-12 handoffs left open
status: building
created: 2026-11-13
---

<!-- prettier-ignore-start -->

## Goal

The handoffs of sessions ff98dab3 and 10f213e1 left four items open after their plans were
marked built: two advisory build-check findings in the YAML artifact tooling, the unbuilt
tester-agent pass-through from `plugin-audit-findings` Phase 3, and four `ceh-web-frontend`
descriptions still worded "Auto-load when". This plan closes all four, one PR per phase. A fifth
advisory finding, the loose rendering of a multi-paragraph glossary definition, is closed with
them, and so is the backslash-before-pipe loss the user asked to fix in every table-cell model,
not only `repeat-mistake`.

## Scope

**In:**

- `generated-md-guard.py`, all 13 byte-identical copies, resolves a relative `file_path`
  against the payload `cwd`, as `artifact-render-hook.py` already does.
- `repeat-mistake-model.py` `_cell` keeps a source backslash written before a pipe, so a
  source `\|` displays as `\|` in the rendered table instead of `|`.
- The ten other models with a table-cell escaper, 22 files in eight plugins, take the same
  escaper as `repeat-mistake`.
- `glossary-model.py`, both copies, rejects a `definition` or `question` that holds a blank
  line, and `glossary-schema.md`, both copies, says each is one paragraph.
- The descriptions of `make-ui-accessible`, `write-react-vite-code`, `write-sveltekit-code`
  and `write-vitest-playwright-tests` in `ceh-web-frontend` say "Trigger on" where they say
  "Auto-load when".
- `ceh-testing/scripts/skill-started-guard.py` lets one of the six tester agents write its own
  test files, if one dispatch of `pytest-unit-tester` shows the guard denies it today.
- Each phase's PATCH bumps, `CHANGELOG.md` entry, `docs/PLUGIN_VERSIONS.md` rows and
  `tools/validate-plugins/checks/hooks.py` fixtures.

**Out:**

- The live check of the v2 formats in real sessions: It needs the user's own sessions with the updated plugins installed, and no code changes
  unless it finds a failure, which would get its own fix record.
- The plugin audit's two leftovers: "or a blog interview" in `docs/VISION.md` line 62, and
  the series assumption in `draft-post` step 1 and the `ceh-blog-and-seo` README.: The user chose on 2026-11-13 to land each as its own small PR outside this plan. The
  vision asks for its own PR, and both are one-paragraph wording edits with nothing to
  build or check beyond `validate.py`.
- The other advisory notes in the three build-check reports: The `maintain-glossary` description silent on the YAML, a duplicate id reported at the
  top level, and model-enforced conversion rules were not carried into any handoff as open
  work, and each reviewer called them advisory.
- The `usage-limit-watch.py` notice: The user chose neither fix in `plugin-audit-findings`, and its Open keeps it there.
- A rule that bans "Auto-load when" in descriptions: Four strings are fixed by hand, and a grep in the Check proves none is left.

## Design

- **Guard paths:** In `main()` of `generated-md-guard.py`, the line
  `file = Path(payload.get("tool_input", {}).get("file_path", ""))` becomes the three lines
  `artifact-render-hook.py` uses at lines 102 to 106:
  `path = payload.get("tool_input", {}).get("file_path", "")`,
  `root = Path(payload.get("cwd") or os.getcwd()).resolve()` and
  `file = (root / path).resolve() if path else Path()`. An
  absolute `file_path` is unchanged by the join. The canonical copy is the `ceh-build-plan`
  one in `docs/CROSS_REFERENCES.md`, and the other 12 are copied from it, so the `copies`
  check stays green.
- **Table cells:** `_cell` in `repeat-mistake-model.py` writes a backslash that stands before a pipe as
  `&#92;`, then escapes every pipe:
  `text.strip().replace("\\|", "&#92;|").replace("|", "\\|")` replaces the lookbehind
  `re.sub(..., text.strip())`, keeping its `.strip()` so the unstripped `Text` fields
  (`evidence`, `fix`, `why_rung`) get no trailing `<br>`, and the `<br>` line stays. A markdown-it-py render on
  2026-11-13 showed `a &#92;\| b` displaying as `a \| b` in its cell, with the row still
  split into its two cells. The model version stays `repeat-mistake/v2`, because the YAML
  it accepts is unchanged.
- **Table cells in the other ten models:** Each escaper keeps its own input handling (`(text or "")` in `evidence`, no strip where it
  had none) and replaces only its pipe step with the `repeat-mistake` one,
  `.replace("\\|", "&#92;|").replace("|", "\\|")`:

  - `_cell` in `evidence-model.py` (3 copies), `fix-record-model.py` (2),
    `competitor-report-model.py` (2, the lookbehind form), `security-audit-model.py` (2),
    `qa-report-model.py` (2), `perf-report-model.py` (2), `error-messages-audit-model.py`
    (2), `interface-audit-model.py` (2), `first-run-audit-model.py` (2).
  - `_row` in `strategy-model.py` (3), where `c.replace("|", "\\|")` becomes
    `c.replace("\\|", "&#92;|").replace("|", "\\|")`.

  For each model the copy `docs/CROSS_REFERENCES.md` names canonical is edited first, then
  copied over the others, so the `copies` check stays green. No format version changes, since
  the YAML each accepts is unchanged. The eight plugins carrying them are `ceh-blog-and-seo`,
  `ceh-build-plan`, `ceh-coding-conduct`, `ceh-competitor-analysis`,
  `ceh-product-direction`, `ceh-security-audit`, `ceh-testing` and `ceh-usability-audit`.
- **Glossary paragraphs:** `glossary-model.py` gains a `Paragraph` type, a `Block` that rejects a blank line
  (a line holding only whitespace counts as blank), with the error text
  `one paragraph: remove the blank line`. `Entry.definition` and `OpenTerm.question` take it.
  `notes` stays a `Block`, because it renders under its own heading where paragraphs are
  fine. The version stays `glossary/v2`: a saved glossary with a blank line in a definition
  now fails its check, and the check's error names the field, which is how the writer fixes
  it. The two lines of `glossary-schema.md` that describe `definition` and `question` add
  "one paragraph, no blank line". The canonical copies are the `ceh-codebase-explanation`
  ones, mirrored into `record-project-decisions`.
- **Descriptions:** Each of the four descriptions keeps its first sentence and its second becomes, matching
  `configure-bun-vite-env`:

  - `make-ui-accessible`: "Trigger on the HTML structure of a .svelte or .tsx file being
    written."
  - `write-react-vite-code`: "Trigger on a .tsx file or vite.config.ts created or modified."
  - `write-sveltekit-code`: "Trigger on a +page.svelte, +page.server.ts, +page.ts,
    shared-state .svelte.ts module, or component file created or modified."
  - `write-vitest-playwright-tests`: "Trigger on a .test.ts, .test.tsx, or .spec.ts file
    created or modified."

  Each stays a `>-` scalar under 300 characters.
- **Tester pass-through:** First, one session started with `claude` from inside a scratch project as its cwd, with
  `ceh-testing` and `ceh-python-service` installed from this repo and no testing skill
  started. The guard skips an absolute path outside the payload `cwd`, and passes when the
  transcript it reads holds a started owning skill, so either would let the dispatch pass
  without the guard applying. Control first: a main-session Write of the relative path
  `tests/test_x.py` must be denied, which proves the guard is live. Then one dispatch of
  `ceh-python-service:pytest-unit-tester`, asked to write the relative path
  `tests/test_scratch.py`. It is a real model call, approved by the user on 2026-11-13 to
  run when the build reaches this phase. The building session runs it as one
  `claude -p` from the scratch project with both plugins loaded from this repo's folders
  (`--plugin-dir`, confirmed in `claude --help` first), its prompt asking for the control
  Write and then the dispatch, and reads the run's transcript. If the
  control is not denied, the run proves nothing and is redone. If the dispatch's Write goes
  through after a denied control, the phase records both transcript lines and changes no
  code. If it is denied by `skill-started-guard`, `main()` returns before the
  rules when the payload's `agent_type`, after its last `:`, is one of `pytest-unit-tester`,
  `pytest-integration-tester`, `pytest-system-tester`, `vitest-unit-tester`,
  `vitest-integration-tester` or `playwright-system-tester`, as `bulk-read-guard.py` returns
  for `bulk-reader`. Each of the six preloads a testing skill the rule names, so letting it
  through keeps the rule's intent.
- **Versions and landing:** One PR per phase, each a PATCH bump of every plugin it touches, in `plugin.json`,
  `marketplace.json` and `docs/PLUGIN_VERSIONS.md`, with a `CHANGELOG.md` entry under the
  PR's dated section. Versions on `main` on 2026-11-13: `ceh-every-session` 2.9.12,
  `ceh-codebase-explanation` 1.3.8, `ceh-web-frontend` 1.3.5, `ceh-testing` 1.6.16. A phase
  bumps from whatever `main` holds when it is built.

## Phases

### Phase 1: The generated-Markdown guard resolves relative paths

- **Builds:** A fixture in `checks/hooks.py`, seen red first, that runs
  `ceh-build-plan/generated-md-guard.py` on the existing `plans / "gen.md"`
  (`hooks.py:283`) by the relative path, `edit("gen.md", cwd=str(plans))`, with `out`
  `gen.yaml`. Then the three-line change (`path = ...`, `root = ...`, `file = ...`, as at
  lines 103 to 106 of `artifact-render-hook.py`) in the canonical copy, the 12 copies, and PATCH bumps of the 13 carriers: `ceh-blog-and-seo`, `ceh-build-plan`,
  `ceh-check-build-against-plan`, `ceh-codebase-explanation`, `ceh-coding-conduct`,
  `ceh-competitor-analysis`, `ceh-every-session`, `ceh-product-direction`,
  `ceh-security-audit`, `ceh-testing`, `ceh-usability-audit`, `ceh-workflow-builder`,
  `ceh-workflow-runner`.
- **Check:** Before the change, `python tools/validate-plugins/validate.py` fails on the new fixture.
  After it, the same command prints `OK: all plugin checks passed`, and
  `md5sum $(find plugins -name generated-md-guard.py) | awk '{print $1}' | sort -u | wc -l`
  prints 1.
- **Status:** done, Before the change, `python tools/validate-plugins/validate.py` failed on the new fixture in
  each plugin's `artifact_fixtures` group ("stdout lacks 'gen.yaml'"). After it, the same
  command printed "OK: all plugin checks passed", and the md5 count printed 1.

### Phase 2: Repeat-mistake table cells keep a backslash before a pipe

- **Builds:** A fixture rendering a repeat-mistake YAML whose `mistake` holds `a \| b`, with an `after`
  check that the rendered row holds `a &#92;\| b`, seen red first. Then the `_cell` change
  and the `ceh-every-session` PATCH bump.
- **Check:** `python tools/validate-plugins/validate.py` fails on the fixture before the change and
  prints `OK: all plugin checks passed` after it.
- **Status:** todo

### Phase 3: The other ten table-cell models keep a backslash before a pipe

- **Builds:** A fixture in the `have_uv` group rendering a fix record YAML (`good_fix` at
  `hooks.py:518`) whose `diagnosis.rows` `hypothesis` holds `a \| b`,
  with an `after` check that the rendered `.md` holds `a &#92;\| b`, seen red first. Then
  the escaper change in all 22 files under Design, and PATCH bumps of the eight plugins.
- **Check:** `python tools/validate-plugins/validate.py` fails on the fixture before the change and
  prints `OK: all plugin checks passed` after it, with the `copies` check included. After it,
  `grep -rnF --include='*-model.py' -e 'replace("|"' -e '(?<!' plugins | grep -v '&#92;'`
  prints nothing (it prints 23 lines on `main` on 2026-11-13: the 22 files and
  `repeat-mistake`).
- **Status:** todo

### Phase 4: Glossary definitions and questions are one paragraph

- **Builds:** A fixture in the `have_uv` group whose glossary `definition` holds a blank line, with `out`
  `entries.0.definition: Value error, one paragraph` (the shape `artifact.py` lines 98 to 99
  print), seen red first. Then `Paragraph` in both
  `glossary-model.py` copies, the line in both `glossary-schema.md` copies, and PATCH bumps
  of `ceh-codebase-explanation` and `ceh-every-session`.
- **Check:** `python tools/validate-plugins/validate.py` fails on the fixture before the change and
  prints `OK: all plugin checks passed` after it, with the `copies` check included.
- **Status:** todo

### Phase 5: Four web-frontend descriptions say "Trigger on"

- **Builds:** The four description edits, the `ceh-web-frontend` PATCH bump, and its `docs/CATALOG.md`
  rows if they quote the old wording.
- **Check:** `grep -rn "Auto-load when" plugins/standalone/ceh-web-frontend` prints nothing, and
  `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`.
- **Status:** todo

### Phase 6: Tester agents may write their own test files

- **Builds:** The control and dispatch run under Design. If denied: two fixtures in `checks/hooks.py`,
  a test-file Write with `agent_type` `ceh-python-service:pytest-unit-tester` expecting no
  output (seen red first) and the same Write with `agent_type` `general-purpose` still
  denied, then the early return and the `ceh-testing` PATCH bump. If allowed: the phase
  evidence quotes the transcript line, and nothing else changes.
- **Check:** The session transcript shows the control Write denied by `skill-started-guard`, then the
  dispatch's Write result. If code changed,
  `python tools/validate-plugins/validate.py` fails on the first fixture before the change and
  prints `OK: all plugin checks passed` after it.
- **Status:** todo. Holds the plan's one paid run, approved by the user on 2026-11-13, so it is built last.

## Open

None

## Record

- 2026-11-13 Planned: status ready
- 2026-11-13 Reviewed: Revise first, 1 blocking (Phase 5 dispatch can pass without the guard applying)
- 2026-11-13 Design changed: All five review findings fixed: Phase 5 runs from the scratch project with a denied control
  Write first, `_cell` keeps `.strip()`, the glossary fixture's `out` is one string, the four
  target descriptions are written out, and the Phase 1 fixture names its guard and file.
- 2026-11-13 Design changed: The user answered both Open questions: the escaper fix covers the ten other table-cell
  models (new Phase 3), and the paid dispatch runs when the build reaches it (now Phase 6).
  The vision and `draft-post` wording go to their own PRs, under Out.
- 2026-11-13 PR: #273 https://github.com/cheneeheng/ceh-claude-code-library/pull/273
- 2026-11-13 Built Phase 1: `python tools/validate-plugins/validate.py`, "OK: all plugin checks passed"
- 2026-11-13 PR: #275 https://github.com/cheneeheng/ceh-claude-code-library/pull/275

<!-- prettier-ignore-end -->
