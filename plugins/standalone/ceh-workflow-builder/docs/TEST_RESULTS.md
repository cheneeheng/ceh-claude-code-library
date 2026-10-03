# Dynamic workflows: test results

Empirical tests run on 2026-10-03 to settle how Claude Code dynamic workflows behave interactively
and headless (`claude -p`), before designing the runner. [ARCHITECTURE.md](ARCHITECTURE.md) cites
these findings by number.

## Environment

| Item        | Value                                                            |
| ----------- | ---------------------------------------------------------------- |
| OS / shell  | Windows 11, PowerShell 7 (pwsh)                                  |
| Plan        | Claude Pro subscription                                          |
| Claude Code | 2.1.288                                                          |
| Repo        | a throwaway git repo with one saved workflow and two test skills |

Results on another plan, OS or version may differ. In particular F5, F8 and F12 are worth
re-checking after a Claude Code upgrade.

## Fixtures

`.claude/workflows/hello-flow.js` — one agent writes `out/<word>.txt`:

```js
export const meta = {
  name: "hello-flow",
  description: "Empirical test: one agent writes out/<word>.txt",
};

const word = (args && args.word) || "default";

const res = await agent(
  `Create the file out/${word}.txt containing exactly the text ${word}. Reply with the path you wrote.`,
  {
    schema: {
      type: "object",
      required: ["path"],
      properties: { path: { type: "string" } },
    },
  },
);

return res;
```

Two test skills, both saved with LF line endings.

`.claude/skills/run-hello/SKILL.md` launches `hello-flow` mid-flow and uses its result (T5). Step 2's
last sentence tests the F6 guard: does an explicit instruction stop the imitation?

```markdown
---
name: run-hello
description: >-
  Empirical test of a skill launching a saved workflow. Trigger on "run-hello".
disable-model-invocation: false
user-invocable: true
---

# Run Hello

1. Write `run/t5-before.txt` containing `before`.
2. Use the Workflow tool to run the saved workflow hello-flow with args `{"word": "t5"}` and wait for
   its result. If the Workflow tool is not available, stop and reply `T5 FAILED: no Workflow tool`.
   Do not do the workflow's work yourself.
3. Write `run/t5-after.txt` containing the `path` field the workflow returned.
4. Reply `T5 DONE`.
```

`.claude/skills/approval-test/SKILL.md` pauses for approval across sessions (T6, T7):

```markdown
---
name: approval-test
description: >-
  Empirical test of pause-for-approval across sessions. Trigger on "approval-test".
disable-model-invocation: false
user-invocable: true
---

# Approval Test

State lives in `run/state.md`. Read it first if it exists.

1. If `run/state.md` does not exist: write `run/step1.txt` containing `step1 done`, then write
   `run/state.md` with two lines: `step1: done` and `step2: awaiting-approval`.
2. If `step2` is `awaiting-approval` and the user's message does not contain the word `APPROVED`:
   reply exactly `AWAITING APPROVAL: step2` and stop. Do nothing else.
3. If `step2` is `awaiting-approval` and the user's message contains `APPROVED`: write
   `run/step2.txt` containing `step2 done`, set `step2: done` in `run/state.md`, reply `DONE`.
4. Never redo a step marked `done`.
```

**How a launch was detected.** Not by files on disk (see F6). Runs used
`--output-format stream-json --verbose` and searched the log for `"name":"Workflow"`.

## Tests

| Test | Question                                                                     | Result                                                                          |
| ---- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| T-1  | Is the Workflow tool in the `-p` tool list?                                  | No by default. Yes with `enableWorkflows: true` (F5, F8)                        |
| T0   | Does a hand-written `.claude/workflows/*.js` load as `/<name>`?              | Yes, after enabling workflows in `/config` and fixing line endings (F1, F2, F3) |
| T1   | In `-p` with no allow rule, is a launch denied?                              | Allowed on the test machine (F12)                                               |
| T2   | In `-p`, does "use the Workflow tool to run the saved workflow X" launch it? | Yes                                                                             |
| T3   | In `-p`, does `/<workflow-name>` launch it?                                  | No: "not installed" (F9)                                                        |
| T4   | In `-p`, does an own-words "use a workflow to ..." work?                     | Probably: one tool call matched in the log (F13)                                |
| T5   | Can a skill launch a saved workflow mid-flow and use its result?             | Yes, in `-p` (F10)                                                              |
| T6   | Pause for approval, resume with `claude -p --resume <id> 'APPROVED'`         | Continued at step 2, step 1 not redone, same `session_id` (F11, F14)            |
| T7   | Same pause, resumed in a fresh session from the state file only              | Continued at step 2 (F11)                                                       |

