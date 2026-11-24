# ceh-every-session design notes

Maintainer detail moved out of the plugin README on 2026-11-24, when the README was rewritten for
the person installing the plugin. The site does not publish this file.

## Skill checks

What each skill's run looks like when it works, from the README's old Skills table:

- `write-questionnaire`: each question reads sensibly to someone who never saw the session, and a
  blank answer is reported as open, not filled with the default.
- `write-research-note`: every sentence in the note carries a `[n]` or an "Inference:" label, and
  the note has a Checked line and a Not found section.
- `stress-test-plan`: no question asks for a fact the files could answer, and each round asks only
  questions whose prerequisites are settled.
- `review-anything`: the reply lists the subject and criteria before the reader runs, and ends with
  a verdict of `Done`, `Not yet` or `Cannot judge` and the file path.
- `audit-anything`: the reply lists the subject, its boundary and the criteria before the reader
  runs, and ends with findings worst first and a file name holding the session id.
- `prevent-repeat-mistake`: the report quotes the mistake and says why each higher rung did not fit.
- `whats-next`: the answer is a table of suggestions whose reasons cite files it read, and nothing
  ran.
- `find-available-guide`: a hit shows a note under `---` with an install command copied word for
  word from the registry, and a name with no entry shows nothing.
- `record-project-decisions`: each decision lands in its own file with a `Why:` line, and an
  inferred one names the file it came from.

The formats each skill saves (`general-review/v1`, `general-audit/v1`, `repeat-mistake/v2`,
`stress-test/v2`, `handoff/v2`), `hand-off-session --file` and its caller fields are described in
each skill's `SKILL.md` and `references/`.

## Checked reads

