# Changelog

Versions follow [Semantic Versioning](https://semver.org/).
Versions refer to the Marketplace versions. Release notes before this repo live in
[agent-skills](https://github.com/cheneeheng/agent-skills/blob/main/CHANGELOG.md).

---

## [Unreleased]

### Added

- Add the `add-plugin-component` repo skill with `SKILL.md` and agent templates as the base for every new component
- Add `tools/validate-plugins/validate.py` and its CI workflow, ported from agent-skills, now also rejecting undocumented frontmatter keys, malformed names, and leftover template guidance
- Add the empty `ceh-claude-code-library` marketplace and skeleton `CLAUDE.md`, `docs/CROSS_REFERENCES.md`, and `docs/PLUGIN_DEPENDENCIES.md` for migrated plugins to land into
- Add a pre-commit config that formats Python with ruff, Markdown and JSON with the official npm prettier, and shell scripts with shfmt
- Migrate `ceh-git-workflow` from agent-skills at `1.0.0`: its 11 skills (branch, commit, open-pr, merge, hotfix, release, code-review, dependency-management, update-changelog, merge-flow, release-flow) restructured onto the repo `SKILL.md` template, plus `scripts/check-semver.py` and its cross-reference entries
- Migrate `ceh-coding-agent` from agent-skills at `1.0.0`: 8 skills, 2 agents, hooks, scripts, and the output style, reshaped to this repo's templates with content unchanged. The `delegate-bulk-reads` eval suite stays in agent-skills
- Add the cross-cutting `ceh-core` plugin for standards that hold however Claude Code is used, seeded with `usage-limit-handoff`, `delegate-bulk-reads`, the `bulk-reader` agent, and their hooks moved out of `ceh-coding-agent`

### Changed

- Route component authoring through `skill-creator` (no eval loop unless asked) and the plugin-dev agent, hook, and MCP skills; configure plugins through environment variables only
- Point the `ceh-coding-agent` less-code hook at the full `write-less-code` skill so it loads before implementing, and gate the skill's runnable-check rule on tests being in scope

### Removed

- Archive the `repo-tree-mapper` agent and its `walk-repo.sh` script to `archive/ceh-coding-agent/`
