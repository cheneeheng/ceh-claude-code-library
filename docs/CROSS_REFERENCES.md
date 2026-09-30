# Cross-Reference Map

Tracks content duplicated word-for-word across multiple skills. When editing any entry,
update **all listed files**. Each block is intentionally inlined (zero file reads at runtime);
this map exists so edits don't get lost.

No entries yet. Add one when a migrated or new skill duplicates content from another, using this
shape:

```markdown
## <Shared block name>

**Canonical:** `plugins/ceh-<plugin>/skills/<skill>/SKILL.md` — § <section>

| Copy                                           | Section     | Diverges                               |
| ---------------------------------------------- | ----------- | -------------------------------------- |
| `plugins/ceh-<plugin>/skills/<skill>/SKILL.md` | § <section> | <what deliberately differs, or "none"> |

**Shared:** <what must stay identical across every copy>.
```

---
