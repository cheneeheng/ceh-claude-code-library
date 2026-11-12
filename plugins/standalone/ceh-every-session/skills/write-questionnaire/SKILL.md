---
name: write-questionnaire
description: >-
  Load this skill when open questions must go to someone not in the session: write a
  self-contained questionnaire file, then read the answers back. Trigger on "write these up as
  questions for X", "I need to ask the team", "read the answers back". Not for the user in this
  session.
argument-hint: "[write [--issue <owner/repo> --labels <list>] | read [path | --issue <owner/repo>#<n>]]"
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Write questionnaire

Turn open questions into one file that someone who never saw this session can answer cold, and
read their answers back into the work. Done means the file is written and its path reported, or,
in read mode, every answer is applied or listed as still open.

## Procedure

### Write

1. **Collect the open questions** from the session: decisions you deferred, facts you could not
   find, choices only the reader owns. Drop any you can answer yourself from the files or a
   sensible default the reader would not care about.
2. **Order them by what they block**, most first. A question nothing waits on goes last or goes.
3. **Write each question self-contained** in the format under Output. The reader has none of this
   session's context, so each question carries the facts needed to answer it, in plain words, with
   no session jargon or file paths the reader cannot open.
4. **Give options where the answer is a choice**, each with its consequence, and mark the one you
   recommend. A free-text question still states what form of answer you can use.
5. **Save** to `.agents_workspace/questionnaires/<YYYYMMDD-HHMMSS>-<session-id>-<topic>.md` in the working directory,
   creating the directory if needed, and report the path and the question count. Take `<YYYYMMDD-HHMMSS>` from one `date +%Y%m%d-%H%M%S` call and `<session-id>` from `${CLAUDE_SESSION_ID}`.

   **With `--issue <owner/repo> --labels <list>`**, post the questionnaire as an issue instead and
   save no file. The body is the same filled template, frontmatter included, with this intro line
   in place of the template's: "From: <asker>, YYYY-MM-DD. Answer on the `Answer:` line under each
   question, here or in a comment as `Answer <n>: <text>`. Leave a line blank to skip it." Post it
   with
   `gh issue create --repo <owner/repo> --title "Questions on <topic>" --label <list> --body-file -`,
   the body on stdin, and report the issue number from the URL `gh` prints, and the question count.
   - `--issue` only selects the form. Post only when a human authorized opening issues in that
     repo ahead of time, in a launch prompt or an instruction in this session. Without that, post
     nothing and say why.
   - When `gh` is missing or fails (no auth, a missing label), report its error, and post and save
     nothing, because the caller waits on an issue number, not a local file.
   - Never retry `gh issue create`. On an error after the call, report that the issue may exist and
     that the caller should look for it by label, because a second issue asks twice.

### Read

1. **Find the file**: the path given, otherwise the newest file in
   `.agents_workspace/questionnaires/`, by the date in its name, then by modified time. With `--issue <owner/repo>#<n>`, run
   `gh issue view <n> --repo <owner/repo> --json body,comments` instead.
2. **Read every `Answer:` line.** Apply each answer to the work it unblocks, in question order. For
   an issue, a question's answer is the newest of its `**Answer:**` line in the body and every
   comment line `Answer <n>: <text>` for its number, by comment time, the body counting as oldest.
3. **List what is still open**: blank answers, and answers that raise a new question. A blank
   answer does not mean the recommended default: say which default you would take and wait.

## Rules

- One question per entry. "Should we use X, and if so how should Y work?" is two questions.
- Ask for the decision, not for permission to think. "Which of A or B?" beats "Any thoughts on
  the design?", which returns an essay instead of an answer.
- Ten questions at most. Past that, the reader skims, so cut to the ten that block the most work.
- Writing the file sends nothing. Delivering it to the reader (email, chat, a ticket) is the
  user's step unless they asked you to do it. The issue form is that delivery, so it posts only
  under the authorization in Write step 5.

## Output

The file fills `assets/questionnaire.template.md`, per `references/questionnaire-schema.md`, one
numbered `##` section per question.
