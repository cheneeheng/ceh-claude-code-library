---
schema: plan/v1
title: Three skills gain a form a calling program sets, for Nightshift's intake
status: built
created: 2026-11-06
---

## Goal

Three skills each gain one optional form that a calling program sets, so a scheduled `claude -p`
session can ask through a GitHub issue, finish a plan another step drafted, and keep its state in
one fixed file. A session that passes none of the new arguments behaves exactly as today. The
first caller is Nightshift's slice 2, `product/plans/first-job-2-commission-and-plan.md` in
`ceh-nightshift`, whose page `product/proposal/06-skills-hooks-scripts.md` gives each behavior.

## Scope

**In:**

- `write-questionnaire write --issue <owner/repo> --labels <list>` posts the questionnaire as an
  issue body and reports the issue number, with no local file. `read --issue <owner/repo>#<n>`
  reads the `Answer:` lines from the body and the comments, the newest per question winning, a
  blank one still open.
- `write-build-plan <path>`, given an existing `status: draft` plan, completes that plan in place
  and keeps its goal and every Scope In item word for word.
- `hand-off-session save --file <path>` overwrites that one file and writes no index line. It
  writes the extra fields the caller names after `**Session:**`, and load reads them back. When the
  caller names a place for decisions, a pending decision goes there, not to the user.
- Each change in its own PR, with its PATCH bump, README and CATALOG cells, changelog entry and
  `docs/PLUGIN_VERSIONS.md` row.

**Out:**

- `write-build-plan`'s revise mode: Nightshift's slice 5 needs it, and only after a failed Verify.
- A `--title` for the issue form: Nightshift finds its questions by label, so the title stays
  `Questions on <topic>`, the questionnaire's own heading.
- Creating missing labels: the caller's repository owns its labels. A missing one fails `gh` and
  the skill reports the error.
- Nightshift's own documents: its slice 2 plan writes the draft as `<slug>.yaml`, its
  `templates/github-issues.md` titles become `Questions on <topic>` with the issue-form intro, and
  its `templates/job-folder.md` moves `**Open questions:**` up under `**Exit:**`. They change in
  `ceh-nightshift`, as its own PR.
- Any other skill on page 06 (`implement-from-plan --skip-check`, the decision-log v2 template,
  `record-project-decisions`, `check-build-against-plan` on a Fix record, `pull-request`): later
  Nightshift slices name them.

## Design

**Shared rule.** Every new form is set by an argument the caller passes. Nothing infers it from the
runtime, because a skill cannot see the `-p` flag, and a guess would change a watched session.

**`write-questionnaire`, issue form** (`plugins/standalone/ceh-every-session/skills/write-questionnaire/`):

- `argument-hint` becomes `"[write [--issue <owner/repo> --labels <list>] | read [path | --issue <owner/repo>#<n>]]"`.
- Write step 5 gains a second branch. With `--issue`, the body is the same filled template,
  frontmatter included, so the issue holds the `questionnaire/v1` file a reader can tell by its
  schema line. It is posted with
  `gh issue create --repo <owner/repo> --title "Questions on <topic>" --label <list> --body-file -`,
  the body on stdin, and the skill reports the number from the URL `gh` prints, plus the question
  count. No file is saved.
- `--issue` selects the issue form. It grants nothing: posting rests on a human's advance
  authorization for that class of action in the session's context (a launch prompt or a user
  instruction to open issues in that repo), per VISION "Autonomy and its limits", because a calling
  agent cannot widen what the agent may do ("Who overrides"). With no such authorization in
  context, the skill posts nothing and reports why. The rule "Writing the file sends nothing"
  stays for the file form, with one added sentence naming the issue form and its authorization.
- When `gh` is missing or fails (no auth, a missing label), the skill reports the `gh` error and
  posts nothing, and saves no file either, because a caller that asked for an issue reads its
  number, and a silent local file would leave the question unasked. The skill never retries
  `gh issue create`: on an error after the call, it reports that the issue may exist and that the
  caller should look for it by label, because a second issue would ask twice. Deduplication stays
  with the caller, which keeps the issue number.
- The issue form's intro line is, word for word: "From: <asker>, YYYY-MM-DD. Answer on the
  `Answer:` line under each question, here or in a comment as `Answer <n>: <text>`. Leave a line
  blank to skip it." It lives in the SKILL.md Write step 5 branch and is quoted in the schema's
  Issue form paragraph, while the template keeps the file form's line. A comment is not under any
  question heading, so the answerer must be told the `Answer <n>:` shape, or a bare "A" is ignored.
- Read with `--issue`: `gh issue view <n> --repo <owner/repo> --json body,comments`. For each
  question, the answer is the newest of its body `**Answer:**` line and every comment's
  `Answer <n>:` line, by comment time, the body counting as oldest. A blank newest answer is still
  open. The rest of Read (apply in order, list what is open, never fill a blank with the default)
  stays.
