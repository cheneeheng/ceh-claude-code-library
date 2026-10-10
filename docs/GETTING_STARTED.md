# Getting started

Which plugins to install the first time, and which to leave out until you need them. Do not install
all of them: every installed plugin adds its skill descriptions to every session, and the ones
with hooks run on every session too. Install a small core once, then add one plugin when you reach
the moment it serves.

The route below follows the product lifecycle in [`STRATEGY.md`](STRATEGY.md): Shape, Build, Prove,
Tell. You can start at any stage. Each plugin works installed alone, and with several installed they
chain through the committed files each one writes.

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
> repository. Ask the user what they are about to do before you install anything. Always install
> `ceh-every-session` in step 2, whatever the answer. Then follow steps 1 to 4 for that moment only, running each install yourself with the `claude plugin` CLI,
> not the `/plugin` slash command. Do not install every plugin. When you finish, tell the user to
> run `/reload-plugins`.

## 1. Add the marketplace

```
/plugin marketplace add cheneeheng/ceh-claude-code-library
```

`claude plugin marketplace list` confirms it was added. To undo it, run
`claude plugin marketplace remove ceh-claude-code-library`, which also uninstalls every plugin
installed from it.

Every `/plugin ...` command typed in a Claude Code session also runs in a terminal as
`claude plugin ...`. They are the same command.

Interrupted partway? `claude plugin list` shows what is already installed, and running an install
again is safe.

## 2. Install the core once, at user scope

User scope installs a plugin for you in every folder you open Claude Code in. A hook is a script Claude Code
runs at fixed points, such as before each file edit, so a plugin with hooks acts on every session.

