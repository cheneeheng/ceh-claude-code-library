# ceh-every-session

Help that holds however you use Claude Code: coding, writing, research, or ops. Nothing here
assumes a repository or code.

What it does for you:

- **Keeps a session's state.** Save where you are to a file, load it in a later session, and stop
  cleanly before the account usage limit cuts the session off.
- **Keeps large files out of the context.** A small, cheap agent reads them and returns only the
  answer.
- **Gets answers.** Research a question with cited sources, send questions to someone outside the
  session, or ask which skill fits what you want to do next.
- **Checks work.** Question a plan before anyone acts on it, review work that is not done yet, or
  audit work that is.
- **Keeps what you learn.** Turn a repeated mistake into a fix that stops it, and write a decision
  down as a rule every later session follows.
- **Shapes every reply.** A summary first, an honest status per topic, and a decision block when
  the choice is yours.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). Some parts need more installed:

| Needs                                  | For                                                                   | Without it                                              |
| -------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------- |
| `python3` on PATH                      | Every hook                                                            | The hooks need it, and a hook that fails blocks no work |
| [uv](https://docs.astral.sh/uv/)       | Checking saved files such as a handoff or a plan against their format | The file is read unchecked, and the agent says so       |
| A Claude Code build with mods          | Folded replies                                                        | Replies show as plain text                              |
| A statusline export of the rate limits | The usage-limit guard, see [Usage-limit guard](#usage-limit-guard)    | The guard stays silent                                  |

## Skills

| Skill                      | Say or type                                                                                                    | What it does                                                                                                                                                                                                                                                  |
| -------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `hand-off-session`         | "save where we are", "pick this up", `/hand-off-session save` or `/hand-off-session load [path]`               | Save writes the goal, what is done, what is open and the pending decisions to `.agents_workspace/handoff/`. Load finds the newest handoff, checks it against the repo, and resumes from its first open step.                                                  |
| `write-questionnaire`      | "make a questionnaire for the team", "read the answers back", `/write-questionnaire write` or `read [path]`    | Turns the session's open questions into one file someone outside the session can answer, each with its context and a recommended default. Later it reads the answers back and lists what is still open. It can post to a GitHub issue instead with `--issue`. |
| `write-research-note`      | "research how X handles Y", `/write-research-note <question>`                                                  | A background agent reads primary sources and writes one note to `.agents_workspace/research/` with every claim cited. The session then checks the citations the answer rests on.                                                                              |
| `whats-next`               | "what's next?", "which skill do I use", `/whats-next [what you want to do]`                                    | Reads the repo and the newest handoff, then suggests one to three installed skills or agents, each with the reason and how to start it. It runs none of them.                                                                                                 |
| `stress-test-plan`         | "grill me on this plan", "poke holes in this", `/stress-test-plan [plan-file]`                                 | Lists every open decision and untested assumption in a plan, looks up what the files can answer, and asks you the rest in rounds of at most four, each with a recommended answer.                                                                             |
| `review-anything`          | "review docs/pricing.md against the vision", `/review-anything [subject] [criteria]`                           | For work not yet marked done: a reader who has not seen the session checks it against the criteria, and the review is saved with a verdict of `Done`, `Not yet` or `Cannot judge`.                                                                            |
| `audit-anything`           | "audit docs/ against the vision", `/audit-anything [subject] [criteria]`                                       | For work already done or shipped: the same independent reader, with the findings saved worst first in a new file on every run.                                                                                                                                |
| `prevent-repeat-mistake`   | "you did X again", "make sure this never happens again", `/prevent-repeat-mistake [the mistake]`               | Names the mistake from quoted evidence, picks the strongest fix that would have caught it (a setting or a check before written guidance), proves it on the real mistake, and drafts the change for your approval.                                             |
| `record-project-decisions` | "we decided to use SvelteKit", "from now on we use Y", `/record-project-decisions [record <decision> \| seed]` | Writes each decision as its own rule file, `.claude/rules/decision-<topic>.md`, which Claude Code loads in every session. `seed` collects the decisions a new project still has open and asks them up front.                                                  |
| `find-available-guide`     | Loads by itself when the work first names a framework, library, or service                                     | Looks the name up in a list of installable skills, plugins and MCP servers, and adds one line with the install command below the reply. It installs nothing and says nothing on a miss.                                                                       |
| `usage-limit-handoff`      | Loads by itself when the usage-limit guard fires                                                               | Finishes the current step, starts nothing new, saves a handoff, and ends the turn.                                                                                                                                                                            |
| `delegate-bulk-reads`      | Loads by itself before the `bulk-reader` agent is used                                                         | Tells the session how to ask `bulk-reader` one clear question and how to check its answer before acting on it.                                                                                                                                                |

## Agents

| Agent                | What it does                                                                                                                                                                                                            |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bulk-reader`        | Reads large or many files and returns a short answer to one question, with line numbers. It runs on the small `haiku` model, which is the saving, and can miss facts, so the session checks its answer. It never edits. |
| `independent-reader` | Checks a piece of work against criteria as a reader who has not seen the session that wrote it. `review-anything` and `audit-anything` use it on every run. It never edits.                                             |

## Hooks

Four guards run by themselves while the plugin is enabled. A guard never blocks work because of its
own error. [Settings](#settings) tunes or turns them off.

| Guard                                                 | What it does for you                                                          | Default                                |
| ----------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------- |
| [Usage-limit guard](#usage-limit-guard)               | Stops the session cleanly, with a handoff, before the usage limit cuts it off | Acts once a statusline export feeds it |
| [Bulk-read guards](#bulk-read-guards)                 | Send whole-file reads of large files to `bulk-reader`                         | Off until you set a line threshold     |
| [Question guard](#question-guard)                     | Turns a question dialog into a decision block at the end of the reply         | On                                     |
| [Handoff render and guard](#handoff-render-and-guard) | Checks each saved handoff and keeps its readable Markdown copy in step        | On                                     |

### Usage-limit guard

After every tool call, the guard reads how much of the account usage limit is used, taking
whichever of the 5-hour and weekly windows is closest to its cap. At 90% it tells the agent to stop
starting new work and save a handoff. The reading covers the whole account: claude.ai on the web,
desktop and mobile, and Claude Code all draw from one pool.

Claude Code gives the rate limits only to the statusline, not to hooks, so the guard needs a
statusline that exports them.
[`statusline-hook`](https://github.com/cheneeheng/claude-code-command-center/tree/main/tools/statusline-hook)
does that by default from `slh-v0.3.0` on. Without the export the guard does nothing, and the rest
of the plugin works unchanged.

### Bulk-read guards

The two guards stop a whole-file read of a file at or above a line threshold, and point the agent
at `bulk-reader` instead. They do nothing until you set the threshold in `~/.claude/settings.json`:

```json
{ "env": { "BULK_READER_MIN_LINES": "350" } }
```

- `350` is a reasonable start. Below roughly 200, handing the read over costs more than it saves.
- A read of part of a file always passes.
- The guards make the handover happen, but nothing checks that the summary was right. That is why
  the session checks the cited lines before acting on them.
- They are a nudge, not a sandbox: other commands can still read a file.

### Question guard

The guard stops every question dialog and has the agent end its reply with a decision block
instead. A dialog holds the turn open, so a background task that finishes while it waits goes
unread until you answer. A decision block ends the turn, so the agent can act on that result.

### Handoff render and guard

`hand-off-session` saves a handoff as a YAML file with a Markdown copy beside it for reading. One
hook checks the YAML on every write and renders the Markdown, or reports the errors back to the
agent. The other stops a hand edit to that generated Markdown and names the YAML to edit instead.
The same pair covers the other files this plugin's skills save or check, such as reviews, audits
and plans.

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable                    | Default              | Effect                                                                                                                                                                                                     |
| --------------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CEH_DISABLED_HOOKS`        | unset (all hooks on) | Comma-separated hook names to skip: `usage-limit-watch`, `bulk-read-guard`, `bulk-read-bash-guard`, `ask-user-question-guard`, `artifact-render-hook`, `generated-md-guard`                                |
| `CEH_USAGE_LIMIT_THRESHOLD` | `90`                 | The usage percentage at which the usage-limit guard fires                                                                                                                                                  |
| `CEH_USAGE_STALE_MINUTES`   | `15`                 | A usage reading older than this is treated as unknown                                                                                                                                                      |
| `BULK_READER_MIN_LINES`     | unset (guards off)   | The line count from which a whole-file read is sent to `bulk-reader`. `999999` suspends the guards for a session                                                                                           |
| `BULK_READER_ALLOW`         | unset                | File patterns the bulk-read guards never stop, such as `*.lock:*/migrations/*`, separated by `;` on Windows                                                                                                |
| `CEH_ARTIFACT_CHECK`        | unset (check on)     | `off` turns the handoff render and guard off                                                                                                                                                               |
| `CEH_USER_RULES_DIR`        | `~/.claude/rules/`   | Where `record-project-decisions` writes a decision that binds all your projects. Set it to keep those rules in a git-tracked folder. The skill then adds one import line per rule to `~/.claude/CLAUDE.md` |

## How it works

### Reply format

While the plugin is enabled, every reply follows its output style, `CEH Every Session`. It replaces
any output style you set yourself.

- A reply with two or more topics opens with a numbered summary, each topic with an honest status
  such as done, verified or assumed.
- The work comes before the explanation.
- A question only you can answer closes the reply as a `**Decision: <question>**` block with
  numbered options, the recommended one first.
- The agent says "I don't know" plainly, and separates what it verified from what it assumed.

### Folded replies

On a Claude Code build with mods, the plugin also redraws these replies:

| What you see         | How it works                                                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Folded topics        | The summary shows in a box, and each topic below it as a folded box that a click opens.                            |
| Decision options     | Each decision block shows as a box of options. A press fills the prompt box, unsent, with the number of your pick. |
| `/details on \| off` | `on` opens every topic, `off` folds them again, and `/details` alone toggles. The setting lasts for the session.   |

Only the drawing changes. The reply itself stays whole, and ctrl+o shows the raw text.

## Not this plugin

- Reviewing a build plan: `ceh-build-plan:review-build-plan`. Reviewing a pull request:
  `ceh-git-workflow:write-code-review`.
- Audits with their own skill, such as security or usability: `ceh-security-audit` and
  `ceh-usability-audit`.

## Where its files live

The plugin saves and reads its files in `.agents_workspace/`, and product files such as reviews and
audits in `.agents_workspace/product/`. A project that keeps them in a root `product/` folder moves
each file to the same sub-path there, or names its own location in `CLAUDE.md`.