- `references/questionnaire-schema.md` gains an "Issue form" paragraph: the same body as an issue,
  the comment answer line, and the newest-wins rule. The schema stays `questionnaire/v1`, because
  the file's shape does not change.

**`write-build-plan`, draft completion** (`plugins/standalone/ceh-build-planning/skills/write-build-plan/SKILL.md`):

- `argument-hint` becomes `"[what to build | <draft plan path>]"`.
- A new paragraph after the opening one: given the path of a `plan/v2` YAML plan with
  `status: draft`, or of a `.md` whose frontmatter has `generated_from: <slug>.yaml` (which
  resolves to that YAML), the skill completes that plan in place. Its goal and every Scope In item
  stay word for word, and more In items may be added after them. Its Design entries, Open items and
  Record are kept, and step 5 adds entries after them. Its `unplanned` phases are replaced by the
  phases step 6 writes. Every step still runs, and step 7 saves to the same YAML, renders its
  Markdown, and appends `Planned: status <ready or draft>`.
- The caller writes the draft's first Record entry, `Planned: status draft`, because `plan/v2`
  needs at least one entry. Completion appends a second Planned entry, so the trail shows both the
  draft and the completion.
- A path to a `plan/v1` Markdown plan with no YAML beside it, or to a plan that is not `draft`, is
  not a completable draft: the reply says so and a new plan is written as today.
- The Rules line "One plan per request" gains: "A draft passed by path is completed, not written
  again."
- No change to the model, the template or `artifact.py`, because a draft already validates: a
  caller writes one Design entry, one `unplanned` phase and one Planned entry, which `plan/v2`
  allows. The caller's side, Nightshift writing `<slug>.yaml` instead of `<slug>.md`, changes in
  `ceh-nightshift`.

**`hand-off-session`, fixed file** (`plugins/standalone/ceh-every-session/skills/hand-off-session/`):

- `argument-hint` (today `[save | load [path]]`) becomes `"[save [--file <path>] | load [path]]"`.
- Save step 3: with `--file <path>`, write to that path, overwriting it. Step 4: with `--file`, no
  index line, because the caller knows where the file is and an index line per save would grow
  without bound.
- Caller fields: a caller names extra fields and their values in its request prose, the same way
  it passes header lines today, for example "save --file .nightshift/jobs/J/state.md with fields
  Plan: product/plans/x.yaml, PR: none yet, decisions go to the Decision log". Each field is a
  `**<Field>:** <value>` line directly after `**Session:**`, in the order named. Load step 3
  reports each one beside the goal. Header lines stay as they are, under the title, because load
  does not report them: they say why the file was saved, while fields are state the caller resumes
  from. The schema stays `handoff/v1`, because a reader that ignores the lines loses nothing.
- Decisions: when the caller names a place for decisions (a file or a skill), Decisions pending
  lists each pending fork as usual and ends with `, forks go to <place>`, and reads
  `none, forks go to <place>` only when nothing is pending. Load step 4 sends each listed fork that
  blocks the first Open item to that place instead of the user: it writes the fork to the file
  named, or invokes the skill named with it.
- The rule "Saving does not end the session ... each save is a new file" gains: "except with
  `--file`, which overwrites its one file".
- `references/handoff-schema.md` gains the caller fields line and the `--file` path.

**Versions.** PATCH each, because each is content in an existing skill: `ceh-every-session`
2.8.19 to 2.8.20 for the issue form and 2.8.21 for the fixed file, `ceh-build-planning` 1.2.2 to
1.2.3.

### Vision check (`docs/VISION.md`)

| Section                                       | Verdict | Reason                                                                                                    |
| --------------------------------------------- | ------- | --------------------------------------------------------------------------------------------------------- |
| Agents first, "no human watching"             | passes  | Each form exists so a session nobody watches can ask, plan and resume.                                    |
| Autonomy and its limits, outward-facing       | passes  | `--issue` selects the form. Posting needs a human's advance authorization in context, else nothing posts. |
| Principle 6, one use case, one install        | passes  | No new plugin dependency. `gh` is needed only by the issue form, and its absence is reported.             |
| Principle 7, guide first, enforce on evidence | passes  | Prose only, no new hook.                                                                                  |
| Principle 9, small surface, sharp edges       | passes  | One optional argument per skill, and nothing changes when it is not passed.                               |

No change to `docs/VISION.md` is needed.

## Phases

### Phase 1: The issue form of `write-questionnaire`

