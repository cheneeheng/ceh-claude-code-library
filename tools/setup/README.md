# setup

One script that gets a machine and a folder ready for the `ceh-*` plugins. It finds the tools
the plugins you pick need and installs each missing one after you say yes. It installs or
enables those plugins for the current folder, and sets the Claude Code settings they rely on.
Nothing changes without a yes.

## Run it

Open PowerShell or Windows Terminal (Windows) or any terminal (Linux, macOS) in the folder you
are about to work in, then:

```
uv run https://raw.githubusercontent.com/cheneeheng/ceh-claude-code-library/main/tools/setup/setup.py
```

`uv run` brings its own Python, so this needs only `uv`. Without `uv`, install it first:

| Platform      | Command                                                                               |
| ------------- | ------------------------------------------------------------------------------------- |
| Windows       | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` |
| Linux / macOS | `curl -LsSf https://astral.sh/uv/install.sh \| sh`                                    |

Or download `setup.py` and run `python3 setup.py` with Python 3.10 or later.

## Options

| Option            | Effect                                                                            |
| ----------------- | --------------------------------------------------------------------------------- |
| `--check`         | Report only: what is missing and what it would do. Installs and writes nothing.   |
| `--scope <scope>` | `local` (default, this folder only), `project` or `user` for plugins it installs. |
| `--plugins a,b`   | Set up these plugins instead of choosing from the list.                           |

With no terminal to answer, as in an agent's shell, the script is report-only whatever the
flags. On Windows, Git Bash's terminal (mintty) may not count as a terminal either: run it from
PowerShell or Windows Terminal to install.

## What it does

Each step prints a section, and a second run changes nothing already in place.

1. **Claude Code.** Stops if `claude` is not on `PATH`, because nothing else can be installed.
2. **Marketplace.** Adds `ceh-claude-code-library` after a yes, when it is missing.
3. **Choose plugins.** A numbered list grouped as in
   [`docs/GETTING_STARTED.md`](../../docs/GETTING_STARTED.md). Enter alone takes the core:
   `ceh-every-session`, plus `ceh-git-workflow` and `ceh-coding-conduct` in a git repo.
4. **Tools.** Checks `python3`, `bash`, `git`, `gh`, `uv`, Bun and Node.js, only those the picks
   need, and offers each missing one's install command. Then it reports whether `gh` is logged
   in and git's name and email are set. It never logs in or sets them for you.
5. **Plugins.** A picked plugin that is off is enabled at the scope it is installed at, with the
   pick as the yes. Those not installed are installed at `--scope`, after one yes. A plugin whose required tool is still missing is skipped, with a
   warning naming its skills. A plugin that only loses part of its function is installed, with a
   warning naming what it loses.
6. **Skill listing budget.** Raises `skillListingBudgetFraction` to `0.02` in your Claude Code
   `settings.json` (in `$CLAUDE_CONFIG_DIR` when set), keeping every other key and any higher
   value.
7. **Statusline.** With `ceh-every-session` picked and no `statusLine` set, offers to install
   [statusline-hook](https://github.com/cheneeheng/claude-code-command-center/tree/slh-v0.4.0/tools/statusline-hook),
   which feeds the usage-limit guard its quota readings. A `statusLine` you already have is never
   replaced: the script only reports whether the guard gets readings.
8. **Summary.** What changed, what is missing, and every warning. Run `/reload-plugins` after.

To undo it, run `claude plugin uninstall <plugin>@ceh-claude-code-library --scope <scope>` and
each tool's own uninstaller. The summary names everything the script changed.

## Platforms

Windows is tested. Linux and macOS are built but untested. `uv` and Bun install through their
own install scripts. The other tools install with `winget` on Windows, `brew` on macOS, and
`apt-get` through `sudo` on Linux. When that installer is not on `PATH`, the script names the
tool's install page instead. Node.js has no Linux
installer here, because Ubuntu's `nodejs` package is older than the 20 the web skills need. The
Linux statusline needs `jq`.

## For maintainers

`TOOLS` and `PLUGINS` at the top of `setup.py` say what each plugin needs. The `setup-registry`
check in [`tools/validate-plugins`](../validate-plugins/README.md) fails when they drift from the
plugins, their skills, their dependencies, or a skill's `compatibility` field, so a new plugin or
skill needs its entry here in the same PR. Tests: `python -m unittest tools/setup/test_setup.py`.
