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

### Changed

- Route component authoring through `skill-creator` (no eval loop unless asked) and the plugin-dev agent, hook, and MCP skills; configure plugins through environment variables only