- **Builds:** the SKILL.md argument-hint, Write step 5 branch, Read `--issue` branch and rule
  sentence, the schema's Issue form paragraph, the plugin README row and invocation line, the
  CATALOG Invoke cell, and the registration: 2.8.20 in `plugin.json`, `marketplace.json` and
  `docs/PLUGIN_VERSIONS.md`, and the `CHANGELOG.md` entry under the PR's date. This plan file is
  committed in this PR.
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`.
  `grep -c -- "--issue"` prints at least 3 for the SKILL.md and at least 1 for the schema, the
  plugin README and `docs/CATALOG.md`. `grep -c "Answer <n>:"` prints at least 2 for the SKILL.md
  and at least 1 for the schema.
  `grep -n "2.8.20" plugins/standalone/ceh-every-session/.claude-plugin/plugin.json .claude-plugin/marketplace.json docs/PLUGIN_VERSIONS.md CHANGELOG.md`
  prints at least one line per file.
- **Status:** done. `validate.py` printed `OK: all plugin checks passed`. `--issue` counts are 4, 2,
  2 and 1, `Answer <n>:` counts 2 and 2, and `2.8.20` is in all four files

### Phase 2: Draft completion in `write-build-plan`

- **Builds:** the SKILL.md argument-hint, the draft paragraph and the Rules sentence, the plugin
  README row and Manual trigger line, the CATALOG Invoke cell, and the registration at 1.2.3.
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`.
  `grep -c "generated_from"` on the SKILL.md is at least 1, and
  `grep -n "1.2.3" plugins/standalone/ceh-build-planning/.claude-plugin/plugin.json .claude-plugin/marketplace.json docs/PLUGIN_VERSIONS.md CHANGELOG.md`
  prints at least one line per file.
  A draft written as Nightshift writes it (goal, two In items, one Design entry, one `unplanned`
  phase, one Planned entry) passes
  `uv run --script plugins/standalone/ceh-build-planning/scripts/artifact.py check <draft>.yaml`.
- **Status:** done. `validate.py` printed `OK: all plugin checks passed`, `generated_from` is in the
  SKILL.md once, `1.2.3` is on the `ceh-build-planning` line in all four files, and a draft of
  "Add a usage section" in that shape exited 0 from `artifact.py check` and `render`. The plugin
  README row also changed `<slug>.md` to `<slug>.yaml`, because it was stale since `plan/v2`

### Phase 3: The fixed file of `hand-off-session`

- **Builds:** the SKILL.md argument-hint, Save steps 3 and 4, the caller fields, the decisions
  place, load steps 3 and 4, the rule sentence, the schema lines, the plugin README row and
  invocation line, the CATALOG Invoke cell, and the registration at 2.8.21.
- **Check:** `python tools/validate-plugins/validate.py` prints `OK: all plugin checks passed`.
  `grep -c -- "--file"` prints at least 3 for the SKILL.md and at least 1 for the schema, the
  plugin README and `docs/CATALOG.md`. `grep -c "forks go to"` prints at least 2 for the SKILL.md.
  `grep -n "2.8.21" plugins/standalone/ceh-every-session/.claude-plugin/plugin.json .claude-plugin/marketplace.json docs/PLUGIN_VERSIONS.md CHANGELOG.md`
  prints at least one line per file.
- **Status:** done. `validate.py` printed `OK: all plugin checks passed`. `--file` counts are 5, 1,
  2 and 1, `forks go to` is in the SKILL.md 3 times, and `2.8.21` is in all four files

## Open

- Whether a model follows each form in a real `claude -p` run: assumed it does. Nightshift's slice
  2 Phase 2 live run is the proof (a `question` issue posted, `state.md` written through
  `save --file`, a draft completed). It is a live model run, so it is not in these Checks.
- Whether GitHub renders the frontmatter lines readably in an issue body: assumed readable enough,
  since `date: ...` above the closing `---` shows as a heading. Nightshift's draft in
  `templates/github-issues.md` posts the same body, so the first live issue shows it.

## Record

- 2026-11-06 Planned: status ready
- 2026-11-06 Reviewed: Revise first, 4 blocking (draft format .md vs plan/v2 .yaml unsettled; Decisions pending "none" drops the forks load must route; --issue as caller authorization contradicts VISION Who overrides; comment answer format not told to the answerer), all fixed in the plan
- 2026-11-06 Built Phase 1: `python tools/validate-plugins/validate.py`, OK: all plugin checks passed
- 2026-11-06 PR: #207 https://github.com/cheneeheng/ceh-claude-code-library/pull/207
- 2026-11-06 Built Phase 2: `python tools/validate-plugins/validate.py`, OK: all plugin checks passed
- 2026-11-06 PR: #208 https://github.com/cheneeheng/ceh-claude-code-library/pull/208
- 2026-11-06 Built Phase 3: `python tools/validate-plugins/validate.py`, OK: all plugin checks passed
