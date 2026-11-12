---
name: hand-off-session
description: >-
  Load this skill when a session's working state must survive into a later one: save writes a
  handoff file, load reads one back and resumes. Trigger on "save where we are", "write a handoff",
  "I'll continue this tomorrow", "load the handoff", "pick this up".
argument-hint: "[save [--file <path>] | load [path]]"
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Checking and rendering the handoff's YAML needs uv; without it the handoff is saved unchecked
  and unrendered.
license: Apache-2.0
---

# Hand off session

Save turns this session's working state into one file a later session can resume from cold. Load
reads that file back and continues from it. The file replaces the transcript: everything needed is
in context _now_, and reconstructing it later from a transcript costs far more than writing it.

Pick the mode from `$ARGUMENTS` or the request: `save` when the state must outlive the session,
`load` when a new session starts from one. With no clear mode, saving is the default, because a
spare handoff file costs nothing and a missing one loses the state.

## Save

1. **Leave nothing half-applied.** Finish the edit or command in flight, or revert it and record it
   as open. Do not start new work to make the snapshot look tidier.
2. **Describe the working tree, do not change it.** Commit uncommitted changes only if committing
   was already authorized. Saving a handoff authorizes no commit, stash, or push.
3. **Write the handoff file** to
   `.agents_workspace/handoff/<YYYYMMDD-HHMMSS>-<session-id>-handoff.yaml` in the working
   directory, filling `assets/handoff.template.yaml` in the `handoff/v2` format in
   `references/handoff-schema.md`, quoting values as its Quoting rule says. Create the directory if
   needed. Take `<YYYYMMDD-HHMMSS>` from one `date +%Y%m%d-%H%M%S` call and `<session-id>` from `${CLAUDE_SESSION_ID}`. The `session` field keeps the first 8
   characters of the session id. A caller that passes its own header lines (a usage window,
   a reason) gets them in `header`. With `--file <path>`, the YAML is that path with its suffix
   replaced by `.yaml`, overwritten, so a calling program keeps its state under a fixed name and
   still reads the rendered Markdown at the path it named. Before writing it, delete the old
   Markdown at that path, so a save that cannot render leaves no stale file to resume from.
   - **Caller fields:** a caller may name extra fields and their values in its request, for example
     "save --file jobs/J/state.md with fields Plan: product/plans/x.yaml, PR: none yet". Write each
     as a `fields` item, in the order named. They render as `**<Field>:** <value>` lines after
     `**Session:**`.
   - **A place for decisions:** when the caller names one (a file or a skill), set `forks_go_to`
     to it, and list each pending fork in `decisions_pending` as usual.

   Then run `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py render <file>.yaml`, which
   writes the `.md` beside it, and fix the YAML for each error it lists. Never edit the generated
   `.md`. On exit 2 or 3, or without uv, say in the reply that the handoff went unchecked and
   unrendered.

4. **Append one line to the global index** at `~/.claude/handoff/index.md`, creating it if absent:
   `- <YYYY-MM-DD HH:MM> — <cwd> — <branch or "no git"> — <one-line state> — <file path>`, the
   path of the `.yaml`.
   The index is what finds the file days later without remembering which directory it was in.
   With `--file`, skip this step: the caller knows where its file is, and a line per save would
   grow without bound.
5. **Report the file path and its content** as your message, so the handoff is readable without
   opening the file.

Saving does not end the session. Keep working afterwards if the user asks, and save again later:
each save is a new file, never an edit of an old one, except with `--file`, which overwrites its
one file.

## Load

1. **Find the file.** Use the path given. Otherwise take the newest `*-handoff.*` or older `HANDOFF-*` in
   `.agents_workspace/handoff/` by the timestamp in its name, `.yaml` and `.md` alike, and if there
   is none, the newest index line in `~/.claude/handoff/index.md` whose cwd matches. If several
   plausible files exist and none was named, list the newest few with their one-line state and
   take the newest, saying so. Whichever path you took, when a `.yaml` of the same stem exists
   beside it, that YAML is the handoff: run
   `uv run --script ${CLAUDE_SKILL_DIR}/scripts/artifact.py check <file>.yaml` and stop on exit 1
   with its errors, then read it by key, `open.0` as the next step. A `.md` with no `.yaml` beside
   it is a `handoff/v1` file, read as before. On exit 2 or 3, or without uv, say that the handoff
   went unchecked and read the YAML anyway.
2. **Read it in full**, then check it against the world before trusting it: the branch exists and
   is checked out, files named under Done exist, `git log` and `git status` match the described
   state. Report every mismatch. The file is a snapshot and the repo may have moved on.
3. **State what you are resuming:** the goal, each caller field after `**Session:**`, and the
   first Open item as the next step.
4. **Continue from the first Open item.** A Decisions pending entry that blocks that step goes to
   the user before any work on it. When the line ends `, forks go to <place>`, send each such fork
   there instead: write it to the file named, or invoke the skill named with it.

## Rules

- Write for a reader with none of this context: exact file paths, branch names, commands. A line
  that only makes sense with the transcript open is a line to rewrite.
- Keep the file a bounded snapshot, short enough to read in full on load, never a log.
- Mark what was validated and what was not. Load treats an unmarked Done item as unverified.
- Resume by loading the file in a fresh session, not by replaying the old one with `--resume`.
  The replay pays again for the context the file exists to compress.

## Output

The handoff file fills `assets/handoff.template.yaml`, per the `handoff/v2` section of
`references/handoff-schema.md`, and renders to the layout of `assets/handoff.template.md`.
