---
name: <agent-name>
description: >-
  Use this agent to <task> in an isolated subagent instead of the main session, because <why
  isolation helps: output volume, cheaper model, read-only guarantee>. Use proactively when
  <condition>. Invoke for "<user phrase>", "<user phrase>". <Read-only: it reports, never edits.>
  Not for <near-miss task> (use ceh-<plugin>:<skill-or-agent>).
model: inherit
tools: Read, Grep, Glob
---
<!-- TEMPLATE-GUIDANCE: delete this whole comment before committing. validate.py fails while it remains.

Frontmatter
- Keys in this order, only the ones you need: name, description, model, effort, tools,
  disallowedTools, skills, maxTurns, memory, background, omitClaudeMd, color.
- name: lowercase letters, digits, single hyphens, equal to the file name without `.md`.
- description: always `>-`, 2-space indent, no blank lines, max 1024 chars. Keep it short: every
  agent description loads into every session. Prose only, no <example> blocks.
- model: inherit | sonnet | haiku | opus. Pick a cheaper model when the job is mechanical.
- tools: the smallest set the job needs. Background subagents (the default) silently lose any
  built-in tool outside Read, Grep, Glob, LSP, Bash, PowerShell, Edit, Write, NotebookEdit,
  WebFetch, WebSearch, TodoWrite, Skill, ToolSearch, EnterWorktree, ExitWorktree, Monitor,
  TaskStop, SendMessage, Artifact. AskUserQuestion is never available to a subagent.
- skills: fully qualified `ceh-<plugin>:<skill>` entries, one per line. This is the only way a
  standard reaches the agent: SessionStart hooks do not fire for subagents.
- Never set permissionMode, hooks, mcpServers, or initialPrompt: Claude Code ignores them on plugin
  agents. Never set isolation: worktree (see add-plugin-component step 2).

Body
- The body is the whole system prompt. The agent does not get the Claude Code system prompt or
  the parent conversation, so state everything it needs.
- Headings are sentence case. Keep the sections below in this order.
- Imperative voice, concise. Give a reason only where a rule looks arbitrary without one.
-->

You are a <role>. You <core job> and return <what the parent session receives>.

## Process

1. <One action per step, imperative.>
2. <Step.>
3. **Report.** Return the output below as your final message.

## Output to parent session

<The exact shape of the final message. Lead with the result, ranked or grouped; cap its length.>

```
<example of the output format>
```

## Hard rules

- <Constraint that holds for the whole run, e.g. "Never edit a file: you report, you do not fix".>
- You cannot ask questions. When blocked, stop and make the blocker your final message: what you
  finished, what stopped you, what the parent should decide.
- Report a check you could not run as "not run" with the reason. Never imply it passed.