## Findings

| #   | Finding                                                                                                                                                                                                                   | Design consequence                                                                                            |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| F1  | On Pro, dynamic workflows are off by default. Saved workflows and `/deep-research` do not appear until **Dynamic workflows** is turned on in `/config`.                                                                   | The Workflow tool is not an assumed capability.                                                               |
| F2  | A workflow `.js` with CRLF line endings fails at launch: `script contains control characters that would be hidden in the approval dialog`. LF fixes it. pwsh `>` and `Set-Content` write CRLF.                            | The builder writes `.js` with LF and adds `.claude/workflows/*.js text eol=lf` to `.gitattributes`.           |
| F3  | Interactively, the Workflow tool exists once enabled.                                                                                                                                                                     | —                                                                                                             |
| F4  | Bash-style `\"` quoting is cut off by pwsh at the first `\"`. Single-quoted prompts with plain `"` inside work (PowerShell 7.3+).                                                                                         | Emitted invocation commands give a pwsh form.                                                                 |
| F5  | In `-p` the Workflow tool is absent by default, even with the `/config` toggle on. Claude searched the deferred tools for "workflow" and found none.                                                                      | The `/config` toggle does not reach `-p` sessions.                                                            |
| F6  | With no Workflow tool, Claude **imitated the workflow by hand**: it read the `.js`, wrote the file itself, and reported "the result the script would return". On disk it looked like success.                             | A missing tool fails the stage or runs its declared fallback. Imitation is forbidden.                         |
| F7  | A file write was allowed in a run meant to have no allow rules, so this machine's global settings already allowed writes.                                                                                                 | Check global settings before reading permission results.                                                      |
| F8  | `--settings '{"enableWorkflows": true, "disableWorkflows": false}'` puts the Workflow tool in the `-p` tool list. The same keys in `.claude/settings.json` also work. `enableWorkflows` is **not in the workflows docs**. | Headless runs pass the flag explicitly. Pin a minimum version; the runner's preflight catches a missing tool. |
| F9  | In `-p`, `/<workflow-name>` as the prompt fails with "not installed". A prompt naming the Workflow tool and the saved workflow launches it.                                                                               | The runner calls the Workflow tool by name.                                                                   |
| F10 | A skill launched a saved workflow mid-flow in `-p` and used its result in the next step.                                                                                                                                  | The runner can sequence workflow stages in both modes.                                                        |
| F11 | Pause for approval works across sessions, both with `--resume <session-id>` and from a fresh session reading the state file. Skill slash commands (`/approval-test`) work in `-p`.                                        | The state file is the record; `--resume` is a convenience. Headless approval = end the session, resume.       |
| F12 | With the tool on and no allow rule, a `-p` launch was allowed. The docs say `-p` evaluates the launch like any tool call, so this is likely machine-specific (F7).                                                        | Pass `--allowedTools 'Workflow(<name>)'` explicitly.                                                          |
| F13 | An own-words "use a workflow to ..." prompt in `-p` produced one matching tool call; two `Write` or two `Agent` calls would have counted 2, so it was almost certainly `Workflow`.                                        | Not relied on: the runner names the tool.                                                                     |
| F14 | `--resume` keeps the same `session_id`.                                                                                                                                                                                   | A run with several approvals can keep one session id.                                                         |

## Not tested

Recorded so the design does not assume them:

- What a workflow agent or subagent does in `-p` when it needs a tool not in `--allowedTools`.
  Expected: the call is denied and the agent fails or returns `null`.
- Whether `--resume` replays a stopped workflow's completed agents.
- A headless run hitting the usage limit. The docs say agents fail instead of waiting in `-p`.
- `enableWorkflows` alone, without `disableWorkflows: false`.
- Whether `claude -p` waits for a workflow launched directly by the prompt (T2) before exiting.
  T5 shows a skill waits for the result before its next step.

## Re-running

The procedure is in pwsh and needs PowerShell 7.3+ for the quoting (F4). Delete any `out/<word>.txt`
left by an earlier attempt before each rerun, because a file on disk does not prove a run (F6).

### Setup

