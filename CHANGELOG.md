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
- Add a `ceh-git-workflow` PreToolUse branch guard that denies file edits on the default branch until a feature branch exists, disabled with `CEH_BRANCH_GUARD=off`
- Add `docs/ENVIRONMENT_VARIABLES.md`, the index of every environment variable any plugin reads
- Migrate `ceh-architecture` from agent-skills at `1.0.0` as a standalone use-case workflow plugin: `document-architecture` and `domain-modeling`, both invocable by name. The SessionStart invariants hook is not migrated: it injected layering rules into every session and pushed unrequested `ARCHITECTURE.md` upkeep, and the skill descriptions already carry the triggers. The README no longer points at plugins that have not migrated
- Migrate `ceh-seo` from agent-skills at `1.0.0` as a standalone use-case workflow plugin: `make-page-crawlable` (was `web-discoverability`), `pitch-project` (was `text-discoverability`), and `write-llms-txt`. The `write-llms-txt` eval suite stays in agent-skills, and references to plugins that have not migrated become prose
- Migrate `ceh-blog` from agent-skills at `1.0.0` as a standalone use-case workflow plugin: `draft-post`, `edit-post`, and `repurpose-post`. `blog-interviewer` and `blog-writer` merge into `draft-post`, which interviews when the material is thin and drafts directly when it is rich, so the shared Voice and post-type blocks exist once
- Add the shared blog voice, blog post-type structures, and GEO writing rules to `docs/CROSS_REFERENCES.md`

### Changed

- Route component authoring through `skill-creator` (no eval loop unless asked) and the plugin-dev agent, hook, and MCP skills; configure plugins through environment variables only
- Point the `ceh-coding-agent` less-code hook at the full `write-less-code` skill so it loads before implementing, and gate the skill's runnable-check rule on tests being in scope
- Consolidate `ceh-git-workflow` from 11 skills to 6: `open-pr`, `merge` and `merge-flow` become `pull-request`, and `release-flow` and `hotfix` fold into `release`, so a compound request loads two skills instead of one per step
- Make `ceh-git-workflow` stack-agnostic: Python and TypeScript checks, the coverage table, and `ARCHITECTURE.md` references are replaced by stack-neutral rules
- State `disable-model-invocation`, `user-invocable`, and `license` in every skill's frontmatter and in the `SKILL.md` template; `agent-coding-contract`, `write-less-code`, `usage-limit-handoff`, `delegate-bulk-reads` and `branch` become model-only, so they no longer appear as slash commands
- Trim the descriptions of the hook-loaded skills `agent-coding-contract`, `usage-limit-handoff` and `delegate-bulk-reads` to one line each, since their hooks name them explicitly and no trigger phrases are needed
- Require `model` in every agent's frontmatter, enforced by `validate.py`

- Name skills with a verb phrase and agents with a noun, with two exemptions (model-only standards, established terms of art). The rule lives in `CLAUDE.md` and the `SKILL.md` template guidance

### Removed

- Archive the `repo-tree-mapper` agent and its `walk-repo.sh` script to `archive/ceh-coding-agent/`
- Archive `ceh-git-workflow:dependency-management` to `archive/ceh-git-workflow/` until a stack plugin can own it
