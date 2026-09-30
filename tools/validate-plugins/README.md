# validate-plugins

Repo-integrity checker for the `ceh-*` plugins. Stdlib-only Python — runs locally on any OS
and in CI with no install step. Used by `.github/workflows/validate.yml`.

```bash
python tools/validate-plugins/validate.py
```

Exits non-zero and prints a grouped list of problems if any check fails.

## Checks

| Group         | What it verifies                                                                                                                                                                                                                                                              |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `manifests`   | Each `plugins/ceh-*/.claude-plugin/plugin.json` is valid JSON, `name` matches its directory, `version` is semver. `marketplace.json` lists every plugin with a matching version and an existing `source` path; no plugin is missing or unlisted.                              |
| `skills`      | Every `skills/<name>/SKILL.md` has `name` + `description` frontmatter and `name` matches the directory. `description` ≤ 1024 chars, `compatibility` ≤ 500.                                                                                                                    |
| `agents`      | Every `agents/<name>.md` has `name` + `description` frontmatter and `name` matches the file name.                                                                                                                                                                             |
| `keys`        | Names are lowercase-hyphenated, ≤ 64 chars. Every frontmatter key is one the Claude Code docs define; keys Claude Code ignores on plugin agents (`permissionMode`, `hooks`, `mcpServers`, `initialPrompt`) fail. No `TEMPLATE-GUIDANCE` comment is left over from a template. |
| `scalars`     | `description` uses the folded block scalar `>-`; no other key is an unquoted scalar containing `: `.                                                                                                                                                                          |
| `references`  | `references/...`, `${CLAUDE_PLUGIN_ROOT}/scripts/...` and `${CLAUDE_SKILL_DIR}/...` mentions in skill/agent files resolve to a real file.                                                                                                                                     |
| `skill-refs`  | `plugin:component` references resolve to an existing skill or agent.                                                                                                                                                                                                          |
| `deps`        | Every `dependencies` entry names a plugin in this repo, the graph is acyclic, a `ceh-scenario-*` bundle holds only `plugin.json` + `README.md` and reaches `ceh-scenario-core`, and only a bundle depends on a bundle.                                                        |
| `invocations` | Every `Invoke the Skill tool with skill="X"` resolves, is in-plugin or in a declared dependency, and does not set `disable-model-invocation: true`.                                                                                                                           |
| `scripts`     | `*.sh` pass `bash -n` (and `shellcheck` when available); `*.py` pass `py_compile`.                                                                                                                                                                                            |

`shellcheck` and `bash` are used when present and skipped otherwise, so a missing tool never
causes a false failure — CI runs them because GitHub-hosted Ubuntu runners ship both.
