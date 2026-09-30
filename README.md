# ceh-claude-code-library

**WORK IN PROGRESS**

2026.09.30 - Migrating from [agent-skills](https://github.com/cheneeheng/agent-skills) repo.


## Plugins

| Plugin | Install as | Contents |
|--------|-----------|---------|

### Categorization

| Tier | Loaded | Plugins |
|------|--------|---------|
| **Scenario bundle** | one per situation | — |
| **Cross-cutting** | most sessions | — |
| **Use-case workflow** | per activity | — |
| **Stack / build** | per project type | — |

---

## Skills

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
```

### Manual installation (alternative)

```bash
git clone https://github.com/cheneeheng/ceh-claude-code-library.git ~/ceh-claude-code-library
```

Then add plugin paths to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "plugins": [
  ]
}
```

---

## Tools

| Tool | Path | Purpose |
|------|------|---------|
| validate-plugins | `tools/validate-plugins/` | Repo-integrity checker run by CI (`.github/workflows/validate.yml`): plugin manifests, skill/agent frontmatter, file and skill references, dependencies, and script syntax. Stdlib-only Python. |
