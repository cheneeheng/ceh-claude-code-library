# Model audit: ceh-python-library

- Date: 2026-10-15
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-python-library.doctor.md](ceh-python-library.doctor.md).

## Kept changes

### plugins/standalone/ceh-python-library/skills/publish-python-library/SKILL.md:126
- **Rule:** 3, a command the skill never declares.
- **Backing:** The file's own `compatibility` (lines 11-13) says "verifying the public surface uses the project's `mypy` and `pytest` dev dependencies". Nothing in the plugin installs `twine`, so `uv run twine` fails after a fresh `uv sync`.
- **Change:**
  - Before: `uv run twine check dist/*     # validate metadata before upload`
  - After: `uvx twine check dist/*        # validate metadata before upload`

### plugins/standalone/ceh-python-library/skills/publish-python-library/SKILL.md:19-21
- **Rule:** 4, a missing statement of when the task is done, added to the file's opening. The other two skills already have one.
- **Backing:** Not applicable beyond rule 4.
- **Change:**
  - Before: `... The public API decides the version,\nand the version decides the release.`
  - After: `... The public API decides the version,\nand the version decides the release. Done when the wheel and sdist build, \`uvx twine check\` passes, and a TestPyPI install imports the public API.`

### plugins/standalone/ceh-python-library/skills/publish-python-library/SKILL.md:50-58
- **Rule:** 2.
- **Backing:** "Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality. Review and consider removing older instructions if default performance is better." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- **Models:** This benefits Fable 5, and by the 5.1 guide's statement that Fable 5 prompts carry over, Fable 5.1. The Opus 5, Opus 5.5, Sonnet 5 and Sonnet 5.5 guides say nothing about trimming restated spec text, so those models are unaffected. The rewrite keeps every repo-specific point, so no model loses information.
- **Change:**
  - Before:
    ```
    For a library, the version contract is about the public API, not internal changes.

    | Increment | When ... |  (three-row MAJOR/MINOR/PATCH table)

    When in doubt, bump the higher level — a surprise break is worse than a cautious bump. Never re-use or lower a version.
    ```
  - After:
    ```
    The public API decides the level: a removed or renamed symbol, a changed signature, or changed
    behavior consumers depend on is MAJOR, a new symbol or optional parameter is MINOR, anything with no
    public effect is PATCH. When in doubt, bump the higher level. Never re-use or lower a version.
    ```

### plugins/standalone/ceh-python-library/skills/configure-python-library-env/SKILL.md:105-127
- **Rule:** 2, with rule 3 for the `pydantic` example.
- **Backing (rule 2):** The same Fable 5 quote and URL as above. The Naming table, the import-grouping block and the `time.sleep` line restate PEP 8. `ruff` with `I` selected already enforces the imports.
- **Backing (rule 3):** The import example uses `from pydantic import BaseModel`. That contradicts the same file's "Keep the runtime dependency set minimal" (line 51).
- **Models:** This benefits Fable 5 and Fable 5.1. The other guides are silent, so those models are unaffected, and the removed text is something every model already knows.
- **Change:**
  - Before: the `**Naming:**` table, the `**Imports** (three groups...)` block with the `pydantic` example, and `Never use \`time.sleep()\` in async code — use \`await asyncio.sleep()\`.`
  - After: all three removed. The 88-column rule, the type-hint rules and the Google docstring example stay.

### plugins/standalone/ceh-python-library/skills/configure-python-library-env/SKILL.md:86
- **Rule:** 4, a negative instruction rewritten as the positive one it implies.
- **Backing:** "Tell Claude what to do instead of what not to do" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices). That page states it for response formatting, so this change rests on rule 4 and the same meaning is kept.
- **Change:**
  - Before: `- Do not use \`Any\` without a comment explaining why`
  - After: `- Use \`Any\` only with a comment explaining why`

### plugins/standalone/ceh-python-library/skills/configure-python-library-env/SKILL.md:141
- **Rule:** 4, same basis as the previous change.
- **Change:**
  - Before: `Do not use \`# type: ignore\` without a comment. Do not downgrade \`strict = true\` to silence errors.`
  - After: `Give every \`# type: ignore\` a comment. Keep \`strict = true\` when errors appear.`

### plugins/standalone/ceh-python-library/skills/write-pytest-library-tests/SKILL.md:86-87
- **Rule:** 3, an inconsistency inside the plugin.
- **Backing:** The skill's opening says "Write library tests against the public API". Its coverage table still names an "application package" and "domain services", which the plugin's README says the library copy dropped. A library has a public API, not domain services.
- **Change:**
  - Before: `| Python application package            | 80%   |` and `| Core business logic / domain services | 95%   |`
  - After: `| Library package                       | 80%   |` and `| Public API and core logic             | 95%   |`

**Dropped from the report:** the three flag-only items (`asyncio_mode`, `requires-python`, the duplicated "No web dependencies" rule). The report proposes no edit for them, and no page above calls for one.

**Bookkeeping that follows from these edits:**
- This plugin's `plugin.json` and `.claude-plugin/marketplace.json` need a PATCH bump.
- `CHANGELOG.md` needs an entry and `docs/PLUGIN_VERSIONS.md` needs rows.
- The mirror copies listed at `docs/CROSS_REFERENCES.md:219,233` need the same changes.
