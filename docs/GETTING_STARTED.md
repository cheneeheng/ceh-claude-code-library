# Getting started

Which plugins to install the first time, and which to leave out until you need them. Do not install
all of them: every installed plugin adds its skill descriptions to every session, and the ones
with hooks run on every session too. Install a small core once, then add one plugin when you reach
the moment it serves.

The route below follows the product lifecycle in [`STRATEGY.md`](STRATEGY.md): Shape, Build, Prove,
Tell. You can start at any stage. Each plugin works installed alone, and with several installed they
chain through the committed files each one writes.

There are three ways through the same route. Pick one and skip the other two:

- [Let Claude set you up](#let-claude-set-you-up): Claude asks what you are about to do and runs
  the installs.
- [Set up with the script](#set-up-with-the-script): the same from a terminal, plus the tools and
  settings the plugins need.
- [Steps 1 to 5](#1-add-the-marketplace): every command written out, to run yourself.

## Let Claude set you up

Open Claude Code in the folder you are about to work in, a git repo or any plain folder, and type:

```
install the Claude Code plugins from https://raw.githubusercontent.com/cheneeheng/ceh-claude-code-library/main/docs/GETTING_STARTED.md
```

The link is this guide, not the repo, so Claude reads it instead of cloning anything. Claude asks
what you are about to do, then installs the core and only the plugins that moment needs. Run
`/reload-plugins` when it finishes: the new skills do not load until you do. Steps 1 to 5 are the
same route by hand, and the route Claude follows.

> **For Claude Code, running this setup:** this file is all you need, so do not clone the
> repository. Before you install anything, ask the user in one round what they are about to do.
> Install every plugin at `local` scope, unless the user names another scope. With no user to ask,
> say which moment you assumed. Always install `ceh-every-session` in step 2, whatever the
> answer. Then follow steps 1 to 4 for that moment only, running each install yourself with the
> `claude plugin` CLI, not the `/plugin` slash command. Do not install every plugin. When you
> finish, tell the user to run `/reload-plugins`.

## Set up with the script

The setup script does the same route from a terminal, and also what a plugin cannot do for
itself: it installs the tools the plugins need (`python3`, `uv`, `git`, the GitHub CLI, Bun),
raises the skill listing budget, and offers the statusline the usage-limit guard reads. It asks
before each change. Run it in the folder you are about to work in, from PowerShell or Windows
Terminal on Windows:

```
uv run https://raw.githubusercontent.com/cheneeheng/ceh-claude-code-library/main/tools/setup/setup.py
```

Without `uv`, install it first. On Windows:

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

On Linux and macOS:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

The script installs plugins at `local` scope, as this guide does, unless you pass `--scope project` or
`--scope user`. `--check` reports what it would do and changes nothing. Windows is tested, and
Linux and macOS are untested. The options and every step are in
[`tools/setup/README.md`](../tools/setup/README.md).

## Install at local scope

Install every plugin at `local` scope, unless you decide otherwise or a step below says so. The
scope decides where a plugin is on:

| Scope     | The plugin is on                           | Recorded in                                      |
| --------- | ------------------------------------------ | ------------------------------------------------ |
| `user`    | in every folder you open Claude Code in    | `~/.claude/settings.json`                        |
| `project` | in this folder, for everyone who clones it | `.claude/settings.json`, committed with the repo |
| `local`   | in this folder, for you only               | `.claude/settings.local.json`, not committed     |

`local` keeps a plugin and its hooks to the folder you install it in, and off your teammates in a
shared repo, so nothing loads where you did not ask for it. The cost is installing in each folder
you work in, the core included. Pick another scope only for a reason like these:

- **`user`:** you work alone across many folders and want the same plugins in each.
- **`project`:** the whole team should get the same plugins from the repo.

To use another scope, swap the `--scope` value in any command below.

## 1. Add the marketplace

```
/plugin marketplace add cheneeheng/ceh-claude-code-library
```

Leave `--scope` off this command: it then adds the marketplace once for your user, in
`~/.claude/settings.json`, so every folder can install from it. The plugins themselves stay at
`local` scope. Run in a terminal, it ends with this line:

```
✔ Successfully added marketplace: ceh-claude-code-library (declared in user settings)
```

To undo it, run `claude plugin marketplace remove ceh-claude-code-library`, which also uninstalls
every plugin installed from it.

Every `/plugin ...` command typed in a Claude Code session also runs in a terminal as
`claude plugin ...`. They are the same command.

Interrupted partway? Run these two in the folder you work in to see where you are:

```
claude plugin marketplace list
claude plugin list
```

The first lists `ceh-claude-code-library` once the marketplace is added. The second lists each
plugin installed in this folder with `Scope: local`. Re-run any step that is missing. Re-running
a step that already ran is safe: the marketplace add answers
`Marketplace 'ceh-claude-code-library' already on disk`, and an install answers
`Plugin "<name>@ceh-claude-code-library" is already installed (scope: local)`.

Installing before this step fails with `Plugin "<name>" not found in marketplace`, which is the
message Claude Code gives for a marketplace it does not know. Run the command above, then repeat
the install.

## 2. Install the core in each folder you work in

At `local` scope the core is on only in the folder you install it in, so install it again in the
next folder. A hook is a script Claude Code runs at fixed points, such as before each file edit,
so a plugin with hooks acts on every session.

| Plugin               | Install when               | What you get                                                                                                                                                                                                                                                                    |
| -------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ceh-every-session`  | always, whatever you do    | the response style every other plugin is written for, session handoff, research notes, questionnaires, plan stress-tests, a usage-limit guard once a statusline export feeds it, and `/ceh-every-session:whats-next` when you forget which skill fits. Always on, through hooks |
| `ceh-git-workflow`   | you work in git repos      | branches, commits, pull requests from open to merge, changelog, code review, and a hook that blocks edits on `main`                                                                                                                                                             |
| `ceh-coding-conduct` | you write code with Claude | the coding contract, write-less-code, root-cause debugging. Always on, through hooks                                                                                                                                                                                            |

Install `ceh-every-session` first, every time. It is not a dependency of any other plugin, so
nothing installs it for you. Then install only the other rows whose "Install when" fits you. If
you neither write code nor use git, for example you only write business plans or posts,
`ceh-every-session` is the whole core.

What each core plugin changes in every session, so you can decide before you install:

- [`ceh-every-session`](../plugins/standalone/ceh-every-session/) forces its response style over
  any `outputStyle` you set, turns Claude's question dialogs into a decision block in the reply,
  and after every file edit checks a handoff or plan file when the edit wrote one.
- [`ceh-git-workflow`](../plugins/standalone/ceh-git-workflow/) denies file edits while the default
  branch is checked out.
- [`ceh-coding-conduct`](../plugins/standalone/ceh-coding-conduct/) loads its coding contract at the
  start of every session, and after every file edit checks the fix record when the edit wrote one.

Their hooks need `python3` on your `PATH` (`ceh-every-session`, `ceh-git-workflow`,
`ceh-coding-conduct`) and `bash` (`ceh-coding-conduct`). The fix record and handoff checks, and
the plan check in step 3, also need `uv`. These show whether each is there:

```
python3 --version
bash --version
uv --version
```

Without `python3` the guards do nothing instead of blocking you, and installing a plugin never
installs `python3` for you. Without `uv`, the commands in
[Set up with the script](#set-up-with-the-script) install it.

```
/plugin install ceh-every-session@ceh-claude-code-library --scope local
```

Run in a terminal, each install ends with
`✔ Successfully installed plugin: <name>@ceh-claude-code-library (scope: local)`. To undo one,
run `claude plugin uninstall <name>@ceh-claude-code-library --scope local`.

If you write code in git repos, add:

```
/plugin install ceh-git-workflow@ceh-claude-code-library --scope local
/plugin install ceh-coding-conduct@ceh-claude-code-library --scope local
```

`ceh-git-workflow` blocks file edits on the default branch, so in a brand-new repo create a
branch before the first skill writes anything:

```
git checkout -b <name>
```

It works even before the first commit. Without a branch, Claude's first edit is denied with
`On the default branch (main). Create a feature branch first ...`. To edit the default branch
anyway, set `CEH_BRANCH_GUARD` to `off`, as described in
[Environment variables](ENVIRONMENT_VARIABLES.md).

## 3. Add the plugin for what you are about to do

`--scope local` keeps a plugin to the folder that needs it, a git repo or any plain folder, so a
project that is only being planned does not load the build and launch plugins. It records the
plugin in that folder's `.claude/settings.local.json`, which is not committed.

Install each plugin below in a Claude Code session opened in that folder, putting its name in place
of `<plugin>`:

```
/plugin install <plugin>@ceh-claude-code-library --scope local
```

Each moment names the plugin, the command that starts it, and the file it writes. Every product
file goes in `.agents_workspace/product/`. A project that kept them in a root `product/` moves each
file to the same sub-path under `.agents_workspace/product/`, or names its location in `CLAUDE.md`.

**Shape**

- Test whether an idea is worth building: install `ceh-product-direction`, start with
  `/ceh-product-direction:develop-business-plan`. Writes
  `.agents_workspace/product/business/BUSINESS_PLAN.yaml`.
- Learn from a competitor's repo or product: install `ceh-competitor-analysis`, start with
  `/ceh-competitor-analysis:analyze-competitor`. Writes reports in `.agents_workspace/`.
- Write down the repo's direction: the same plugin, start with
  `/ceh-product-direction:write-vision-and-strategy`. Writes
  `.agents_workspace/product/VISION.yaml` and `.agents_workspace/product/STRATEGY.yaml`.

**Build**

- Plan a new app or one feature: install `ceh-build-plan`, start with
  `/ceh-build-plan:write-build-plan`. Writes
  `.agents_workspace/product/plan/<YYYYMMDD-HHMMSS>-<slug>.yaml` and the `.md` generated from
  it, and deleting both discards the plan. It needs `uv` to check and render the plan, and saves
  it unchecked without.
- Build from that plan: the same plugin and your stack plugin (below), start with
  `/ceh-build-plan:implement-from-plan`. Writes the code and the plan's evidence.
- Write the user and operator docs: install `ceh-documentation`, start with
  `/ceh-documentation:write-project-docs`. Writes `docs/`.

**Prove**

- Check the code is what the plan said: install `ceh-check-build-against-plan`, start with
  `/ceh-check-build-against-plan:check-build-against-plan`. Reports in the session.
- Test it and roll up the evidence: `ceh-testing` (a stack plugin already brings it), start with
  `/ceh-testing:explore-app-for-bugs`, then `/ceh-testing:write-evidence-report`. Writes
  `.agents_workspace/product/EVIDENCE.yaml` and the `EVIDENCE.md` generated from it. It needs
  `uv` to check and render the report, and saves it unchecked without.
- Check a stranger can use it: install `ceh-usability-audit`, start with
  `/ceh-usability-audit:simulate-newcomer-first-run`. Writes a report in
  `.agents_workspace/product/`.
- Audit the whole codebase for security: install `ceh-security-audit`, start with
  `/ceh-security-audit:audit-codebase-security`. Writes a report.

**Tell**

- Write a launch post: install `ceh-blog-and-seo`, start with `/ceh-blog-and-seo:draft-post`.
  Writes a post.
- Make it findable: the same plugin, start with `/ceh-blog-and-seo:write-project-listing-text` for
  the README first screen and listings, or `/ceh-blog-and-seo:make-page-crawlable` for web pages.

Pick one stack plugin for the build, and install it when you build from a plan, not before: its
skills load in every session in that folder, so while you only plan they take listing space for
nothing. Each brings `ceh-testing`, and the web one also brings `ceh-ui-design`:

| You are building           | Install              |
| -------------------------- | -------------------- |
| a Python backend service   | `ceh-python-service` |
| a distributable Python lib | `ceh-python-library` |
| a web frontend             | `ceh-web-frontend`   |

For example, a new Python backend service starts with a plan and adds the build plugins once the
plan is written. In a Claude Code session opened in that repo, install the plan plugin now:

```
/plugin install ceh-build-plan@ceh-claude-code-library --scope local
```

After `/reload-plugins`, start the plan with `/ceh-build-plan:write-build-plan`. Then, when you
build from the plan:

```
/plugin install ceh-python-service@ceh-claude-code-library --scope local
```

Run `/reload-plugins` after each install, so the new skills load.

The Tell stage reads `.agents_workspace/product/business/BUSINESS_PLAN.yaml` and
`.agents_workspace/product/EVIDENCE.yaml` when they exist. Without them it still runs, and says
which claims rest on nothing proven.

## 4. Add these only when the moment arrives

| Plugin                     | Install when                                                                               |
| -------------------------- | ------------------------------------------------------------------------------------------ |
| `ceh-codebase-explanation` | you inherit a repo, or need an architecture doc, a glossary, or why code is the way it is  |
| `ceh-ui-design`            | you design a UI or HTML page without `ceh-web-frontend`                                    |
| `ceh-ag-ui`                | you build a generative-UI canvas for an AG-UI agent                                        |
| `ceh-workflow-builder`     | the same product work repeats and an agent should run it                                   |
| `ceh-workflow-runner`      | a built `flow.yaml` must run, here or headless                                             |
| `ceh-session-learning`     | a session went wrong and you want to know why, or one went well and you want it as a skill |

## 5. Check it worked

```
/reload-plugins
/help
```

Installed plugins do not load into a running session until `/reload-plugins` or a new session. Then
the `ceh-*:` skills you installed appear in the skills list. `claude plugin list` shows each
installed plugin with its version and scope. After an interruption, see
[Interrupted partway?](#1-add-the-marketplace) in step 1.

To drop a plugin you no longer need, `claude plugin uninstall <name>@ceh-claude-code-library`,
adding the `--scope` it was installed at, such as `--scope local`. Add `--prune` to also remove
the plugins it brought, such as the `ceh-testing` a stack plugin installs, when nothing else
needs them. Removing the marketplace removes every plugin installed from it. Prerequisites
(Python for hooks, `uv`, Bun, the GitHub CLI) are in the root
[`README.md`](../README.md#prerequisites).

## If a skill stops triggering, raise the listing budget

Claude Code lists every skill's name and description so it can match your request to a skill.
The listing has a budget of 1% of the model's context window. When it exceeds that budget,
Claude Code keeps every name and drops descriptions, starting with the skills invoked least.
Without a description, a skill loses the keywords Claude needs to match your request.

Run `/doctor` to estimate the listing's context cost. `/skill-doctor` (Claude Code v2.1.252 or
later) shows what each skill costs and how often it is used.

The [setup script](#set-up-with-the-script) raises the budget to 2% for you. To do it by hand,
merge this setting into `~/.claude/settings.json`:

```json
{
  "skillListingBudgetFraction": 0.02
}
```

Another way to free budget is to set a rarely used skill to `"name-only"` in `skillOverrides`.
See [Skill descriptions are cut short](https://code.claude.com/docs/en/skills#skill-descriptions-are-cut-short).
