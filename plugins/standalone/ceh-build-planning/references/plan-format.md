# Plan format

A build plan is one Markdown file. `ceh-build-planning` writes it, `ceh-build-from-plan` builds
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

A new plan is a copy of `plan.template.md`, next to this file: its frontmatter, then its sections
in that order. The `schema: plan/v1` line stays as written, so a reader can tell which version of
the format a plan follows.

- `draft`: an Open question blocks building. `ready`: buildable as written. `building`: at least
  one phase is done. `built`: every phase is done, with evidence.

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
- A `built` plan is kept. Once any check of the build against it has run, each Design decision a
  later reader still needs is copied to the Key Decisions log in `product/ARCHITECTURE.md`, and the
  change gets a changelog entry when the repo keeps one. New work gets a new plan file.
