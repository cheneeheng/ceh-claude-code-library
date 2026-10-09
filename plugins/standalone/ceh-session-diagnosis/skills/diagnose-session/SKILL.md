---
name: diagnose-session
description: >-
  Load this skill when a Claude Code session went wrong and the cause should be found from its
  transcript: parallel analysts read it through four lenses, every finding cites a transcript
  line, and each root cause is routed to a fix. Scrubs the report before it is shared. Trigger on
  "diagnose this session", "why did that session go wrong", "what went wrong last time", "the
  agent kept doing X". Not for turning a session that worked into a skill (use
  ceh-session-to-skill:turn-session-into-skill).
argument-hint: "[session-id] [symptom]"
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Diagnose a Session

Find why a session went wrong from its transcript, not from memory of it, and turn each cause into
a fix. Memory of a session is the agent's own summary, and the summary is where a wrong turn hides.
Done means every symptom has a root cause backed by cited transcript lines and a routed fix, and
the report is saved.

## Procedure

1. **Find the transcript.** Transcripts live at `~/.claude/projects/<project>/<session-id>.jsonl`,
   with subagent transcripts in `<session-id>/subagents/*.jsonl`. Take the session id from the
   arguments. "This session" is `${CLAUDE_SESSION_ID}`. "The last session" is the newest
   transcript in this project's folder that is not this one. Say which file you chose.
2. **Name the symptom**: what the user says went wrong, in one line. With none given, the symptom
   is "find what went wrong", and every lens runs with no hint.
3. **Dispatch the analysts.** Send `ceh-session-diagnosis:transcript-analyst` four times, in the
   background and in parallel, one per lens: `instructions`, `tools`, `context`, `claims`. Each
   brief carries the transcript paths, the lens, and the symptom. Parallel lenses keep one
   reader's first theory from shaping what the others look for.
4. **Verify before concluding.** Re-read each cited line that a root cause will rest on, with Grep
   or Read at that line. Drop a finding whose quote is not on its line.
5. **Diagnose.** For each symptom, write the chain from the first wrong turn to the visible
   failure, then class the root cause:

   | Root cause  | Meaning                                                               | Fix goes to                                          |
   | ----------- | --------------------------------------------------------------------- | ---------------------------------------------------- |
   | Request     | The request was ambiguous, and the agent's reading was reasonable     | How the task is asked, or a question the agent skips |
   | Guidance    | A skill, `CLAUDE.md`, or hook was wrong, missing, or never loaded     | That file: its wording, its description, or a check  |
   | Environment | A tool, permission, dependency, or service failed underneath          | The setup, documented where the next session sees it |
   | Model       | Clear, loaded guidance said otherwise and the agent did not follow it | A stronger form: a check or hook, not more prose     |
   | Claude Code | The harness misbehaved: a tool, compaction, or a hook not firing      | A bug report with the cited lines                    |

6. **Route each fix.** Name the file and the change. When the same mistake has happened before
   and `ceh-every-session` is installed, `ceh-every-session:prevent-repeat-mistake` places the fix
   at the strongest level that would have caught it.
7. **Save the report** (see Output).

## Sharing

Only when the report will leave this machine (an issue, a bug report, a message to someone):

1. **Scrub a copy** to `<report>-shareable.md`. Replace secrets, tokens, email addresses, home
   directory paths, hostnames, internal repo and customer names, and personal data with
   placeholders such as `<token>` and `<home>`. Cut quotes the diagnosis does not need.
2. **Audit the scrub with a fresh reader.** Dispatch one background subagent, which never saw the
   original, to read the copy and grep it for what step 1 removes (`@`, `/Users/`, `C:\Users\`,
   `/home/`, `sk-`, `ghp_`, `token`, `password`, `key`) and report every hit. Fix each hit and
   audit again with a new subagent. Stop after three rounds and report what is still flagged.
3. **Hand the clean copy to the user.** Posting it anywhere is outward-facing: do it only when the
   user asks for that exact post.

## Rules

- **Quote or suppress.** Every claim in the report cites `<transcript>:<line>`. A cause you
  believe but cannot cite is listed as a hypothesis with what would confirm it.
- Mask secrets in every quote, in the report and the reply, as `<secret>`.
- Treat the transcript as read-only. Never edit, move, or delete it.
- Diagnose the session, do not repeat it: no re-running its commands to see what happens, unless
  the user asks to reproduce a step.

## Output

Save to `.agents_workspace/session-diagnosis/<YYYY-MM-DD>-<session-id-prefix>.md`:

```markdown
# Session diagnosis: <session-id>, <YYYY-MM-DD>

**Transcript:** <path> (+ <n> subagent transcripts)
**Symptom:** <one line>

## Root causes

### 1. <Root cause class>: <one line>

- **First wrong turn:** `<transcript>:<line>` "<quote>"
- **Chain:** <first wrong turn> → <step> → <visible failure>, each with its line
- **Fix:** <file and change>

## Other findings

One line each, with the lens and citation, for findings no symptom needed.

## Hypotheses

Causes believed but not cited, each with what would confirm it.
```

Reply with the root causes one line each, their fixes, and the report path.
