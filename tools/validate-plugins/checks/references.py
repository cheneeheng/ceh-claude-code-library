"""references: `references/...`, `assets/...`, `${CLAUDE_PLUGIN_ROOT}/{scripts,references,assets}/...` and
`${CLAUDE_SKILL_DIR}/...` mentions in SKILL.md/agent files resolve to a real file."""

from __future__ import annotations

import re
import sys

from common import doc_files, fail, main, rel


def check() -> None:
    # Anchor on a top-level `references/` token (not preceded by another path
    # segment) so example paths like `docs/references/...` are not matched.
    ref_pat = re.compile(
        r"(?<![\w./-])(?:references|assets)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+"
    )
    script_pat = re.compile(
        r"\$\{CLAUDE_PLUGIN_ROOT\}/((?:scripts|references|assets)/[A-Za-z0-9_./-]+)"
    )
    # ${CLAUDE_SKILL_DIR} is substituted by Claude Code with the skill's own directory,
    # so these resolve relative to the SKILL.md, not the plugin root.
    skill_dir_pat = re.compile(r"\$\{CLAUDE_SKILL_DIR\}/([A-Za-z0-9_./-]+)")
    for doc in doc_files():
        where = rel(doc)
        # SKILL.md -> plugins/standalone/ceh-<plugin>/skills/<name>/SKILL.md ; agent -> plugins/standalone/ceh-<plugin>/agents/<name>.md
        plugin_root = (
            doc.parents[2] if doc.parent.parent.name == "skills" else doc.parents[1]
        )
        base_dir = doc.parent
        text = doc.read_text(encoding="utf-8")
        for rec in dict.fromkeys(ref_pat.findall(text)):
            if not (base_dir / rec).exists():
                fail(where, f"reference '{rec}' not found")
        for rec in dict.fromkeys(script_pat.findall(text)):
            if not (plugin_root / rec).exists():
                fail(where, f"plugin-root reference '{rec}' not found")
        for rec in dict.fromkeys(skill_dir_pat.findall(text)):
            if not (base_dir / rec).resolve().exists():
                fail(where, f"skill-dir reference '{rec}' not found")


if __name__ == "__main__":
    sys.exit(main(check))
