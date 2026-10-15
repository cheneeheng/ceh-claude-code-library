| # | Topic | Outcome | Status |
| --- | --- | --- | --- |
| 1 | Scope and target | Audited 3 `SKILL.md` files plus the README and `plugin.json`, against Claude Sonnet 5.5. Groups 3 and 4 do not apply. | assumed |
| 2 | `twine` is not a declared tool | `publish-python-library` runs `uv run twine check`, but the skill's own `compatibility` says only `mypy` and `pytest` are installed. | proposed, not applied |
| 3 | Service wording left in the tests skill | The coverage table still reads "application package" and "domain services", although the README says the library copy dropped service content. | proposed, not applied |
| 4 | Restated defaults in the env skill | The naming table, the import-grouping block and the `time.sleep` line restate PEP 8 and what `ruff` already enforces. | proposed, not applied |
| 5 | Generic semver table | The three-row semver table restates the spec. Only the "behavior consumers depend on" clause and the no-reuse rule are repo-specific. | proposed, not applied |
| 6 | Flag-only items | Three low-confidence items with no edit proposed. | your call |

**Scope and target**

- The scope is the whole plugin directory you named. It holds no hooks, agents or scripts, and none of the skills pins a model. I treated the target as the model running this audit, Claude Sonnet 5.5, and I did not ask you to confirm it.
- Counts: Group 1 has 2 findings (padding), Group 2 has 2 (a stale fact and a service remnant), Groups 3 and 4 are not applicable (no tool definitions, no request code), and there are 3 flags.
- Not found: pressure language, scaffolds that API features replaced, prefill, thinking prose, retired model names, and conflicts between instruction files. I grepped for `MUST|NEVER|ALWAYS|CRITICAL`, and the few hits are reasoned rules about `uv.lock`, `.env`, `--no-verify` and `strict = true`. Keep them.
- I read the three skills in full and grepped for `twine`, `pytest-asyncio` and `pytest-mock`. I did not run `git blame` (a compound shell command was refused), so no finding rests on provenance.

**`twine` is not a declared tool**

- **High confidence, `rewrite`.** `publish-python-library/SKILL.md:126` says `uv run twine check dist/*`, but `SKILL.md:11-13` says only the `mypy` and `pytest` dev dependencies are installed, and nothing in the plugin adds `twine`. A fresh `uv sync` therefore fails at this step. `uvx` runs it without a dev dependency.

```diff
--- a/skills/publish-python-library/SKILL.md
+++ b/skills/publish-python-library/SKILL.md
@@ -126
-uv run twine check dist/*     # validate metadata before upload
+uvx twine check dist/*        # validate metadata before upload
```

**Service wording left in the tests skill**

- **Medium confidence, `rewrite`.** `write-pytest-library-tests/SKILL.md:86-87` carries "Python application package" and "Core business logic / domain services". The README (`README.md:26-29`) and `docs/CROSS_REFERENCES.md:219,233` say the library copies dropped service content. A library has a public API, not domain services.

```diff
--- a/skills/write-pytest-library-tests/SKILL.md
+++ b/skills/write-pytest-library-tests/SKILL.md
@@ -84,4
 | Area                                  | Floor |
 | ------------------------------------- | ----- |
-| Python application package            | 80%   |
-| Core business logic / domain services | 95%   |
+| Library package                       | 80%   |
+| Public API and core logic             | 95%   |
```

**Restated defaults in the env skill**

- **Medium confidence, `remove`.** `configure-python-library-env/SKILL.md:105-127` holds a PEP 8 naming table, a three-group import example and a `time.sleep` warning. The model already knows these, and `ruff` with `I` selected enforces the imports. This is the "could the model already know this" test. Keep the 88-column rule, the type-hint rules and the Google docstring example, which are repo choices.

```diff
--- a/skills/configure-python-library-env/SKILL.md
+++ b/skills/configure-python-library-env/SKILL.md
@@ -104,25
-**Naming:**
-
-| Kind                 | Convention            | Example                         |
-| -------------------- | --------------------- | ------------------------------- |
-| Variables, functions | `snake_case`          | `parse_duration`, `max_retries` |
-| Classes              | `PascalCase`          | `RetryPolicy`                   |
-| Constants            | `UPPER_SNAKE_CASE`    | `DEFAULT_TIMEOUT`               |
-| Private members      | `_leading_underscore` | `_normalize`                    |
-
-**Imports** (three groups, separated by blank lines):
-
-```python
-# 1. Standard library
-import asyncio
-...
-from your_library.core import RetryPolicy
-```
-
-Never use `time.sleep()` in async code — use `await asyncio.sleep()`.
```

- The `Imports` line also carries a risk. Its example imports `pydantic`, a runtime dependency that contradicts the "minimal dependencies" rule two sections earlier. Removing it fixes that too.

**Generic semver table**

- **Medium confidence, `rewrite`.** `publish-python-library/SKILL.md:52-58` is the semver spec in table form. A one-line version keeps the two repo-specific points and drops the rest.

```diff
--- a/skills/publish-python-library/SKILL.md
+++ b/skills/publish-python-library/SKILL.md
@@ -50,9
-| Increment | When ... |
-| ... three-row table ... |
-
-When in doubt, bump the higher level — a surprise break is worse than a cautious bump. Never re-use or lower a version.
+The public API decides the level: a removed or renamed symbol, a changed signature, or changed
+behavior consumers depend on is MAJOR, a new symbol or optional parameter is MINOR, anything with no
+public effect is PATCH. When in doubt, bump the higher level. Never re-use or lower a version.
```

**Flag-only items**

- **`asyncio_mode = "auto"`.** It appears at `configure-python-library-env/SKILL.md:77-78`, with `pytest-asyncio` named at `write-pytest-library-tests/SKILL.md:23`, but no skill declares that plugin as a dev dependency. Without it, `pytest` warns about an unknown config key. This may be a leftover from the service copy, or a deliberate default for async libraries, so I left it for you.
- **`requires-python = ">=3.12"`.** It is shown as the default in both `SKILL.md` files. For a distributable library the floor is a consumer-facing decision, and 3.12 is a pin that will age. Low confidence, and the repo may intend it.
- **`SKILL.md:140` in `publish-python-library`.** Its "No web dependencies" rule duplicates `configure-python-library-env/SKILL.md:51-52`. Both copies agree, so keep-list item 8 says leave them.

---

I applied no edits, because you did not ask for them. If you do, the three skills are duplicated from `ceh-python-service`, so hunks 3 and 4 need the mirror check in `docs/CROSS_REFERENCES.md` (lines 219 and 233). Any applied change needs a version bump in `plugin.json` and `marketplace.json`, a `CHANGELOG.md` entry and `docs/PLUGIN_VERSIONS.md` rows, and `python tools/validate-plugins/validate.py` before commit. I did not run the validator.
