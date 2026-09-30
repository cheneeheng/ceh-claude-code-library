---
name: <skill-name>
description: >-
  Load this skill when <the moment, as a verb phrase: "opening a PR", "writing a migration">:
  <what it makes Claude do, key use case first>. Trigger on "<user phrase>", "<user phrase>",
  "<user phrase>". Not for <near-miss task> (use ceh-<plugin>:<other-skill>).
---
<!-- TEMPLATE-GUIDANCE: delete this whole comment before committing. validate.py fails while it remains.

Frontmatter
- Keys in this order, only the ones that change behavior: name, description, argument-hint,
  arguments, disable-model-invocation, user-invocable, allowed-tools, disallowed-tools, model,
  effort, context, agent, background, paths, hooks, shell, compatibility, license, metadata.
- name: lowercase letters, digits, single hyphens, max 64 chars, equal to the directory name.
- description: always `>-`, 2-space indent, no blank lines, max 1024 chars. Triggers live here,
  not in `when_to_use` and not in the body.
- Any other value containing ": " gets single quotes: argument-hint: '[plan-file]'.
- Add `compatibility: >-` only when the skill needs software the machine may lack. Name the
  runtime, its minimum version, and what fails without it.

Body
- Headings are sentence case. Keep the sections below in this order and delete the optional ones
  you do not need. Do not add a "When to use" section: the description already carries it.
- Put the most important instruction first. After compaction Claude Code keeps only the first
  5,000 tokens of a skill.
- Write standing instructions ("after every edit, ..."), not one-time steps. Claude Code does not
  re-read the file on later turns.
- Imperative voice, concise. Give a reason only where a rule looks arbitrary without one.
- Keep content inline. Use references/ only for a schema or template shared by several skills, or
  a standard too large to inline. Reference bundled files as ${CLAUDE_SKILL_DIR}/<path>.
- Keep SKILL.md under 500 lines.
-->

# <Skill Title>

<One or two sentences: what this skill makes Claude do and what "done" looks like.>

## Procedure

1. <One action per step, imperative.>
2. <Step.>
3. <Step.>

## Rules

- <Standing constraint that holds for the whole task.> <Reason, only if the rule looks arbitrary
  without it.>
- <Rule.>

## Output

<Optional. The exact shape of what the skill produces: file path, template, or report format.
Delete this section when the skill produces nothing beyond edits.>

## Stop conditions

<Optional. When to stop and report instead of continuing.>

- <Condition> → <what to report>.

## Hands off to

<Optional. Explicit calls to other skills. An every-run call needs the target plugin in
`dependencies` and this exact wording; a conditional handoff stays prose.>

- Invoke the Skill tool with skill="ceh-<plugin>:<skill>" to <purpose>.