`whats-next` and `record-project-decisions` check a plan or `ARCHITECTURE.yaml` against its model
before reading it, `whats-next` a `PRD.yaml` too, whose first unplanned feature it suggests
planning, and `record-project-decisions` a `GLOSSARY.yaml`, which needs
[uv](https://docs.astral.sh/uv/), installing pydantic and PyYAML on first use. Without uv the file
is read unchecked, and a repo with none of these files needs no uv.

## User rules folder

`record-project-decisions` writes a decision that binds all of the user's projects to the folder
`CEH_USER_RULES_DIR` names (optional, default `~/.claude/rules/`), for a user who keeps those rules
in a git-tracked folder. Claude Code loads only the default folder by itself, so for any other
folder the skill adds one `@<folder>/decision-<topic>.md` import line per rule to
`~/.claude/CLAUDE.md`.

Why a variable and an import:

- **A tracked home.** `~/.claude/rules/` sits in no repository, so a rule written there has no
  history and does not reach another machine. The variable lets those rules live in a repo.
- **The default stays.** A user who does not set the variable sees no change.
- **The import is the only way in.** The Claude Code memory docs, read 2026-11-13, name no setting
  that loads user rules from another folder, and an `@path` line in `~/.claude/CLAUDE.md` is the
  documented way to load a file from elsewhere.
- **Not built: a symlink.** Making `~/.claude/rules/` a symlink into a tracked repo would need no
  import, since rules folders support symlinks. It was left out because creating a symlink on
  Windows needs Developer Mode or administrator rights.
- **Not checked:** whether a `paths` field in an imported rule still narrows when it loads.

## Agents

`bulk-reader` runs on `haiku` with `Read`/`Grep`/`Glob` only — the model line is the entire cost
saving, and the recall ceiling. Measured over 30 dispatches (the eval suite in
[agent-skills](https://github.com/cheneeheng/agent-skills/tree/main/plugins/ceh-coding-conduct/skills/delegate-bulk-reads/tests),
not migrated): 100% recall on enumerative questions, 69% when the answer has to be assembled, which
is why `delegate-bulk-reads` makes the caller confirm coverage.

`independent-reader` runs on the session's model (`inherit`), because the judgement is the job,
with `Read`/`Grep`/`Glob` only.

## Output style

`CEH Every Session` (`output-styles/ceh-every-session.md`) sets `force-for-plugin: true` and
`keep-coding-instructions: true`, so Claude Code's built-in engineering instructions stay in place
for coding sessions.

`force-for-plugin` overrides any `outputStyle` the user set, and if several enabled plugins force a
style, Claude Code uses the first one loaded. Output styles reach the main conversation and forks
only. Other subagents run their own system prompt, so rules that must hold there stay in
`CLAUDE.md` or a skill.

The style's last section, Available guides, is what starts `find-available-guide`. It tells the
agent to invoke the skill once when the work first names a framework, library, or service, and to
say nothing about the lookup when the registry lists nothing.

## Registry

`skills/find-available-guide/references/registry.txt` lists pointers to skills, plugins, and MCP
servers worth installing, one line per install method:
`name | aliases | kind | beats | method | install | source | checked`. `kind` is what the entry is
(`skill`, `plugin`, `mcp`) and `method` is how it installs (`plugin`, `mcp-add`, `skill-copy`).
An entry with several ways to install has several lines, the preferred one first. Each column is
described in `skills/find-available-guide/references/registry.schema.md`, which sits beside the
registry because the registry itself takes no header or comment lines.

To add an entry, read the install command at its source, write the line with today's date as
`checked`, and run `python tools/validate-plugins/validate.py`, which checks every cell. Entries
are our own pointers, never text copied from a third party, and cover only help for building,
proving, or telling people about a product. The skill shows the install command and never runs it.

## Mod

`hooks/fold-replies.tsx` is a Claude Code mod, a hooks module `hooks/hooks.json` names under
`modules`, that redraws replies written in the output style's shape. It changes the drawing only:
the stored reply and what the model reads stay whole, and ctrl+o shows the raw text. A `code`
span in a Topic, a question, or an option draws as inline code, as it does in a reply.

- **Folded topics.** Shows the list in a box titled Summary, then each bold Topic as a bordered box
  with a `▸ <#> <Topic>` title that a click unfolds, its bullets indented under it. A quick second
  click or a slip of the hand on a title selects its text instead of toggling, which Claude Code
  gives a mod no way to stop without shifting every click in VS Code. The `---` right after the
  list is dropped from the drawing, since the box border separates it, and stays in the reply for
  surfaces without the mod. Text below a later `---` that belongs to no Topic shows open in a box
  titled Notes. A reply with no summary list draws as Claude Code draws it.
- **Decision options.** A press marks the option and fills the prompt box, unsent, with every pick
  of that reply as numbers only: the option number, or one `<decision>: <option>` line each when
  the reply has several blocks.
- **`/details`.** `on` keeps the boxes and opens every Topic, and a press folds one. `off` folds
  again. The prompt footer shows the mode `folded replies (mod)` while folding is on.

The mod's tests run with `claude plugin test plugins/standalone/ceh-every-session`, which
`validate.py` does not run.

## Hooks

| Guard                    | Event                                         | Script(s)                                          |
| ------------------------ | --------------------------------------------- | -------------------------------------------------- |
| Usage-limit guard        | `PostToolUse` (every tool)                    | `usage-limit-watch.py`                             |
| Bulk-read guards         | `PreToolUse` (`Read`, `Bash`)                 | `bulk-read-guard.py`, `bulk-read-bash-guard.py`    |
| Question guard           | `PreToolUse` (`AskUserQuestion`)              | `ask-user-question-guard.py`                       |
| Handoff render and guard | `PostToolUse`, `PreToolUse` (`Edit`, `Write`) | `artifact-render-hook.py`, `generated-md-guard.py` |

Each hook script is stdlib-only Python, needs `python3` on PATH, and fails open: a hook that blocked
work on its own bugs would cost more than it saves. The handoff render hook runs `artifact.py`
through `uv` for the check itself.

### Handoff render and guard

A `PostToolUse` hook (`scripts/artifact-render-hook.py`) checks a written handoff YAML against its
model through `uv` and renders the Markdown, or reports each error back to the agent and leaves the
Markdown as it was. A `PreToolUse` guard (`scripts/generated-md-guard.py`) denies a direct edit to a
generated Markdown file and names its YAML. Both run on every Edit or Write in every session and
return at once for any other file, about 85 ms per edit for the two together, measured once on
Windows. Because `whats-next` and `record-project-decisions` carry the plan and architecture
models, and `record-project-decisions` the glossary model, the hook also checks and renders those
files when they are written, as their own plugins already do. `prevent-repeat-mistake` saves its
report as `repeat-mistake/v2`, which the same hook checks and renders, and a dated report missing
its schema key in either retro folder is reported, not skipped. `stress-test-plan` saves its
outcome as `stress-test/v2` when there is no plan file to write back to, which the hook checks and
renders too. `review-anything` saves its review as `general-review/v1`, and `audit-anything` its
audit as `general-audit/v1`, which the hook checks and renders as well. Without `uv` the agent is
told once per session that the file went unchecked.

### Usage-limit guard

When the usage crosses `CEH_USAGE_LIMIT_THRESHOLD`, the hook tells the agent to stop starting new
work and run `usage-limit-handoff`; if ignored, it re-fires every 5 further points of usage.

The reading refreshes on every API round-trip, so sampling per tool call is fresh enough to stop
preemptively rather than after a 429. The hook reads the newest record across _all_ sessions and
projects, so a second Claude Code window does not leave a session acting on a stale number. Inside
a subagent it tells the subagent to stop and report upward instead of writing an artifact, since a
subagent sees only its own slice of the work.

The hook reads the rate-limit data that a statusline export writes to
`~/.claude/statusline/latest/rate-limits.jsonl`, one line `{"session_id", "ts", "data": <payload>}`
that each turn overwrites. `C4_STATUSLINE_DISABLE_EXPORT=1` turns the export off. The hook also
reads an older export's per-session files, `~/.claude/statusline/<project-dir>/<session_id>.jsonl`.
Without the export the guard does nothing and says nothing, unless `CEH_USAGE_LIMIT_THRESHOLD` or
`CEH_USAGE_STALE_MINUTES` is set or the export folder exists, in which case it warns once per
session that it is inactive. Readings older than `CEH_USAGE_STALE_MINUTES` (default 15) are
treated as unknown: a stale low number reads as safety that is not there. A window whose
`resets_at` has already passed is skipped regardless of the record's age — the reading predates
the reset, so a high number there describes a window that no longer exists.

The hook needs `python3` on PATH (stdlib only, no packages), which is what makes it behave the
same on Linux, macOS, and Windows; it replaced a bash+`jq` version that needed a POSIX shell and
a `jq` binary Windows does not ship. It is advisory, so it fails open: on error it prints one
line to stderr and exits 1 (visible warning, nothing blocked).

### Bulk-read guards

Unlike every other hook here they are **inert unless `BULK_READER_MIN_LINES` is set**: this plugin
loads in most sessions, and denying reads by default is not a decision to make on a user's behalf.
The `bulk-reader` agent itself is let through, since the guard sends work to it.
`BULK_READER_ALLOW` patterns come on top of the built-in exclusions for lockfiles, minified assets,
images and archives, separated by the OS path separator so a pattern with a drive letter stays
whole on Windows.

Targeted reads always pass: `Read` with `offset`/`limit`, piped or redirected bash
(`cat f | grep x`), and `head`/`tail` that genuinely print a small window. The bash guard resolves
that window against the real file rather than reading the bare integer, so `tail -n +1` (an offset
— it prints the whole file) is blocked while `tail -n +400` on a 500-line file is not, and `-c`
is measured in bytes. Several files in one command are summed: `cat a b c` costs their total.
Each guard sends its full deny text for its first three denials in a session, then one line with
the denial's number, because repeating an identical block pushes the model into loops.
Both guards need `python3` on PATH (stdlib only) and fail open — unparseable input, a binary file,
a missing path, or a crashed interpreter allows the read through, because a guard that blocked work
on its own bugs would cost more than it saves.

The guards are a nudge with teeth rather than a sandbox — `sed -n`, `awk`, `python -c open(...)`
and an editor all still read files, and the bash guard covers only the common dumps. And a
delegation is a full subagent turn, so on small files it is strictly worse than reading directly;
that is what the threshold exists to prevent.

### Question guard

When no user is present, the guard's reason sends the question where the caller says instead.
Skills in other plugins that name `AskUserQuestion` keep working, because the denial redirects
them.

## Prior art

The read-delegation design here follows
[Portal by Spotify cut my Claude Code token usage by 90%](https://engineering.atspotify.com/2026/9/portal-by-spotify-cut-my-claude-code-token-usage-by-90)
(Dimitri Mazmanov, September 2026), which pairs a `bulk-reader` worker on a cheaper model with a
hook that intercepts reads over 350 lines. This plugin keeps the shape and the threshold but not
the infrastructure: the worker is a plain Claude Code subagent rather than a hosted runtime, and
the guards are stdlib Python hooks with no service behind them. The 90% figure is theirs and is not
reproduced here — the eval suite left behind in
[agent-skills](https://github.com/cheneeheng/agent-skills/tree/main/plugins/ceh-coding-conduct/skills/delegate-bulk-reads/tests)
measures this implementation against its own corpus and finds roughly 78% saved on enumerative
questions, where recall is perfect, and 62% on reasoning ones, where about three facts in ten go
missing.

## History

Since 2026-11-14 this plugin saves and reads product files in `.agents_workspace/product/`.
