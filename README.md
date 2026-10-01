# ceh-claude-code-library

**WORK IN PROGRESS**

2026.09.30 - Migrating from [agent-skills](https://github.com/cheneeheng/agent-skills) repo.

## Plugins

| Plugin                | Install as         | Contents                                                                                                                                                                                                                                                                                                                                 |
| --------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Core                  | `ceh-core`         | Standards that hold however Claude Code is used: usage-limit guard + handoff (`usage-limit-handoff`); context economy (`delegate-bulk-reads`, `bulk-reader`, opt-in read guards)                                                                                                                                                         |
| Agent Coding Contract | `ceh-coding-agent` | Behavioral contract for coding agents (always-on via SessionStart hook); write-less-code minimalism (always-on via hooks); retroactive refactoring (`shrink-diff`, `refactor-repo`); explaining code until it lands; whole-repo orientation (`explain-codebase`); the `CEH Coding Agent` output style (always-on via `force-for-plugin`) |
| Git Workflow          | `ceh-git-workflow` | Branching, commits, pull requests from open to merge, changelog entries, releases including hotfixes, code review; a hook that blocks file edits on the default branch                                                                                                                                                                   |

### Categorization

| Tier                  | Loaded            | Plugins                                            |
| --------------------- | ----------------- | -------------------------------------------------- |
| **Scenario bundle**   | one per situation | —                                                  |
| **Cross-cutting**     | most sessions     | `ceh-core`, `ceh-coding-agent`, `ceh-git-workflow` |
| **Use-case workflow** | per activity      | —                                                  |
| **Stack / build**     | per project type  | —                                                  |

---

## Skills

### Core (`ceh-core`)

| Skill               | Invoke                          | When                                                                                                                                               |
| ------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage Limit Handoff | `/ceh-core:usage-limit-handoff` | Auto via PostToolUse guard hook when 5h or weekly usage crosses the threshold (default 90%) — stop cleanly, write a handoff artifact, end the turn |
| Delegate Bulk Reads | `/ceh-core:delegate-bulk-reads` | Before dispatching the `bulk-reader` agent, and before acting on its summary — the delegation prompt and the verification rules                    |

### Agent Coding Contract (`ceh-coding-agent`)

| Skill                    | Invoke                                       | When                                                                                                                                                                                                          |
| ------------------------ | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Agent Coding Contract    | `/ceh-coding-agent:agent-coding-contract`    | Start of any coding session (auto via SessionStart hook) — core rules, five-step workflow, stop conditions, non-goals                                                                                         |
| Write Less Code          | `/ceh-coding-agent:write-less-code`          | Every coding session (auto — per-turn digest via hook) — the minimalism ladder (YAGNI → stdlib → native → installed dep → one line)                                                                           |
| Shrink Diff              | `/ceh-coding-agent:shrink-diff`              | Branch functionally done, before the PR — retroactively apply write-less-code to the accumulated diff vs `main`                                                                                               |
| Refactor Repo            | `/ceh-coding-agent:refactor-repo`            | Manual only — propose-then-apply refactor campaign over the whole repo or a named module                                                                                                                      |
| Explain Until Understood | `/ceh-coding-agent:explain-until-understood` | Explaining a subsystem, design, or diff to the person in the session: stated floor, foundations first, verified claims, ASCII pictures, one walked case, and the escalation ladder when an explanation misses |
| Explain Codebase         | `/ceh-coding-agent:explain-codebase`         | Go through a whole repo and write what each component does, how they connect, and key flows into the ignored `.agents_workspace/CODEBASE_EXPLAINED.md`                                                        |

### Git Workflow (`ceh-git-workflow`)

| Skill            | Invoke                               | Auto-loads when                                                                                                                                                           |
| ---------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Branch           | `/ceh-git-workflow:branch`           | Creating or naming a branch; a PreToolUse hook denies file edits on the default branch until one exists                                                                   |
| Commit           | `/ceh-git-workflow:commit`           | Writing a commit message or staging changes                                                                                                                               |
| Pull Request     | `/ceh-git-workflow:pull-request`     | A branch is heading into `main`: open a PR, merge it (or a local branch), or land the branch in one pass — changelog under `[Unreleased]` → commit → PR → merge → cleanup |
| Release          | `/ceh-git-workflow:release`          | Ship a version: bump → changelog → PR → merge → tag → GitHub release; also tag-only and the hotfix variant                                                                |
| Code Review      | `/ceh-git-workflow:code-review`      | Reviewing a PR or leaving review comments                                                                                                                                 |
| Update Changelog | `/ceh-git-workflow:update-changelog` | Generate or update CHANGELOG.md, write release notes, or log a change under `[Unreleased]`                                                                                |

---

## Agents

### Core (`ceh-core`)

| Agent       | Invoke                  | When                                                                                                                                                       |
| ----------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bulk Reader | `/ceh-core:bulk-reader` | Read large or numerous files on Haiku and return a compressed, line-anchored answer to one question, keeping the file contents out of the caller's context |

---

## Installing in Claude Code

### Step 1 — Add the marketplace

```
/plugin marketplace add cheneeheng/ceh-claude-code-library
```

### Step 2 — Install plugins

```
/plugin install ceh-core@ceh-claude-code-library --scope user
/plugin install ceh-coding-agent@ceh-claude-code-library --scope user
/plugin install ceh-git-workflow@ceh-claude-code-library --scope user
```

### Manual installation (alternative)

```bash
git clone https://github.com/cheneeheng/ceh-claude-code-library.git ~/ceh-claude-code-library
```

Then add plugin paths to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "plugins": [
    { "path": "~/ceh-claude-code-library/plugins/ceh-core" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-coding-agent" },
    { "path": "~/ceh-claude-code-library/plugins/ceh-git-workflow" }
  ]
}
```

---

## Tools

| Tool             | Path                      | Purpose                                                                                                                                                                                         |
| ---------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| validate-plugins | `tools/validate-plugins/` | Repo-integrity checker run by CI (`.github/workflows/validate.yml`): plugin manifests, skill/agent frontmatter, file and skill references, dependencies, and script syntax. Stdlib-only Python. |

### Formatting

`.pre-commit-config.yaml` formats staged files on commit: ruff for Python, prettier (official npm
package) for Markdown and JSON, shfmt for shell scripts. Enable it once per clone:

```bash
pre-commit install
```
