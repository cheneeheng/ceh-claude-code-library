---
name: commit
description: >-
  Load this skill when making a git commit or writing its message: Conventional Commits type and
  scope, subject line, body, and footers for breaking changes and issue references.
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Requires the git CLI on PATH, a git working tree, and a configured `user.name` / `user.email`.
  If the repo installs commit hooks, their interpreters (e.g. Python for pre-commit) must also be
  present - none is assumed by this skill itself.
license: Apache-2.0
---

# Commit

Every commit is one logical change with a Conventional Commits message:

```
<type>(<scope>): <short summary>

[optional body — explain why, not what]

[optional footer — breaking changes, issue refs]
```

## Procedure

1. Stage one logical change: `git add <files>`.
2. Single-line message (subject only):

   ```bash
   git commit -m "<type>(<scope>): <short summary>"
   ```

3. Multi-line (body or footer needed) — write the message to a temp file and commit with `-F`,
   then delete the file:

   ```bash
   # Write the message to msg.txt:
   #   <type>(<scope>): <short summary>
   #
   #   <body — explain why, not what>
   #
   #   <footer — BREAKING CHANGE or Closes #NNN>
   git commit -F msg.txt && rm msg.txt
   ```

   Never build a multi-line message with an inline shell heredoc or a PowerShell `@'...'@`
   here-string: the temp-file path avoids all shell quoting and behaves identically in PowerShell
   and Bash.

## Rules

### Types

`feat`, `fix`, `refactor` (no behavior change), `perf`, `test`, `docs`, `style` (formatting only),
`build`, `ci`, `chore` (anything not covered above), `revert` (body: `Reverts <sha>`).

### Scope

The optional `(<scope>)` names the area of the codebase touched — a module, package, or
component (`auth`, `orders`, `api`). Pick the narrowest noun that covers the change. Omit the
parentheses entirely for repo-wide changes (`chore: bump all dev dependencies`). Keep it
lowercase and consistent with scopes already used in the log (`git log --oneline`).

### Message

- One logical change per commit. Don't mix a refactor with a feature, or two unrelated fixes —
  split them so each can be reviewed and reverted on its own.
- Subject line: imperative mood ("add", not "added"/"adds"), lowercase, no trailing period,
  ≤ 72 characters.
- Body: explain _why_, not _what_ — the diff already shows what changed. Wrap at 72 columns.
  Use `-` bullets for multiple points. Separate it from the subject with one blank line.
- Breaking changes: `BREAKING CHANGE:` footer with migration notes (or a `!` after the
  type/scope: `feat(api)!: ...`).
- Reference issues: `Closes #123` (auto-closes on merge) or `Refs #456` (links only) in footer.
- Attribution: end the commit message with the `attribution.commit` line the session's Git
  instructions supply, verbatim. Never substitute a literal from this skill or from memory. If no
  line is supplied, or the setting is `false` or empty, omit it.

## Output

```
bad:  fixed bug                          # not imperative, no type/scope, vague
good: fix(orders): reject cancel on shipped orders
```
