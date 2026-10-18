# Repeat mistakes, 2026-10-18 (session a2035f28-1913-41f9-8f99-d59a0cc27bfe)

| Mistake                                                                     | Evidence                                                                                                                                                                                                                                                                                                                                                                                                                                       | Rung | Fix                                                                                                                                                                                                                                                | Proof                                                                                                                                                                                   | Status                                |
| --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| Created a branch without loading `ceh-git-workflow:branch`                  | Bash `git checkout -b fix/usage-insights-projection-range-note`, no Skill call for `branch` before it; 57 of 61 branch creations across this project's transcripts did the same                                                                                                                                                                                                                                                                | 3    | PreToolUse Bash hook `branch-skill-gate.py` in `ceh-git-workflow`: denies a branch-creating git command until the transcript holds a Skill call for `ceh-git-workflow:branch`                                                                      | fails on the real mistake: yes (`replay.py`, 11 branch checks pass)                                                                                                                     | awaiting approval (user applies it)   |
| Fixed a diagnosed fix note without loading `ceh-testing:test-a-bug-fix`     | User prompt "Fix this @apps/usage-insights/product/fixes/range-switch-leaves-first-section-unchanged.md" (`status: diagnosed`), first edit `Edit defaultLayout.test.tsx` with no Skill call for `test-a-bug-fix`                                                                                                                                                                                                                               | 3    | PreToolUse Edit/Write hook `bug-fix-skill-gate.py` in `ceh-testing`: once a `product/fixes/*.md` with `status: diagnosed` is in the transcript, denies the first edit outside `product/` and `.agents_workspace/` until `test-a-bug-fix` is loaded | fails on the real mistake: yes (`replay.py`, 4 fix checks pass)                                                                                                                         | awaiting approval (user applies it)   |
| Wrote non-trivial code without loading `ceh-coding-conduct:write-less-code` | Write `branch-skill-gate.py`, `bug-fix-skill-gate.py`, `replay.py` after the per-prompt reminder said "Before implementing a feature or non-trivial logic, invoke the Skill tool with skill=\"ceh-coding-conduct:write-less-code\""; across 19 sessions in this project where both hooks fired and something was edited, the SessionStart "MANDATORY FIRST ACTION" contract load was followed in 18, the conditional write-less-code load in 2 | 1    | Remove the judgment call: `load-contract.sh` makes write-less-code part of the mandatory first load, and the per-prompt reminder drops its conditional load line                                                                                   | not provable by replay: the fix changes what the model is told, not a check; the 18-of-19 vs 2-of-19 counts are the evidence that a mandatory load holds and a conditional one does not | applied (`ceh-coding-conduct` 2.2.11) |

**Why rung 3:** rung 1 does not fit, because there is no duplicate path to remove: the skill and the
commands both have to exist. Rung 2 does not fit, because a `permissions.deny` rule cannot tell
whether a skill was loaded. Both mistakes have a mechanical moment to catch (a branch-creating
command, or the first edit after a diagnosed fix note), so rung 5 guidance would be the level
that already failed: the skill descriptions named both triggers and were skipped.

**Why rung 1 for write-less-code:** it has no single mechanical moment (it applies to every edit,
and SOUL.md keeps a load hook for it because "write-less-code is not really a moment"), so a rung 3
gate would either fire on every edit or guess at "non-trivial". The cause is the conditional
"before non-trivial logic" wording, which asks the model to judge when to load it. The mandatory
form in the same plugin already works.

## Review

Moved here from claude-code-command-center's `.agents_workspace/repeat-mistakes/2026-10-18.md`,
with its drafts. The write-less-code fix is applied. The two gates are held back, for these reasons:

- **Branch gate:** SOUL.md prefers rewriting a skill's description over a hook that enforces its
  load, keeping load hooks only for skills with no clear moment, and a branch has a clear moment.
  The gate also adds little: the session's branch name already followed the skill's naming, and
  `branch-guard.py` already puts the prefix list in front of the agent when it edits on `main`.
- **Bug-fix gate:** the same SOUL.md rule applies, since a diagnosed fix note is a clear moment. The
  gate also scans the whole transcript on every edit outside `product/` in every session. In this
  session, the first edit was the regression test, so test-first held without the skill. The
  conservative fix is a `test-a-bug-fix` description that names "fix this product/fixes/<slug>.md"
  as a trigger.

## Drafts

Full scripts sit next to this file in `2026-10-18-claude-code-command-center-repeat-mistake/`: `branch-skill-gate.py`,
`bug-fix-skill-gate.py`, and `replay.py` (the replay of both mistakes against this session's
transcript, `python -I replay.py`, exit 0 = all pass; edit its paths to point at the drafts).

Apply in `ceh-claude-code-library` (each plugin owns its own gate, so each works on its own):

1. Copy `branch-skill-gate.py` to `plugins/standalone/ceh-git-workflow/scripts/` and add a
   second PreToolUse entry to `plugins/standalone/ceh-git-workflow/hooks/hooks.json`:

   ```json
   {
     "matcher": "Bash",
     "hooks": [
       {
         "type": "command",
         "command": "python3 -I -S \"${CLAUDE_PLUGIN_ROOT}/scripts/branch-skill-gate.py\"",
         "timeout": 10
       }
     ]
   }
   ```

2. Copy `bug-fix-skill-gate.py` to `plugins/standalone/ceh-testing/scripts/` and create
   `plugins/standalone/ceh-testing/hooks/hooks.json`:

   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Edit|Write|MultiEdit|NotebookEdit",
           "hooks": [
             {
               "type": "command",
               "command": "python3 -I -S \"${CLAUDE_PLUGIN_ROOT}/scripts/bug-fix-skill-gate.py\"",
               "timeout": 10
             }
           ]
         }
       ]
     }
   }
   ```

3. Bump both plugins' versions and follow that repo's release steps.

4. Write-less-code, in `plugins/standalone/ceh-coding-conduct/scripts/`:

   - `load-contract.sh`, the first line of the heredoc becomes:

     ```
     MANDATORY FIRST ACTION: Invoke the Skill tool with skill="ceh-coding-conduct:agent-coding-contract",
     then with skill="ceh-coding-conduct:write-less-code",
     ```

     and the SubagentStart fallback sentence names both files:
     `If you have no Skill tool, Read ${CLAUDE_PLUGIN_ROOT}/skills/agent-coding-contract/SKILL.md and ${CLAUDE_PLUGIN_ROOT}/skills/write-less-code/SKILL.md instead.`

   - `inject-less-code-reminder.sh`: delete the last heredoc line ("Before implementing a feature
     or non-trivial logic, invoke ..."), and change the header comment "The full write-less-code
     skill loads on demand when non-trivial code is actually being written" to "The full skill
     loads at session start with the contract (load-contract.sh)".
   - Cost: the skill is 3.9 KB, about 1k tokens once per session start, resume, clear, and compact.

Known limits: the branch gate misses `git -C "<path with spaces>" checkout -b`. The fix gate scans the
transcript on every edit outside `product/` in every session, up to the first `test-a-bug-fix`
call or to the end: 54 ms per edit on this session's 1.9 MB transcript, against 44 ms for
Python startup alone (measured, 5 runs each).
