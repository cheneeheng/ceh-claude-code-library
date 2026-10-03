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

Two test skills: `run-hello` (writes a file, launches `hello-flow`, writes its returned path) and
`approval-test` (step 1, then stops at `awaiting-approval` in `run/state.md` until a message
contains `APPROVED`, then step 2).

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

The full step-by-step procedure (pwsh) is kept with the session notes in
`.agents_workspace/workflow-empirical-tests.md`, which is git-ignored. The essentials:

```powershell
# Is the Workflow tool loaded in -p?
claude -p 'hi' --settings '{"enableWorkflows": true, "disableWorkflows": false}' `
  --output-format stream-json --verbose |
  Select-String '"subtype":"init"' | ForEach-Object { $_.Line } > init.json
Select-String -Path init.json -Pattern 'Workflow' -Quiet

# Did a run actually launch a workflow?
claude -p 'Use the Workflow tool to run the saved workflow hello-flow with args {"word": "t2"}' `
  --settings '{"enableWorkflows": true, "disableWorkflows": false}' `
  --output-format stream-json --verbose > t2.jsonl
Select-String -Path t2.jsonl -Pattern '"name":"Workflow"'
```
