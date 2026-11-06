# Plan schema

A build plan is one Markdown file (`plan/v1`), or a YAML file with its Markdown generated beside
it (`plan/v2`, below). `ceh-build-planning` writes it, `ceh-build-from-plan` builds
from it and records evidence in it, and `ceh-check-build-against-plan` checks the code against it.
This file is copied word for word into all three plugins, so each works installed alone.

## Location

`product/plans/<slug>.md` in the target repo, committed, unless the repo's `CLAUDE.md` names another
plans folder. A plan shapes the repo for whoever builds next, so it lives where a fresh clone and a
reviewer can read it. `<slug>` is kebab-case from the goal: `mvp`, `checkout-flow`. Plans are never
deleted: a built plan stays where it is, with `status: built`, as the record of how that change was
planned, built, and proven, and every path that cites it stays valid. A skill that looks for work in
the folder reads only the frontmatter of a `built` plan, and its full text only when the new work
touches what it built, so finished plans stay cheap to keep. `product/` holds the files the people
and agents building the product read. `docs/` is left to what users of the product read.

## Template

A new plan is a copy of `../assets/plan.template.md`, relative to this file: its frontmatter, then
its sections in that order. The `schema: plan/v1` line stays as written, so a reader can tell which
version of the format a plan follows.

**Frontmatter:**

- `title`: what this plan builds, one line.
- `status`: `draft` (an Open question blocks building), `ready` (buildable as written),
  `building` (at least one phase is done), or `built` (every phase is done, with evidence).
- `created`: the date the plan was first saved.
- `business_plan`: the path to `.agents_workspace/product/business/BUSINESS_PLAN.md`. Omit the key when there is none.

**Sections:**

- **Goal:** one paragraph: what gets built, for whom, and the one user flow that matters most.
  With `business_plan` set, one sentence plus a pointer to its product section instead.
- **Scope:** **In** has one bullet per capability a user or caller can observe, and this list is
  what done means. **Out** has one bullet per thing deliberately not built, with a one-line reason.
- **Design:** only the decisions the phases need, each with its reason: stack, components (a
  Mermaid diagram when there are more than two), data model (entities and key fields), and
  interface (routes with method and path, CLI commands, or public functions). Each decision is
  written once here, and phases refer to it.
- **Phases:** one `### Phase <n>: <name>` per phase. **Builds** names what the phase adds by its
  Scope and Design items. **Check** is the command that proves it and what passing looks like, for
  example `uv run pytest tests/test_signup.py` passes. **Status** follows Phase rules below.
- **Open:** each unsettled question, with the assumption taken until it is answered. `None` when
  empty.
- **Record:** append-only, oldest first, one dated line per lifecycle event, per Record rules
  below.

## plan/v2: YAML with generated Markdown

A `plan/v2` plan is `product/plans/<slug>.yaml`, a copy of `../assets/plan.template.yaml`, and its
Markdown, `product/plans/<slug>.md`, is generated from it and committed beside it. The YAML is the
source: agents read and edit it, and nobody edits the Markdown, which opens with
`generated_from: <slug>.yaml`. The Markdown keeps the `plan/v1` layout above, so a reader of it sees
no change. A `plan/v1` plan with no YAML beside it is still edited in place.

The format in code is `plan-model.py` beside this file: its pydantic model checks every key, type
and rule below, and its renderer writes the Markdown. `scripts/artifact.py` in the plugin runs both,
through uv:

```bash
uv run --script scripts/artifact.py check product/plans/<slug>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render product/plans/<slug>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means this plugin has no model for that version. Field paths count from 0, so
`phases.0` is Phase 1.

**Keys**, each one required unless marked optional, and no other key allowed:

- `schema`: `plan/v2`. `title`, `status`, `created`, `business_plan` (optional): as the `plan/v1`
  frontmatter above. `created` is an unquoted date, `2026-11-06`.
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

- Phases run in order. Each is buildable from the phases before it and leaves the app runnable.
- Every phase has a runnable Check. A phase no command can prove is merged into the next one, or
  names its manual check and why no command can do it.
- **Status** is `todo`, `unplanned` (a one-line placeholder that must be planned before it is
  built), or `done` followed by its evidence: the commit, or the check's command, and one line of
  its passing output.

## Record rules

Each skill that acts on the plan appends its own line. A line is never edited or removed, and lines
are appended in any status, including after `built`.

| Event          | Appended by                | Line                                                                                     |
| -------------- | -------------------------- | ---------------------------------------------------------------------------------------- |
| Planned        | `write-build-plan`         | `- YYYY-MM-DD Planned: status <ready or draft>`                                          |
| Reviewed       | `review-build-plan`        | `- YYYY-MM-DD Reviewed: <verdict>, <n> blocking (<the blocking findings, short>)`        |
| Built Phase    | `implement-from-plan`      | `- YYYY-MM-DD Built Phase <n>: <commit or check command>, <one line of passing output>`  |
| Design changed | `implement-from-plan`      | `- YYYY-MM-DD Design changed: was "<old line>", now "<new line>", because <reason>`      |
| Checked        | `check-build-against-plan` | `- YYYY-MM-DD Checked: <count per status>, <each item not Built>`                        |
| Evidence       | `write-evidence-report`    | `- YYYY-MM-DD Evidence: product/EVIDENCE.md section <date> at <sha>, <areas not passed>` |
| PR             | `pull-request`             | `- YYYY-MM-DD PR: #<n> <url>`                                                            |

- Phase **Status** holds the current state of a phase. Record holds the history, so a phase built
  twice shows both runs.
- A log that is edited cannot be trusted as a trail, and the fixed event word first makes each kind
  of line easy to find with grep.
- A line whose facts a skill cannot get (no git, no PR number) is left out, never guessed.

## Changing a plan

- A builder that departs from Design edits the Design line, gives the reason in that phase's
  Status, and appends a Design changed line to Record quoting the old line, so the plan stays true
  to the code and the original decision survives in the file.
- A `built` plan is kept. Once every phase is done, each Design decision a later reader still
  needs is copied to the Key Decisions log in `product/ARCHITECTURE.md`, after the check of the
  build against the plan when that check is installed, and the change gets a changelog entry when
  the repo keeps one. New work gets a new plan file.
