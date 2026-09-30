# ceh-claude-code-library

**WORK IN PROGRESS**

2026.09.30 - Migrating from [agent-skills](https://github.com/cheneeheng/agent-skills) repo.

## Plugins

| Plugin       | Install as         | Contents                                                                                                                                                   |
| ------------ | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Git Workflow | `ceh-git-workflow` | Commits, branching, PRs, merging, changelog entries, releases, code review, dependency management, plus the `merge-flow` and `release-flow` orchestrations |

### Categorization

| Tier                  | Loaded            | Plugins            |
| --------------------- | ----------------- | ------------------ |
| **Scenario bundle**   | one per situation | —                  |
| **Cross-cutting**     | most sessions     | `ceh-git-workflow` |
| **Use-case workflow** | per activity      | —                  |
| **Stack / build**     | per project type  | —                  |

---

## Skills

### Git Workflow (`ceh-git-workflow`)

| Skill                 | Invoke                                    | Auto-loads when                                                                                                                                            |
| --------------------- | ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Branch                | `/ceh-git-workflow:branch`                | Creating or naming a branch                                                                                                                                |
| Commit                | `/ceh-git-workflow:commit`                | Writing a commit message or staging changes                                                                                                                |
| Open PR               | `/ceh-git-workflow:open-pr`               | Opening a pull request, writing a PR description, checking the definition of done, or enabling auto-merge on repos that allow it                           |
| Merge                 | `/ceh-git-workflow:merge`                 | Merging a PR (immediate or auto-merge) or a local branch into `main`, then cleaning up the branch afterward                                                |
| Hotfix                | `/ceh-git-workflow:hotfix`                | Executing a critical production fix                                                                                                                        |
| Release               | `/ceh-git-workflow:release`               | Tagging a release or bumping a version                                                                                                                     |
| Code Review           | `/ceh-git-workflow:code-review`           | Reviewing a PR or leaving review comments                                                                                                                  |
| Dependency Management | `/ceh-git-workflow:dependency-management` | Adding, removing, or upgrading a package                                                                                                                   |
| Update Changelog      | `/ceh-git-workflow:update-changelog`      | Generate or update CHANGELOG.md, write release notes, or log a change under `[Unreleased]`                                                                 |
| Merge Flow            | `/ceh-git-workflow:merge-flow`            | Land the branch you are on in one pass — changelog under `[Unreleased]` → README → commit → PR → merge → cleanup, with no version bump and no tag          |
| Release Flow          | `/ceh-git-workflow:release-flow`          | Ship a complete release in one pass — version bump → changelog → README → CLAUDE.md → PR → merge → tag → release, sequencing the skill that owns each step |

---

## Agents

---

## Installing in Claude Code

### Step 1 — Add the marketplace

```
/plugin marketplace add cheneeheng/ceh-claude-code-library
```

### Step 2 — Install plugins

```
/plugin install ceh-git-workflow@ceh-claude-code-library --scope user
```

### Manual installation (alternative)

```bash
git clone https://github.com/cheneeheng/ceh-claude-code-library.git ~/ceh-claude-code-library
```

Then add plugin paths to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "plugins": [{ "path": "~/ceh-claude-code-library/plugins/ceh-git-workflow" }]
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
