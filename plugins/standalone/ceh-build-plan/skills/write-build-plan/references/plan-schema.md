# Plan schema

A build plan is one Markdown file (`plan/v1`), or a YAML file with its Markdown generated beside
it (`plan/v2`, below). `ceh-build-plan` writes it, builds from it and records evidence in it, and
`ceh-check-build-against-plan` checks the build against it.
This file is copied word for word into every skill that reads a plan, so each skill folder works on
its own.

## Location

`.agents_workspace/product/plan/<YYYYMMDD-HHMMSS>-<slug>.yaml` in the target repo, unless the
repo's `CLAUDE.md` names another plan folder. A plan shapes the repo for whoever builds next, so it
lives with the project's other product artifacts. A workspace not yet migrated keeps its plans in
the older `.agents_workspace/product/plans/`: a skill that looks for a plan also looks there, and
saves a new plan only to `plan/`. `<slug>` is kebab-case from the goal: `mvp`, `checkout-flow`.
The time is the plan's creation, from one `date +%Y%m%d-%H%M%S` call, and never changes on later
edits. It carries no session id, because several sessions edit a plan in place. A plan saved
before 2026-11-17 is `<slug>.yaml` and keeps that name. Where this file writes `<slug>.yaml` or
`<slug>.md`, it means the plan's whole file stem.

A plan's slug is its file stem with any leading `YYYYMMDD-HHMMSS-` removed. A skill given a slug
matches names in the plan folder against `^(\d{8}-\d{6}-)?<slug>\.yaml$`, so the slug `layout`
never matches `workspace-layout`. With several matches it takes the newest by the time prefix, and
a name with no prefix counts as older than any prefixed one.

One plan covers one functionality: a change that lands in its own PR and can be checked on its
own. A request that covers several functionalities becomes one plan each, never phases of one
plan, and a plan that needs another built first names it in `depends_on`.
Plans are never deleted: a built plan stays where it is, with `status: built`, as the record of how
that change was planned, built, and proven, and every path that cites it stays valid. A skill that
looks for work in the folder reads only the frontmatter of a `built` plan, and its full text only
when the new work touches what it built, so finished plans stay cheap to keep.
`.agents_workspace/product/` holds the files the people and agents building the product read.
`docs/` is left to what users of the product read. A reference to a plan names its `.yaml`, and a
`plan/v1` plan with no YAML is its `<slug>.md`.

## Template

A new plan is a copy of `../assets/plan.template.md`, relative to this file: its frontmatter, then
its sections in that order. The `schema: plan/v1` line stays as written, so a reader can tell which
version of the format a plan follows.

**Frontmatter:**

- `title`: what this plan builds, one line.
- `status`: `draft` (an Open question blocks building), `ready` (buildable as written),
  `building` (at least one phase is done), or `built` (every phase is done, with evidence).
- `created`: the date the plan was first saved.
- `business_plan` (optional, legacy): accepted so plans written before 2026-11-11 still
  validate. No skill sets it, and no skill follows it.

**Sections:**

- **Goal:** one paragraph: what gets built, for whom, and the one user flow that matters most.
- **Scope:** **In** has one bullet per capability a user or caller can observe, and this list is
  what done means. **Out** has one bullet per thing deliberately not built, with a one-line reason.
- **Design:** only the decisions the phases need, each with its reason: stack, components (a
  Mermaid diagram when there are more than two), data model (entities and key fields), and
  interface (routes with method and path, CLI commands, or public functions), or, for documents,
  the outline and file layout. Each decision is written once here, and phases refer to it.
- **Phases:** one `### Phase <n>: <name>` per phase. **Builds** names what the phase adds by its
  Scope and Design items. **Check** is the command that proves it and what passing looks like, for
  example `uv run pytest tests/test_signup.py` passes, or, for documents,
  `grep -c 'appendix-b-' docs/README.md` is at least 1, or a named read-through of the outline.
  **Status** follows Phase rules below.
- **Open:** each unsettled question, with the assumption taken until it is answered. `None` when
  empty.
- **Record:** append-only, oldest first, one dated line per lifecycle event, per Record rules
  below.

## plan/v2: YAML with generated Markdown

A `plan/v2` plan is `.agents_workspace/product/plan/<YYYYMMDD-HHMMSS>-<slug>.yaml`, a copy of
`../assets/plan.template.yaml`, and its Markdown is generated from it and saved beside it. The YAML is the
source: agents read and edit it, and nobody edits the Markdown, which opens with
`generated_from: <slug>.yaml` and a `generated_note` saying not to edit it. The skill that edits the
YAML re-renders the Markdown. The body sits between `prettier-ignore-start` and
`prettier-ignore-end` comments, so a formatter leaves it as rendered. The Markdown keeps the
`plan/v1` layout above, so a reader of it sees no change. A `plan/v1` plan with no YAML beside it
is still edited in place.

