# Model audit: ceh-orchestration-lab

- Date: 2026-10-15
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-orchestration-lab.doctor.md](ceh-orchestration-lab.doctor.md).

## Kept changes

None.

I fetched all seven pages and read every file in the plugin. I read the pinned `agents/implementer.md` only for context. Findings A and C from the `/doctor` report are not kept. Finding B is on the pinned file, so I ignored it.

- **Finding A, `skills/orchestrate/SKILL.md:36`, dropping "at most 30 line-anchored lines".** No fetched page says a numeric output cap is a defect or that removing one helps a model. The Opus 5 guide says its replies run long and tells you to "prompt explicitly" for brevity, so loosening the cap risks hurting it. It fits none of rules 1 to 4.
- **Finding C, the implementer's Process list.** It sits in the pinned `agents/implementer.md`, so I ignored it.
- **Negative instructions** ("Never write the finished text or code into a brief", "Do not run it yourself", "Never edit a project file yourself"). Each one gives its reason in the same sentence. The general page's "Tell Claude what to do instead of what not to do" is about formatting steers, and a positive rewrite would add nothing.
- **`run_in_background: false` for parallel pieces, `orchestrate` step 4.** The Fable 5 and 5.1 guides favour asynchronous subagents. The step already sends a clearly longer piece in the background, and pieces of similar size finish together, so there is no idle time to recover. No other guide asks for the change, and the foreground choice is a deliberate step-count saving.
- **Explicit check steps** (`orchestrate` step 6, `plan-then-implement` step 4). The Opus 5 guide says to remove explicit verification instructions. The Sonnet 5.5 guide says verification matters and warns about skipped checks, so removal would hurt Sonnet 5.5.
- **The duplicate "never take over" sentence** (`orchestrate` lines 72-73 against 67-68). I left it alone, because deleting it would also change how the worker pieces are handled, not only the wording.
- **Missing files or commands.** None. Both scripts exist and take `session_id` plus a second argument. `references/run-log.md` exists. The README commands match.
- **Contradictions.** None found. The stop conditions, rules and defaults agree across the two skills and the run log.
- **"Done" statements.** Both skills already state when the run is done in their opening paragraph.

## Pinned tuning: `agents/implementer.md` for sonnet-5-5

Tuning model: opus-5-5, effort: high. Last tuned for: never.

### Proposed edits

#### Line 22, step 4: "If it fails because of your change, fix it and run it again."

> "If the task is unreasonable or infeasible, or if any of the tests are incorrect, please inform me rather than working around them." and "Do not hard-code values or create solutions that only work for specific test inputs." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

> "It does not silently generalize an instruction from one item to another, and it does not infer requests you didn't make. [...] If you need Claude to apply an instruction broadly, state the scope explicitly" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)

Before:

```
4. **Run the check** the brief names. If it fails because of your change, fix it and run it again.
```

After:

```
4. **Run the check** the brief names. If it fails because of your change, fix the code and run it
   again. Fix the code, not the check: never hard-code values to match it, and if the check itself
   looks wrong, leave it as is and say so under Deviations. If it fails for a reason outside your
   change, leave that failure alone and report it on the Check line.
```

#### Line 23, step 4: "If the brief names no check, run the tests that cover the files you changed."

> "When you change code that can be run, built, or type-checked, run a real check that exercises the change before reporting it done [...] A syntax-only check, or a check command that failed to start, does not count; if all that is missing is the project's declared dependencies, install them with its own package manager and lockfile (e.g. npm install, pip install -r requirements.txt), never via sudo or the system package manager, unless told not to." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5)

Before:

```
   If the brief names no check, run the tests that cover the files you changed.
```

After:

```
   If the brief names no check, run the tests that cover the files you changed. The check must
   exercise the change: a syntax-only check, or a command that failed to start, does not count.
   If all that is missing is the project's declared dependencies, install them with its own
   package manager and lockfile, never via sudo or the system package manager.
```

#### Lines 41-42, Hard rules: scope

> "The model tends to add tests, documentation, and small supporting files that fit your repository's conventions, even when you don't ask for them. It does this at every effort level, and more at higher effort." and "When the work the user asked for is done and checked, stop and report. Don't add features, tests, files, docs or refactors that weren't asked for. If you think one would help, mention it at the end instead of doing it." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5)

> "When the work the user asked for is done and its checks pass, stop and report. Don't start extra rounds of review or hardening on your own" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5)

Before:

```
- Stay inside the files and behavior the brief names. Work the brief did not ask for goes under
  Deviations as a suggestion, not into the code.
```

After:

```
- Stay inside the files and behavior the brief names. When the change is done and its check
  passes, stop and report: add no features, tests, files, docs, or refactors the brief did not ask
  for, and start no extra rounds of review or hardening. If you think one would help, put it under
  Deviations as a suggestion.
```

#### Line 43, Hard rules: git state

> "If you need Claude to apply an instruction broadly, state the scope explicitly" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5)

> "Hard to reverse operations: git push --force, git reset --hard, amending published commits" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

Before:

```
- Never commit, push, stash, reset, or check out: the parent and the user own the git state.
```

After:

```
- Never commit, push, stash, reset, check out, or run any other git command that changes the
  repository or working tree (restore, clean, rebase, merge, branch): the parent and the user own
  the git state. Read-only commands such as git status and git diff are fine.
```

#### Lines 46-47, Hard rules: blockers

> "On agentic coding tasks at `low` and `medium` effort, the model sometimes checks in before the work is done. It might pause to confirm a plan, ask a question it could answer itself, or stop after one part of a multipart task to ask whether to continue. [...] Keep working until everything the user asked for is done, and only stop to ask when you can't go on without the user or before a risky step." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5)

Before:

```
- You cannot ask questions. When blocked, stop and make the blocker your final message: what you
  finished, what stopped you, what the parent should decide.
```

After:

```
- You cannot ask questions, so carry the brief through to the end. Stop early only when you
  cannot go on without a decision from the parent, or before a risky step. Then make the blocker
  your final message: what you finished, what stopped you, what the parent should decide.
```

#### New hard rule, after line 48: scratch files

> "If you create any temporary new files, scripts, or helper files for iteration, clean up these files by removing them at the end of the task." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

Before:

```
- Report a check you could not run as "not run" with the reason. Never imply it passed.
```

After:

```
- Report a check you could not run as "not run" with the reason. Never imply it passed.
- Delete any scratch file or script you created to try things out before you report, so Files
  changed lists only the change.
```