| Plugin               | Install when               | What you get                                                                                                                                                                                                                                  |
| -------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ceh-every-session`  | always, whatever you do    | the response style every other plugin is written for, session handoff, research notes, questionnaires, plan stress-tests, a usage-limit guard, and `/ceh-every-session:whats-next` when you forget which skill fits. Always on, through hooks |
| `ceh-git-workflow`   | you work in git repos      | branches, commits, pull requests from open to merge, changelog, code review, and a hook that blocks edits on `main`                                                                                                                           |
| `ceh-coding-conduct` | you write code with Claude | the coding contract, write-less-code, root-cause debugging, design before code. Always on, through hooks                                                                                                                                      |

Install `ceh-every-session` first, every time. It is not a dependency of any other plugin, so
nothing installs it for you. Then install only the other rows whose "Install when" fits you. If
you neither write code nor use git, for example you only write business plans or posts,
`ceh-every-session` is the whole core.

```
/plugin install ceh-every-session@ceh-claude-code-library --scope user
```

If you write code in git repos, add:

```
/plugin install ceh-git-workflow@ceh-claude-code-library --scope user
/plugin install ceh-coding-conduct@ceh-claude-code-library --scope user
```

## 3. Add the plugin for what you are about to do, at project scope

`--scope project` keeps a plugin to the folder that needs it, a git repo or any plain folder, so a
project that is only being planned does not load the build and launch plugins. It records the
plugin in that folder's `.claude/settings.json`. In a git repo, commit that file and everyone who
clones the repo gets the same plugins.

If you installed `ceh-git-workflow` and the repo is brand new, create a branch before the first
skill writes anything: that plugin blocks file edits on the default branch.
`git checkout -b <name>` works even before the first commit.

Install each plugin below in a Claude Code session opened in that folder, putting its name in place
of `<plugin>`:

```
/plugin install <plugin>@ceh-claude-code-library --scope project
```

Each moment names the plugin, the command that starts it, and the file it writes.

**Shape**

- Test whether an idea is worth building: install `ceh-business-plan`, start with
  `/ceh-business-plan:develop-business-plan`. Writes `BUSINESS_PLAN.md`.
- Learn from a competitor's repo or product: install `ceh-competitor-analysis`, start with
  `/ceh-competitor-analysis:analyze-competitor`. Writes reports in `.agents_workspace/`.

**Build**

- Plan a new app or one feature: install `ceh-build-planning`, start with
  `/ceh-build-planning:write-build-plan`. Writes `docs/plans/<slug>.md`.
- Build from that plan: install `ceh-build-from-plan` and your stack plugin (below), start with
  `/ceh-build-from-plan:implement-from-plan`. Writes the code and the plan's evidence.
- Write the user and operator docs: install `ceh-documentation`, start with
  `/ceh-documentation:write-project-docs`. Writes `docs/`.

**Prove**

- Check the code is what the plan said: install `ceh-check-build-against-plan`, start with
  `/ceh-check-build-against-plan:check-build-against-plan`. Reports in the session.
- Test it and roll up the evidence: `ceh-testing` (a stack plugin already brings it), start with
  `/ceh-testing:explore-app-for-bugs`, then `/ceh-testing:write-evidence-report`. Writes
  `docs/EVIDENCE.md`.
- Check a stranger can use it: install `ceh-usability-audit`, start with
  `/ceh-usability-audit:simulate-newcomer-first-run`. Writes a report in `.agents_workspace/`.
- Audit the whole codebase for security: install `ceh-security-audit`, start with
  `/ceh-security-audit:audit-codebase-security`. Writes a report.

**Tell**

- Write a launch post: install `ceh-blog`, start with `/ceh-blog:draft-post`. Writes a post.
- Make it findable: install `ceh-seo`, start with `/ceh-seo:write-project-listing-text` for the
  README first screen and listings, or `/ceh-seo:make-page-crawlable` for web pages.

Pick one stack plugin for the build. Each brings `ceh-testing`, and the web one also brings
`ceh-ui-design`:

| You are building           | Install              |
| -------------------------- | -------------------- |
| a Python backend service   | `ceh-python-service` |
| a distributable Python lib | `ceh-python-library` |
| a web frontend             | `ceh-web-frontend`   |

For example, a new Python backend service starts with a plan and adds the build plugins once the
plan is written. In a Claude Code session opened in that repo, install the planning plugin now:

```
/plugin install ceh-build-planning@ceh-claude-code-library --scope project
```

Then, when you build from the plan:

```
/plugin install ceh-build-from-plan@ceh-claude-code-library --scope project
/plugin install ceh-python-service@ceh-claude-code-library --scope project
```

The Tell stage reads `BUSINESS_PLAN.md` and `docs/EVIDENCE.md` when they exist. Without them it
still runs, and says which claims rest on nothing proven.

## 4. Add these only when the moment arrives

| Plugin                     | Install when                                                                              |
| -------------------------- | ----------------------------------------------------------------------------------------- |
| `ceh-codebase-explanation` | you inherit a repo, or need an architecture doc, a glossary, or why code is the way it is |
| `ceh-ui-design`            | you design a UI or HTML page without `ceh-web-frontend`                                   |
| `ceh-ag-ui`                | you build a generative-UI canvas for an AG-UI agent                                       |
| `ceh-git-datastore`        | you want an app to run on a bare git repo instead of a database                           |
| `ceh-workflow-builder`     | the same product work repeats and an agent should run it                                  |
| `ceh-workflow-runner`      | a built `flow.yaml` must run, here or headless                                            |
| `ceh-session-to-skill`     | a task just went well and you want it as a reusable skill                                 |
| `ceh-session-diagnosis`    | a session went wrong and you want to know why from its transcript                         |
| `ceh-orchestration-lab`    | experimental: you want to compare orchestration strategies on real tasks                  |

## 5. Check it worked

```
/reload-plugins
/help
```

Installed plugins do not load into a running session until `/reload-plugins` or a new session. Then
the `ceh-*:` skills you installed appear in the skills list. `claude plugin list` shows each
installed plugin with its version and scope. Running an install again is safe: it reports that the
plugin is already installed, so after an interruption, check the list and carry on.

To drop a plugin you no longer need, `claude plugin uninstall <name>@ceh-claude-code-library`, adding
`--scope project` for one installed at project scope. Removing the marketplace removes every plugin
installed from it. Prerequisites (Python for hooks, `uv`, Bun, the GitHub CLI) are in the root
[`README.md`](../README.md#prerequisites).
