# Model audit: ceh-build-from-plan

- Date: 2026-10-15
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-build-from-plan.doctor.md](ceh-build-from-plan.doctor.md).

## Kept changes

### plugins/standalone/ceh-build-from-plan/skills/implement-from-plan/SKILL.md:27-28 and :40-41

**Rule:** 3. Two instructions contradict each other. The report's own finding and diff are kept as written.

**Backing:** No guide is needed for a contradiction. The conflict is between `SKILL.md:27-28` ("Set `status: building`" before any code) and `references/plan-format.md:29` ("`building`: at least one phase is done"). Neither Sonnet 5.5 nor any other guide above discusses it. A first phase that stops after two failed fixes would leave a plan marked `building` with zero phases done.

**Before:**
```
2. **Read the whole plan before any code.** Design is binding. An Open item marked as blocking
   stops the run before it starts. Set `status: building`.
...
   5. Set the phase's Status to `done` with its evidence: the commit, or the check command and
      one line of its passing output. Append a Built Phase line to the plan's `## Record`.
```

**After:**
```
2. **Read the whole plan before any code.** Design is binding. An Open item marked as blocking
   stops the run before it starts.
...
   5. Set the phase's Status to `done` with its evidence: the commit, or the check command and
      one line of its passing output. Append a Built Phase line to the plan's `## Record`. When
      this is the plan's first `done` phase, set `status: building`.
```

The fix goes in `SKILL.md` because `plan-format.md` is copied word for word into three plugins. Editing `SKILL.md` avoids a `CROSS_REFERENCES.md` change. Because the status is now set after the first `done` phase, step 1 still finds a plan by `ready` or `building`, and a failed first phase leaves the plan at `ready`.

### plugins/standalone/ceh-build-from-plan/skills/implement-from-plan/SKILL.md:73

**Rule:** 1, with 4 as a second basis. The negative instruction becomes the positive one it implies, and the same statement already appears in Rules.

**Backing:** "**Tell Claude what to do instead of what not to do** * Instead of: 'Do not use markdown in your response' * Try: 'Your response should be composed of smoothly flowing prose paragraphs.'" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices). Rule 4 applies because `SKILL.md:59-60` already says "A check you could not run leaves the phase `todo`, with the reason in its Status." The "Never mark it `done`" clause adds nothing the model does differently.

**Before:**
```
- A Check needs a secret, a service, or a device the session cannot reach → stop at that phase,
  record what it needs, and report. Never mark it `done` on a skipped check.
```

**After:**
```
- A Check needs a secret, a service, or a device the session cannot reach → stop at that phase,
  record what it needs, leave it `todo`, and report.
```

The report left this duplicated "never" alone as working redundancy. It does not disagree with the rewrite, because it never addressed the instruction. The Sonnet 5.5 verification guidance and the Opus 5 "remove generic verification steps" guidance are unaffected. This change does not touch the phase Check itself, which is the plan's own checkpoint.

### Not kept (no change)

- **Opus 5 "remove explicit verification instructions":** The skill's per-phase Check is the plan's own gate, not a generic "verify your work" step. Sonnet 5.5 says to run a real check before reporting done. The guides conflict on this reading, so the instruction stays.
- **Parallel tool calls, subagent, and progress-update rules:** The skill has no independent tool-call or delegation pattern that calls for them.
- **"A third blind fix rarely works" and the repeated "only what the phase names":** These are a stop rule with its reason and working redundancy, so they stay, as the report concluded.
