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

### Changed
- Route component authoring through `skill-creator` (no eval loop unless asked) and the plugin-dev agent, hook, and MCP skills; configure plugins through environment variables only
