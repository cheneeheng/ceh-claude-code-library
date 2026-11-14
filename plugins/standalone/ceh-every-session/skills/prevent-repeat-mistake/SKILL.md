---
name: prevent-repeat-mistake
description: >-
  Load this skill when a mistake must not happen again: pick the strongest fix that
  would have caught it (a setting or check before written guidance) and prove it on the real
  mistake. Trigger on "you did X again", "I keep telling you", "make sure this never happens again".
argument-hint: "[the mistake]"
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Uses uv, which runs scripts/artifact.py with Python 3.10+, pydantic 2 and PyYAML, to check and
  render the repeat-mistake report. Without uv it is read and written unchecked and unrendered.
license: Apache-2.0
---

# Prevent a repeat mistake

Turn a mistake that must not come back into a fix that stops it, placed at the strongest level that
works. The mistake may have repeated already, or a retro (`diagnose-session`, `review-recent-work`)
may have found it once and routed it here: either way, one occurrence quoted from evidence is
enough to start. The files can be anything: code, a knowledge base of notes, plans, a roadmap, a business
strategy. Done means each mistake has a fix that is either in place and proven, or drafted and
waiting for the user's approval.

## Procedure

1. **Pick up pending drafts.** In `.agents_workspace/product/retros/`, or the retros folder the
   repo's `CLAUDE.md` names, find
   every report named `<YYYYMMDD-HHMMSS>-<session-id>-repeat-mistake` or, in the older form,
   `<YYYY-MM-DD>-repeat-mistake`, `.yaml` or `.md`, and read each once, the YAML when there is
   one. A labelled name such as
   `<YYYY-MM-DD>-<label>-repeat-mistake.md`, with a label before `repeat-mistake`, is not a report. Before reading a YAML, run
   `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check <file>.yaml`. On exit 1, use
   nothing from that report, report its errors, and say the intake is incomplete, never that no
   fix is pending, unless the only error is a stale `.md`, which the same command with `render`
   repairs. On exit 2 or 3, without uv, or when the command is denied, say the report went unchecked, and read it anyway. List
   every fix still awaiting approval, `fixes[].status: awaiting approval` in a YAML, with its
   `fixes[].id`, `fixes[].mistake`, `fixes[].fix` and full `fixes[].draft`, before taking a new
   mistake, so a draft from an earlier session is not lost. A `v1` `.md` is read as it is.
2. **Name the mistake from evidence.** Quote what went wrong: the tool call, the file and line,
   the wrong output, and the correction that preceded it. "Was sloppy" is not a mistake, "wrote
   dates as `10/09/2026` in `roadmap.md:14` after being told ISO dates" is. If you cannot quote it,
   stop: there is nothing to fix yet. To find the mistakes in a whole session rather than one,
   `ceh-session-learning:diagnose-session` reads its transcript and routes each one here.
3. **Climb the ladder, strongest first.** Stop at the first rung that would have caught this exact
   mistake:

   | Rung                    | In code                                          | In notes, plans, or documents                                       |
   | ----------------------- | ------------------------------------------------ | ------------------------------------------------------------------- |
   | 1. Remove the cause     | Delete the second code path, merge the duplicate | One source note instead of copies, a template, rename what misleads |
   | 2. Claude Code setting  | A `permissions.deny` rule in `settings.json`     | The same: deny writes to a folder that must not change              |
   | 3. Check at write time  | A type, a lint rule, a hook                      | A frontmatter schema, a link or date-format check, a hook           |
   | 4. Check before landing | A test, a CI job                                 | A validator script, a CI job, a checklist the file itself carries   |
   | 5. Written guidance     | `CLAUDE.md`, a skill, a code comment at the trap | `CLAUDE.md`, memory, a style note in the folder                     |

   Rung 5 is for judgment calls nothing mechanical can check. Choosing it for a mistake that a
   pattern match would catch is choosing the rung that already failed.

4. **Build or draft the fix.** Build rungs 3 and 4 when they live in the current repository and
   touch nothing else: they are checks that prove work, and the contract allows them. Draft, do
   not apply, anything that changes how later sessions behave or rewrites the user's content:
   rung 1, rung 2, a hook, and every rung 5 edit (`CLAUDE.md`, memory, a skill, a plugin). Show the
   draft and wait for approval.
5. **Prove it.** Replay the real mistake against the fix and show it fails, then show the correct
   version passes. Keep the failing case as a test or fixture where the repo has a place for one.
   A rung 5 fix cannot be proven this way: say so, and say why no higher rung fit.
6. **Save and report** in the format under Output.

## Rules

- One mistake per fix. A fix aimed at two mistakes usually stops neither.
- Fix the class, not the instance: the check catches every future `10/09/2026`, not only the one
  in `roadmap.md`.
- A new check must not fail on correct existing files. Run it over what is already there before
  calling it done, and fix or exempt real violations only with the user's approval.
- Correcting the file the mistake landed in is part of the fix, but it is not the fix.

## Output

Save one report, adding to today's file when it exists and creating the directory if needed:
`.agents_workspace/product/retros/<YYYYMMDD-HHMMSS>-<session-id>-repeat-mistake.yaml`, with
`other_file: null`. It holds both the fixes that land in the current repository and those outside
it (user settings, the global `CLAUDE.md`, memory, an installed plugin), because a later session
working in the repo reads it, and saving it authorizes no commit of a draft. Mask secrets in every
text value as `<secret>`, because the workspace may be pushed to a remote. Take `<YYYYMMDD-HHMMSS>` from one `date +%Y%m%d-%H%M%S` call and `<session-id>` from `${CLAUDE_SESSION_ID}`. Reply with the same table. Each fix awaiting approval carries its full draft, so
a later session can apply it from the file alone. When a draft is applied or rejected, change that
fix's `status` in the file it was saved in, keeping its draft and evidence.

The report fills `assets/repeat-mistake.template.yaml`, per the `repeat-mistake/v2` section of
`references/repeat-mistake-schema.md`, which also says how a new fix takes its `id`, how a retry
avoids a duplicate, and how a `v1` `.md` is converted before it is amended. After the last edit,
run `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py render <file>.yaml`, which checks it
and writes the `.md` beside it in the layout of `assets/repeat-mistake.template.md`. On exit 1,
fix each error it lists and render again. On exit 2 or 3, without uv, or when the command is denied, say in the reply that the
report went unchecked and its Markdown was not rendered. Never edit the generated `.md`.
