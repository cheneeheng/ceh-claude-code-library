# Model audit: ceh-usability-audit

- Date: 2026-10-16
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-usability-audit.doctor.md](ceh-usability-audit.doctor.md).

## Kept changes

### plugins/standalone/ceh-usability-audit/skills/simulate-newcomer-first-run/SKILL.md:77

- **Rule:** 1. This is also the `/doctor` report's Group 1a hit (emphasis with no reason attached), and the report's rewrite is followed.
- **Backing:** "The fix is to dial back any aggressive language. Where you might have said "CRITICAL: You MUST use this tool when...", you can use more normal prompting like "Use this tool when..."." https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- **Before:**
  ```
  list **exactly** what a newcomer has, and nothing else. This is the single most important step —
  everything after it is only as honest as this list.
  ```
- **After:**
  ```
  list **exactly** what a newcomer has, and nothing else. Everything after this step is only as honest as this list.
  ```

### plugins/standalone/ceh-usability-audit/skills/simulate-newcomer-first-run/SKILL.md:139

- **Rule:** 1, the same quote and URL as above. The report's rewrite is followed. It drops "not optional" and keeps the reason the rule exists.
- **Before:**
  ```
  **This is the anti-inflation rule and it is not optional.** Severity comes from what actually
  happened to a walker, never from how bad something looks to you. Assign each stall one of the four
  ```
- **After:**
  ```
  Severity comes from what actually happened to a walker, never from how bad something looks to
  you, so the report records observed outcomes instead of the auditor's preferences. Assign each stall one of the four
  ```

### plugins/standalone/ceh-usability-audit/skills/audit-error-messages/SKILL.md:20

- **Rule:** 4. The file never states when the task is done. Step 5 comes closest, but only for rewrites, and nothing in the opening says so. This is added to the opening.
- **Backing:** The rule 4 wording itself ("a missing statement of when the task is done, added to the file's opening"). The model guides are consistent with it, for example Fable 5.1's "Turn ends before the work is done" section (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1), but I kept it under rule 4 only.
- **Before:** (the opening ends with) `...a `ValueError` with no offending value is the same defect as a toast saying "failed".`
- **After:** the same text, plus a new final line: `The work is done when every harvested message has a triage row marked rewritten, or left alone with a stated reason, and the file under Output exists.`

### plugins/standalone/ceh-usability-audit/skills/write-plain-language/SKILL.md:14

- **Rule:** 4, covering two changes to the opening. The first is a missing done-statement. The second is cutting rhetorical preamble, which the report flagged but left unedited. Deleting the preamble changes nothing the model does, because the floor and the never-simplify list carry the behavior.
- **Backing:** The rule 4 wording itself ("a sentence whose deletion changes nothing the model does"). The report's Group 1 note on this paragraph agrees.
- **Before:**
  ```
  The instruction "write simply" is not the useful part — every writer already agrees with it and
  still ships "Configure your workspace to initiate synchronization." What produces clear copy is a
  **floor you can check a word against**, and a list of the things you must not simplify.
  ```
- **After:**
  ```
  Clear copy comes from a **floor you can check a word against**, and a list of the things you must
  not simplify. The work is done when every harvested string has a row in the rewrite table and the
  one-name check has passed.
  ```

## Pinned tuning: `agents/newcomer-simulator.md` for sonnet-5-5

Tuning model: opus-5-5, effort: high. Last tuned for: never.

### Proposed edits

#### Process, step 6 (lines 54–56)

> "At `low` and `medium`, on long agentic tasks, it's more likely to stop and check in with the user before it finishes." … "Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5

The frontmatter pins no `effort`, and a walk is a long agentic task of up to 35 turns. Naming the only valid stopping points keeps the agent from ending the walk early.

Before:

```markdown
6. **Stop the walk** when you reach the goal, hit a stall you cannot get past, or run out of turns.
   These are three different outcomes and the report must name which one — running out of turns is a
   limit of _you_, not a defect of the product, and reporting it as a stall invents a finding.
```

After:

```markdown
6. **Keep walking until one of three things happens:** you reach the goal, hit a stall you cannot
   get past, or run out of turns. A stall you can step past, a budget overrun, or a command you were
   not permitted to run is not a reason to stop. These are three different outcomes and the report
   must name which one — running out of turns is a limit of _you_, not a defect of the product, and
   reporting it as a stall invents a finding.
```

#### Holding the persona, Interrupted (line 70)

> "Claude Sonnet 5 interprets prompts literally and explicitly, particularly at lower effort levels. It does not silently generalize an instruction from one item to another, and it does not infer requests you didn't make. … If you need Claude to apply an instruction broadly, state the scope explicitly."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

The file never defines "major step", but it does define milestones. This edit assumes the two mean the same thing.

Before:

```markdown
- **Interrupted** — after each major step, act as though ten minutes passed and the tab or terminal
  closed. Can you tell where you were and resume? If not, that is a stall.
```

After:

```markdown
- **Interrupted** — after each milestone you reach, act as though ten minutes passed and the tab or
  terminal closed. Can you tell where you were and resume? If not, that is a stall.
```

#### Output to parent session, opening line (line 79)

> "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude better understand your goals and deliver more targeted responses." … "Claude is smart enough to generalize from the explanation."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices

Before:

```markdown
End with exactly this, and nothing after it. No recommendations section.
```

After:

```markdown
End with exactly this, and nothing after it. Leave recommendations out: the auditor who dispatched
you turns stalls into fixes, and a fix you propose brings in the outside knowledge this walk exists
to exclude.
```

#### Hard rules, source-code and documentation bullets (lines 137–140)

> "Tell Claude what to do instead of what not to do"
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
>
> "If you need Claude to apply an instruction broadly, state the scope explicitly"
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

The current wording says "this repo", which a literal reader can take to mean the plugin repo rather than the target. The rewrite states one positive rule, keyed to the allowlist the agent is given.

Before:

```markdown
- **Do not read source code** unless it is on the allowlist. Reading the source to work out what a
  flag does is the single most common way this walk gets silently invalidated.
- **Do not read this repo's other documentation**, issues, commit messages, or anything the
  conversation that spawned you knew. You were not there.
```

After:

```markdown
- **Read only what the allowlist names.** Source code, the target's other documentation, its issues
  and commit messages, and anything the conversation that spawned you knew stay unread unless
  listed: you were not there. Reading the source to work out what a flag does is the single most
  common way this walk gets silently invalidated.
```

#### Hard rules, "You cannot ask questions" bullet (lines 142–143)

> "Be specific about the desired output format and constraints."
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
>
> "Claude Sonnet 5 interprets prompts literally and explicitly"
> https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5

This bullet asks for a free-form final message that says "what the parent should decide". Line 79 asks for "exactly this, and nothing after it. No recommendations section." A literal model has to break one of the two. The rewrite routes the blocker into the walk report and leaves the output contract as it is.

Before:

```markdown
- You cannot ask questions. When blocked, stop and make the blocker your final message: what you
  finished, what stopped you, what the parent should decide.
```

After:

```markdown
- You cannot ask questions. When blocked, stop and return the walk report with **Stopped because:**
  stall I could not pass. The Milestones table shows what you finished, the last stall entry shows
  what stopped you, and Notes names the fact the parent must supply.
```
