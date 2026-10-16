"""keys: skill/agent names are lowercase-hyphenated (<= 64 chars); every frontmatter key is one
Claude Code documents; no plugin-agent key Claude Code ignores; no TEMPLATE-GUIDANCE comment left
over from a template."""

from __future__ import annotations

import sys
from pathlib import Path

from common import NAME, agent_files, fail, main, parse_frontmatter, rel, skill_files

MAX_NAME_LEN = 64
TEMPLATE_MARKER = "TEMPLATE-GUIDANCE"

# Claude Code silently ignores unknown frontmatter keys, so a typo reads as working config.
# Sources: https://code.claude.com/docs/en/skills#frontmatter-reference
#          https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields
SKILL_KEYS = {
    "name",
    "description",
    "when_to_use",
    "argument-hint",
    "arguments",
    "disable-model-invocation",
    "user-invocable",
    "allowed-tools",
    "disallowed-tools",
    "model",
    "effort",
    "context",
    "agent",
    "background",
    "hooks",
    "paths",
    "shell",
    "metadata",
    "license",
    "compatibility",
}
AGENT_KEYS = {
    "name",
    "description",
    "tools",
    "disallowedTools",
    "model",
    "maxTurns",
    "skills",
    "memory",
    "background",
    "omitClaudeMd",
    "effort",
    "isolation",
    "color",
    "experimental",
}
# Valid on project agents, but Claude Code ignores them on plugin agents.
PLUGIN_AGENT_IGNORED_KEYS = {"permissionMode", "hooks", "mcpServers", "initialPrompt"}


def check_doc(path: Path, allowed_keys: set[str]) -> None:
    where = rel(path)
    if TEMPLATE_MARKER in path.read_text(encoding="utf-8"):
        fail(
            where,
            f"{TEMPLATE_MARKER} comment from the template is still present - delete it",
        )
    fm = parse_frontmatter(path)
    if fm is None:
        return  # `skills` and `agents` report the missing block
    for key in fm:
        if key not in allowed_keys:
            why = (
                "is ignored on plugin agents"
                if key in PLUGIN_AGENT_IGNORED_KEYS
                else "is not a documented key, so Claude Code ignores it silently"
            )
            fail(where, f"frontmatter '{key}' {why} - remove it")
    name = fm.get("name")
    if name and (not NAME.match(name) or len(name) > MAX_NAME_LEN):
        fail(
            where,
            f"name '{name}' must be lowercase letters, digits and single hyphens, "
            f"max {MAX_NAME_LEN} chars",
        )


def check() -> None:
    for path in skill_files():
        check_doc(path, SKILL_KEYS)
    for path in agent_files():
        check_doc(path, AGENT_KEYS)


if __name__ == "__main__":
    sys.exit(main(check))
