# Archive

Retired plugins and plugin contents (skills, agents, hooks, scripts) kept for reference.

Nothing here is published: `archive/` sits outside `plugins/`, so it is not listed in
`.claude-plugin/marketplace.json` and `tools/validate-plugins/validate.py` does not scan it.
Move content back under `plugins/` to revive it, and re-register it per `CLAUDE.md`.

## Scenario bundles (retired 2026-10-10)

`ceh-scenario-service`, `-library`, `-webapp`, `-ideation`, and `-editorial` were manifests that
installed other plugins as dependencies. They were retired because they did not fit the lifecycle
in `docs/STRATEGY.md`. Three were cut by stack and two by stage. A stack bundle installed all of
Build and Prove at once, up to 13 plugins, and refused to let any of them be disabled.
`docs/GETTING_STARTED.md` replaces them: a small core, then one plugin per stage. Their READMEs'
links to `docs/` were written for their old place under `plugins/scenarios/`.
