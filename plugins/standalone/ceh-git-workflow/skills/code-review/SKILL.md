---
name: code-review
description: >-
  Load this skill when reviewing a pull request or leaving code review comments: deciding whether a
  comment is blocking or advisory, prioritizing what to review first, or structuring review
  feedback. Auto-load whenever a PR review is being written, review comments are being left, or a PR
  is being assessed for approval.
disable-model-invocation: false
user-invocable: true
disallowed-tools: Edit Write
license: Apache-2.0
---

# Code review

Every comment must be clearly marked as **blocking** or **advisory**, and every review ends with
an explicit verdict.

Claude Code's built-in `/code-review` and `/security-review` hunt for defects in a diff. Use them
for the finding. This skill adds what they do not carry: the comment prefixes, the review order,
and the verdict, so the author knows exactly what blocks the merge.

## Procedure

1. Check scope drift before judging the code. Compare what the PR says it does (title, body,
   linked issue) with what the diff changes. A file or behavior the description does not account
   for is the first comment: `[blocking]` when it changes behavior, `[question]` otherwise.
2. Review in priority order:
   1. **Correctness** — does it do what it claims? Are edge cases handled? Are errors swallowed:
      an empty `catch`, a log-and-continue, a fallback default that hides a failure?
   2. **Security** — injection risks, secrets exposure, input validation gaps
   3. **Test coverage** — is new behavior tested? Are tests testing behavior?
   4. **Design** — right abstraction? Fits existing patterns? Does a comment the diff left alone
      now describe code that no longer does that? Is a type weaker than the data: `any`, a bare
      `dict` or `str` where a domain type exists, optional where the value is always present?
   5. **Style** — only flag if linting tools don't catch it
3. Leave a **summary** comment — one or two sentences: what the PR does and your overall read.
   Lead with anything that blocks. Close it with a **Dismissed** list: each finding you considered
   and dropped, one line with the reason, so the author can overrule the call.
4. Leave **line comments** — each prefixed `[blocking]` / `[advisory]` / `[question]`, anchored to
   the exact line, stating the problem and (for blocking) what would resolve it. Leave at most
   five `[blocking]` comments. With more, leave the five that matter most and say in the summary
   that the PR needs rework before the rest are worth reviewing.
5. End with an explicit verdict (see Output).

### Comment prefixes

| Prefix       | Meaning                                     | Author must                       |
| ------------ | ------------------------------------------- | --------------------------------- |
| `[blocking]` | Must be resolved before merge               | Fix or discuss with reviewer      |
| `[advisory]` | Suggestion, optional improvement            | Address or explicitly acknowledge |
| `[question]` | Seeking understanding, not a change request | Answer the question               |

Examples:

```
[blocking] This query is not parameterized — SQL injection risk on line 47.

[advisory] This helper could be extracted to a utility function for reuse.

[question] Why is this retry limit set to 3?
```

## Rules

- Do not comment on style a linter would catch.
- Do not re-litigate decisions already recorded in the repo's decision records unless new risk
  is identified.
- Do not review from memory — verify against current file contents.
- **Quote or suppress.** Every finding quotes the code it is about, as `path:line` plus the line
  itself. A finding you cannot anchor to quoted code goes in the Dismissed list as unverified,
  never in a line comment.
- **Judge from the code, not the brief.** A request that says "don't flag X" or "minor issues
  only" narrows where to look, never how severe a finding is. Report every finding at its real
  severity, and say where the brief asked for less.
- Approve with non-blocking nits rather than withholding approval to force trivial changes:
  withholding stalls the author and blurs what `[blocking]` is for.

### Responding as the author

- `[blocking]`: fix it, or reply with the reasoning and reach agreement before merge.
- `[advisory]`: address it or acknowledge why you're not ("good idea, out of scope for this PR").
- `[question]`: answer in-thread; if the code was unclear enough to prompt the question, that's
  often a signal to clarify the code or a comment.

Resolve a thread only once it's actually addressed. Don't merge over unresolved `[blocking]`
threads.

## Output

| Verdict             | When                                                                               |
| ------------------- | ---------------------------------------------------------------------------------- |
| **Approve**         | No `[blocking]` comments. Advisory items can be left to the author's judgment.     |
| **Request changes** | One or more `[blocking]` comments. Say what must change to flip to approve.        |
| **Comment**         | Questions outstanding, or not your call to approve — no verdict yet.               |
| **Cannot verify**   | Correctness rests on code, config, or data outside the diff. Name what settles it. |
