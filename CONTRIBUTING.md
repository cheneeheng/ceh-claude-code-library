# Contributing

How to work on this repo. What the plugins are and how to install them is in the
[`README.md`](README.md). The rules every change follows are in [`CLAUDE.md`](CLAUDE.md), the
decision files in [`.claude/rules/`](.claude/rules/), and [`docs/VISION.md`](docs/VISION.md). Add a skill, agent, hook, or plugin with the repo-local
`add-plugin-component` skill in `.claude/skills/`.

## Tools

| Tool             | Path                      | Purpose                                                                                                                                                                                                                                                            |
| ---------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| setup            | `tools/setup/`            | Set up a machine and folder for the plugins: installs the tools the picked plugins need, the plugins themselves, the skill listing budget and the statusline, each after a yes. Its `TOOLS`/`PLUGINS` registry is checked by `setup-registry`. Stdlib-only Python. |
| skills-sync      | `tools/skills-sync/`      | Copy individual skills (from this repo or any other) into a project's `.claude/skills/` directory: install, update, add, remove, list. Python, bash, PowerShell, and browser-based HTML implementations.                                                           |
| validate-plugins | `tools/validate-plugins/` | Repo-integrity checker run by CI (`.github/workflows/validate.yml`): plugin manifests, skill/agent frontmatter, file and skill references, dependencies, and script syntax. Stdlib-only Python.                                                                    |

Run the CI gate locally before you push:

```bash
python tools/validate-plugins/validate.py
python -m unittest discover -s tools/validate-plugins/tests
python -m unittest tools/setup/test_setup.py
```

The mod tests are not in CI, because they need Claude Code on the runner. Run them before you push
a change to `plugins/standalone/ceh-every-session/hooks/`:
`claude plugin test plugins/standalone/ceh-every-session`, and before you push a change to
`plugins/standalone/ceh-session-orchestration/hooks/`:
`claude plugin test plugins/standalone/ceh-session-orchestration`.

## Formatting

`.pre-commit-config.yaml` formats staged files on commit: ruff for Python, prettier (official npm
package) for Markdown and JSON, shfmt for shell scripts. Enable it once per clone:

```bash
pre-commit install
```
