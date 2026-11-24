# ceh-codebase-explanation

Leave a codebase understood. Reach for it when you inherit a repo, need a subsystem or a diff
explained until it makes sense, want an architecture document or a glossary, or ask why code is
the way it is. The understanding goes to a person in the session, or into a file that outlives it.
The skills work on code repos and on Markdown or text knowledge bases alike.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). No other plugin installs it as a
dependency. Some parts need more installed:

| Needs                                                 | For                                                                                 | Without it                                                    |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| `git`, and a clone with its full history              | `explain-codebase`, and `trace-code-rationale`, which reads the history             | A shallow clone cuts the rationale answer short               |
| The GitHub CLI (`gh`), signed in with `gh auth login` | The PR and review-comment lookup in `trace-code-rationale`                          | The answer comes from commits alone, and says so              |
| [uv](https://docs.astral.sh/uv/)                      | Checking and rendering the architecture file, the glossary, and the learning record | The file is saved unchecked, and its Markdown is not rendered |

## Skills

| Skill                      | Say or type                                                                                                                              | What it does                                                                                                                                                                                                                                                                                                                             |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `explain-until-understood` | "explain this to me", "I don't understand this diff", `/ceh-codebase-explanation:explain-until-understood [what to explain]`             | Explains a subsystem, design, diff or tool from zero, from the real code, with plain-text pictures and one ordinary case walked end to end, until you can answer unaided. When an explanation misses, it goes back a step to the foundation that was skipped. It closes with a rule you can reuse and a self-test.                       |
| `explain-codebase`         | "explain this codebase", "what does this repo do", "I inherited this repo", `/ceh-codebase-explanation:explain-codebase`                 | Writes a whole-repo orientation into a git-ignored file: what each component or topic area does, how they connect, and the key flows.                                                                                                                                                                                                    |
| `document-architecture`    | "write the architecture doc", "diagram the system", "record this decision", `/ceh-codebase-explanation:document-architecture`            | Keeps the living architecture document: a short overview, Mermaid diagrams of components, key flows, data model and state machines, and an append-only Key Decisions log. Update it when the system's shape changes, not on every commit.                                                                                                |
| `trace-code-rationale`     | "why is it like this", "why was this added", "is this safe to remove", `/ceh-codebase-explanation:trace-code-rationale <file>[:<lines>]` | Traces the code through `git log -L`, blame, pickaxe, and the linked PRs and issues. It answers in the session with every claim cited to a commit, PR or issue, keeps stated reasons apart from inferred ones, and lists what the history does not record. It changes no files.                                                          |
| `maintain-glossary`        | "what do we call X", "define our terms", "add this to the glossary", `/ceh-codebase-explanation:maintain-glossary [term ...]`            | Finds each term's real uses in code and prose, settles one word and one definition, and asks you when the choice changes meaning. It writes the entry to a committed glossary, converts an old Markdown-only glossary without losing an entry, and lists the files still using a rejected word as `path:line` without renaming anything. |

## Agents

This plugin has no agents.

## Hooks

Two hooks run by themselves while the plugin is enabled, both on by default.
[Settings](#settings) turns them off.

| Hook                     | What it does for you                                                                                                                                                                                                        |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| File check               | Checks the architecture file, the glossary, or a learning record each time it is written, and renders its Markdown beside it. Errors go back to the agent to fix, and the Markdown stays as it was until the file is valid. |
| Generated Markdown guard | Stops a hand edit to the generated Markdown, and names the YAML file to edit instead.                                                                                                                                       |

Both need uv. Without it, the agent is told once per session that the file went unchecked. A
`GLOSSARY.yaml` that names no format is checked only at the session's root, or in `docs/` beside a
`GLOSSARY.md`, so a project's unrelated `GLOSSARY.yaml` is left alone.

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable             | Default              | Effect                                                                           |
| -------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK` | unset (check on)     | `off` turns the file check and the generated Markdown guard off                  |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook names to skip: `artifact-render-hook`, `generated-md-guard` |

## How it works

### Planned and built diagrams

`document-architecture` draws what is built. A diagram marked as planned comes from
`ceh-build-plan:write-technical-design`, which settles a design before the build.
`document-architecture` removes the mark when it redraws that diagram from the code.

### Learning over several sessions

Ask `explain-until-understood` to keep track of what you know ("teach me this over the week"), and
it keeps a learning record per subject: the terms you have said back, the rules, your self-test
history and what comes next. A later session opens with two self-test questions. Without that
request it writes no files.

## Not this plugin

- How an agent behaves while it codes: `ceh-coding-conduct`.
- Settling a design before anything is built: `ceh-build-plan:write-technical-design`.

## Where its files live

| File                                                | Written by                 |
| --------------------------------------------------- | -------------------------- |
| `.agents_workspace/CODEBASE_EXPLAINED.md`           | `explain-codebase`         |
| `.agents_workspace/product/ARCHITECTURE.yaml`       | `document-architecture`    |
| `.agents_workspace/product/learning/<subject>.yaml` | `explain-until-understood` |
| `GLOSSARY.yaml` at the repo root, or under `docs/`  | `maintain-glossary`        |

Each YAML file has its Markdown rendered beside it. The glossary is committed with the repo.
`document-architecture` moves an old `.agents_workspace/ARCHITECTURE.md` to its new place on the
first run. `explain-until-understood` may also write one
developer-facing explainer of a single subsystem into `docs/`, when you still want one after it
names the gap. A project that keeps product files in a root `product/` folder moves each file to
the same sub-path there, or names its own location in `CLAUDE.md`.
