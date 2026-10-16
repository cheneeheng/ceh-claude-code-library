# Model audit: ceh-session-diagnosis

- Date: 2026-10-16
- claude-code 2.1.301
- Edits applied: no
- WARNING: 1 tool call(s) were denied, so the report may be incomplete.

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-session-diagnosis.doctor.md](ceh-session-diagnosis.doctor.md).

## Kept changes

### plugins/standalone/ceh-session-diagnosis/skills/diagnose-session/SKILL.md:81-83

**Rule:** 1 and 4. The negative instruction says the same thing as the positive one, and the "Never edit, move, or delete it" sentence only repeats "read-only".

**Backing quote:** "Tell Claude what to do instead of what not to do. Instead of: 'Do not use markdown in your response'. Try: 'Your response should be composed of smoothly flowing prose paragraphs.'" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

The task needs this because the skill's job is reading a transcript. The "no re-running its commands" clause is a prohibition where the positive form ("work from the transcript alone") says the same and tells the agent what to do.

**Before:**
```
- Treat the transcript as read-only. Never edit, move, or delete it.
- Diagnose the session, do not repeat it: no re-running its commands to see what happens, unless
  the user asks to reproduce a step.
```

**After:**
```
- Treat the transcript as read-only.
- Diagnose from the transcript alone. Re-run a session command only when the user asks to
  reproduce that step.
```

---

**Not kept:**
- **`/doctor` report:** Its two low-confidence flags (the output caps in `transcript-analyst.md`, and the commit-on-save behavior at `SKILL.md:45` and `:87-89`) are not changes. The agent file is pinned. The commit behavior is the report's open "your call" decision between keeping it and rewording it.
- **Fresh-context audit subagent at `SKILL.md:69`:** The Fable 5 page says fresh-context verifier subagents outperform self-critique. The Opus 5 page says verification instructions and using subagents to double-check work cause over-verification. The guides conflict, so I left it alone.
- **Parallel dispatch in step 3:** Step 3 already says "in the background and in parallel", so adding a batching nudge would change nothing.
- **Definition of done:** Lines 17-18 already state it.
- **Other changes:** No CAPS, "you MUST", or filler prose remains in the skill.

## Pinned tuning: `agents/transcript-analyst.md` for sonnet-5-5

Tuning model: opus-5-5, effort: high. Last tuned for: never.

### Proposed edits

#### Line 23: step 3, "Apply your lens"

Quote (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5): "Claude Sonnet 5 interprets prompts literally and explicitly, particularly at lower effort levels. It does not silently generalize an instruction from one item to another [...] If you need Claude to apply an instruction broadly, state the scope explicitly"

Before:

```
3. **Apply your lens**:
```

After:

```
3. **Apply your lens** to every transcript in the brief, each subagent transcript included, not
   only the main one:
```

#### Line 38: finding cap and ranking

Quote (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5): "If you do want the model to self-filter in a single pass, be concrete about where the bar is rather than using qualitative terms like 'important' [...] If your harness has a separate verification, deduplication, or ranking stage, tell the model explicitly that its job at the finding stage is coverage rather than filtering."

Before:

```
At most 12 findings, most consequential first, then one line on what you could not read.
```

After:

```
At most 12 findings, then one line on what you could not read. Rank first the findings that bear
most directly on the symptom in the brief (with no symptom, on how the session ended): a user
correction, a claim of done that the output contradicts, or a wrong turn the session never
recovered from comes before a one-off retry or a slow call. Below the cap, report every finding
you can cite, even one you are unsure matters, because the parent session re-reads each cited
line before it concludes anything.
```

#### Lines 40–46: output template

Quote (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices): "Be specific about the desired output format and constraints." Together with the Sonnet 5 literal-following quote above: the "Other lens:" line appears only in the Hard rules, not in the template, so a literal reader can leave it out or put it anywhere.

Before:

```
   First wrong turn: <file>:<line> — <one sentence>
Not read: <files or line ranges skipped, and why>, or "nothing"
```
```

After:

```
   First wrong turn: <file>:<line> — <one sentence>
Not read: <files or line ranges skipped, and why>, or "nothing"
Other lens: <lens> — <file>:<line> — <one sentence>, one entry per finding, or "none"
```
```

#### Line 52: secret masking

Quote (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5): "It does not silently generalize an instruction from one item to another [...] state the scope explicitly (for example, 'Apply this formatting to every section, not just the first one')."

Before:

```
- Mask any secret, token, password, or key in a quote as `<secret>`. Transcripts hold whatever
  passed through the session.
```

After:

```
- Mask any secret, token, password, or key as `<secret>` everywhere in your final message: quotes,
  the one-sentence summaries, and the Other lens line. Transcripts hold whatever passed through
  the session.
```

#### Line 54: read-only Bash rule

Quote (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices): "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude better understand your goals [...] Claude is smart enough to generalize from the explanation."

Before:

```
- Use Bash only to read: `python3`, `jq`, `wc`, `head`. Never write, move, or delete a file.
```

After:

```
- Use Bash only to read: `python3`, `jq`, `wc`, `head`. Never write, move, or delete a file: the
  other lens analysts read the same transcripts in parallel, and the parent re-reads your cited
  lines afterwards, so a changed file breaks both.
```

#### Lines 57–58: carrying the work through

Quote (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5): "On agentic coding tasks at `low` and `medium` effort, the model sometimes checks in before the work is done. It might pause to confirm a plan, ask a question it could answer itself, or stop after one part of a multipart task to ask whether to continue. [...] 'Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step.'"

Before:

```
- You cannot ask questions. When blocked, stop and make the blocker your final message: what you
  finished, what stopped you, what the parent should decide.
```

After:

```
- You cannot ask questions. Keep working until every transcript in the brief has been read
  through your lens, and stop early only when you cannot go on. Then make the blocker your final
  message: what you finished, what stopped you, what the parent should decide.
```
