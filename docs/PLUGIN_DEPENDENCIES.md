# Plugin Dependencies

The current dependency graph between `ceh-*` plugins: every declared edge, the reference that
forces it, and what each scenario bundle installs. The rules for an edge are in `CLAUDE.md`
(Plugin Dependencies); this page holds the graph as it stands and the evidence behind each edge.

## The graph

No edges yet.

## Edge evidence

| From | To | Forcing reference |
|------|----|-------------------|

## What each scenario installs

| Bundle | Installs |
|--------|----------|

## Checking the graph

```bash
# Every declared edge
grep -H '"dependencies"' plugins/*/.claude-plugin/plugin.json

# Resolution, acyclicity, bundle shape, and that every bundle reaches ceh-scenario-core
python tools/validate-plugins/validate.py
```