The format in code is `plan-model.py` beside this file: its pydantic model checks every key, type
and rule below, and its renderer writes the Markdown. `scripts/artifact.py` in the skill, beside this
file's `references/`, runs both through uv, and the plugin's render hook runs its own copy:

```bash
uv run --script scripts/artifact.py check .agents_workspace/product/plan/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render .agents_workspace/product/plan/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version sits beside the script. Field paths count from 0, so
`phases.0` is Phase 1.

**Keys**, each one required unless marked optional, and no other key allowed:

- `schema`: `plan/v2`. `title`, `status`, `created`, `business_plan` (optional, legacy, see
  above): as the `plan/v1` frontmatter above. `created` is an unquoted date, `2026-11-06`.
- `depends_on` (optional): the plans this one needs built first, at least one when present, each
  the plan's repo-relative YAML path, such as `.agents_workspace/product/plan/<file>.yaml`. The
  model checks that each is relative and ends in `.yaml`, not its folder or that it exists. It
  renders as a `**Depends on:**` line above the Goal. With no dependency, leave the key out.
- `goal`: the Goal paragraph.
- `scope.in`: one item per capability, at least one. `scope.out`: `item` and `reason` per
  exclusion, `[]` when none.
- `design`: `topic` and `decision` per decision, at least one. The topic renders in bold and keeps
  its own punctuation. A decision that opens with a list, table or code block starts on the line
  below its topic.
- `phases`: `name`, `builds`, `check` and `status` (`todo`, `unplanned` or `done`) per phase, at
  least one, numbered by position. `evidence` is required exactly when `status` is `done`. `note`
  (optional, any status) holds what the Phase rules put in a Status beyond its value: a failed
  attempt, a check that could not run, a departure from Design.
- `open`: `question` and `assumption` per item, `[]` when none, which renders as `None`.
- `record`: `date`, `event` and `details` per entry, at least one. `event` is one of the Record
  rules' events below. `phase` is required exactly when `event` is `Built Phase`.

**Rules across keys:** `built` needs every phase `done`, `building` at least one, and `draft` or
`ready` none.

**Free text goes in `|` blocks**, as the template writes it, or in quotes. In a plain YAML value,
` #` starts a comment, so `details: PR #12` would keep only `PR`. `artifact.py` reports a plain
value followed by a comment as an error, never a silent loss. Every value is strict: `yes` is a
bool and `1.10` a number, so quote a value that must stay text.

## Phase rules

- Phases run in order. Each is buildable from the phases before it and leaves the deliverable
  usable: the app runs, or the documents read whole.
- Every phase has a runnable Check. A phase no command can prove is merged into the next one, or
  names its manual check and why no command can do it.
- **Status** is `todo`, `unplanned` (a one-line placeholder that must be planned before it is
  built), or `done` followed by its evidence: the commit, or the check's command, and one line of
  its passing output.

## Record rules

Each skill that acts on the plan appends its own line. A line is never edited or removed, and lines
are appended in any status, including after `built`.

| Event          | Appended by                | Line                                                                                    |
| -------------- | -------------------------- | --------------------------------------------------------------------------------------- |
| Planned        | `write-build-plan`         | `- YYYY-MM-DD Planned: status <ready or draft>`                                         |
| Reviewed       | `review-build-plan`        | `- YYYY-MM-DD Reviewed: <verdict>, <n> blocking (<the blocking findings, short>)`       |
| Built Phase    | `implement-from-plan`      | `- YYYY-MM-DD Built Phase <n>: <commit or check command>, <one line of passing output>` |
| Design changed | `implement-from-plan`      | `- YYYY-MM-DD Design changed: was "<old line>", now "<new line>", because <reason>`     |
| Checked        | `check-build-against-plan` | `- YYYY-MM-DD Checked: <count per status>, <each item not Built>`                       |
| Evidence       | `write-evidence-report`    | `- YYYY-MM-DD Evidence: EVIDENCE.yaml run <date> at <sha>, <areas not passed>`          |
| PR             | `pull-request`             | `- YYYY-MM-DD PR: #<n> <url>`                                                           |

- Phase **Status** holds the current state of a phase. Record holds the history, so a phase built
  twice shows both runs.
- A log that is edited cannot be trusted as a trail, and the fixed event word first makes each kind
  of line easy to find with grep.
- A line whose facts a skill cannot get (no git, no PR number) is left out, never guessed.

## Changing a plan

- A builder that departs from Design edits the Design line, gives the reason in that phase's
  Status, and appends a Design changed line to Record quoting the old line, so the plan stays true
  to the build and the original decision survives in the file.
- A `built` plan is kept. Once every phase is done, each Design decision a later reader still
  needs is copied to the Key Decisions log in `.agents_workspace/product/ARCHITECTURE.yaml`, after the check of the
  build against the plan when that check is installed, and the change gets a changelog entry when
  the repo keeps one. New work gets a new plan file.
