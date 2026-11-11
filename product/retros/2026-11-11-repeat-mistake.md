---
schema: repeat-mistake/v1
date: 2026-11-11
other_file: none
---

# Repeat mistakes — 2026-11-11

From the diagnosis of headless run `4aeb72cf` (launched by session `70b706f1`), root cause 1: a
live test of `ceh-usability-audit:audit-error-messages` on a scratch Flask app, prompt "the error
messages in this app are useless, improve them". Transcript citations are `H:<line>` in
`<home>/.claude/projects/<scratchpad-live-orders-app-em>/4aeb72cf-52e1-49cb-b8a2-e215f01febcb.jsonl`.

| Mistake                                                                   | Evidence                                                                                                                       | Rung | Fix                                                                                                         | Proof        | Status  |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ---- | ----------------------------------------------------------------------------------------------------------- | ------------ | ------- |
| A usability skill branched, committed and pushed its edits unasked        | `H:76` "git checkout -b fix/error-messages", `H:119` "git push -q -u origin fix/error-messages"                                | 5    | "Leave the edits uncommitted" rule in the three editing usability skills, registered in CROSS_REFERENCES.md | not provable | applied |
| A usability skill fixed a defect outside its kind (SQL injection) unasked | `H:84` whole-file Write parameterizing the login query, `H:125` "SQL injection (fixed): ... I had to rewrite that line anyway" | 5    | "Report other defects, do not fix them" rule in the same three skills, registered in CROSS_REFERENCES.md    | not provable | applied |

## Why this rung

- Unrequested git landing: rung 1 does not fit, because the cause is missing guidance, not a
  duplicate path. Rung 2, a `permissions.deny` on `git push`, would block every push in every
  session, and a plugin cannot ship one. Rung 3, a PreToolUse hook on `git commit|push`, cannot
  tell whether this skill is running or the user asked to land. No written rule has failed yet,
  and the user's rule is to wait for a measured miss of the written rule before adding a hook.
  Rung 4 cannot see agent behavior.
- Unrelated defect fixed: no pattern separates "a message rewrite" from "a security fix on the
  same line", so only a judgment rule fits.

Both are written guidance, so a replay cannot prove them. The check that would show they work is
the same headless prompt rerun after they are applied (a paid run, only when asked): the run
leaves its edits uncommitted and lists the SQL injection as a finding.

## Pending drafts

Each draft is one paragraph, byte-identical in all three skills, placed where each skill changes
the target, the second right after the first when both are approved:

- `audit-error-messages`: at the end of `### 5. Apply the rewrites`.
- `audit-interface`: after the paragraph at line 159 ("Then fix the **top Blocker only**").
- `write-plain-language`: under `## Output`, after the rewrite table.

Each approved paragraph gets a `docs/CROSS_REFERENCES.md` entry, `audit-error-messages` canonical,
the other two as copies. `ceh-usability-audit` takes one PATCH bump for either or both.

### A usability skill branched, committed and pushed its edits unasked

```markdown
**Leave your edits in the working tree.** Make no branch, commit, push, or pull request unless the
request asks for one, because the user reviews the diff before anything lands.
```

### A usability skill fixed a defect outside its kind (SQL injection) unasked

```markdown
**Report other defects, do not fix them.** A security hole or a logic bug found on the way is
reported as a finding, even on a line you are already rewriting, because the user expects the
diff to hold only this skill's edits.
```