```powershell
claude --version          # record it; >= 2.1.248 for /workflow-authoring
New-Item -ItemType Directory -Force ~/wf-test | Out-Null; Set-Location ~/wf-test; git init
New-Item -ItemType Directory -Force .claude/workflows, .claude/skills, out, run | Out-Null
# Global settings must not pre-allow what T1 tests (F7)
Select-String -Path ~/.claude/settings.json -Pattern 'Workflow|Write|Edit|disableWorkflows'
```

Turn on **Dynamic workflows** in `/config` (F1). Save the fixtures above, then check `hello-flow.js`
for CRLF and fix it (F2):

```powershell
$p = '.claude/workflows/hello-flow.js'
Select-String -Path $p -Pattern "`r" -Quiet     # True = CRLF present
[IO.File]::WriteAllText((Resolve-Path $p), ((Get-Content $p -Raw) -replace "`r`n", "`n").TrimStart([char]0xFEFF))
```

Every `-p` command below that launches a workflow also takes
`--settings '{"enableWorkflows": true, "disableWorkflows": false}'` (F8). It is left out below to
keep the lines short.

### T-1: Workflow tool loaded in `-p`?

```powershell
claude -p 'hi' --output-format stream-json --verbose |
  Select-String '"subtype":"init"' | ForEach-Object { $_.Line } > init.json
Select-String -Path init.json -Pattern 'Workflow' -Quiet
```

### T0: interactive load

Run `claude`, type `/` and check `hello-flow` is listed (else `/reload-skills`), run
`/hello-flow word t0`, approve with **Yes, run it**, check `/workflows` shows the run, then
`Get-Content out/t0.txt` should print `t0`.

### T1: `-p`, no allow rule

```powershell
claude -p 'Use the Workflow tool to run the saved workflow hello-flow with args {"word": "t1"}' `
  --output-format stream-json --verbose > t1.jsonl
Select-String -Path t1.jsonl -Pattern '"name":"Workflow"'
Select-String -Path t1.jsonl -Pattern 'permission_denials'
```

Then add allow rules for the remaining tests in `.claude/settings.json` (throwaway repo, so broad
file rules are fine):

```json
{
  "enableWorkflows": true,
  "disableWorkflows": false,
  "permissions": { "allow": ["Workflow(hello-flow)", "Read", "Edit", "Write"] }
}
```

### T2 to T4: launch forms in `-p`

```powershell
# T2: plain language naming the tool. Check the file at once to see whether -p waited.
claude -p 'Use the Workflow tool to run the saved workflow hello-flow with args {"word": "t2"}' `
  --output-format stream-json --verbose > t2.jsonl
Test-Path out/t2.txt

# T3: slash command. Expect "not installed" (F9).
claude -p '/hello-flow word t3' --output-format stream-json --verbose > t3.jsonl

# T4: own words, unsaved workflow. Change the allow rule to "Workflow" first, then back.
claude -p 'Use a workflow to create out/t4-a.txt and out/t4-b.txt in parallel, one agent each, each containing its own file name.' `
  --output-format stream-json --verbose > t4.jsonl

Select-String -Path t2.jsonl, t3.jsonl, t4.jsonl -Pattern '"name":"Workflow"'
```

### T5: skill launches a saved workflow

```powershell
claude -p '/run-hello' --output-format stream-json --verbose > t5.jsonl
Select-String -Path t5.jsonl -Pattern '"name":"Workflow"'
Get-Content run/t5-after.txt   # expect out/t5.txt
```

### T6: pause, resume by session id

```powershell
Remove-Item run/state.md, run/step*.txt -ErrorAction SilentlyContinue
claude -p '/approval-test' --output-format json > t6a.json
$a = Get-Content t6a.json -Raw | ConvertFrom-Json
$a.result                 # expect AWAITING APPROVAL: step2
$SID = $a.session_id
$before = (Get-Item run/step1.txt).LastWriteTime

claude -p --resume $SID 'APPROVED' --output-format json > t6b.json
$b = Get-Content t6b.json -Raw | ConvertFrom-Json
$b.result                 # expect DONE
(Get-Item run/step1.txt).LastWriteTime -eq $before   # expect True: step 1 not redone
$b.session_id -eq $SID    # expect True (F14)
```

### T7: pause, fresh session from the state file

```powershell
Remove-Item run/state.md, run/step*.txt -ErrorAction SilentlyContinue
claude -p '/approval-test' --output-format json > t7a.json
claude -p '/approval-test APPROVED' --output-format json > t7b.json   # no --resume
Get-Content run/state.md  # expect step2: done
```
