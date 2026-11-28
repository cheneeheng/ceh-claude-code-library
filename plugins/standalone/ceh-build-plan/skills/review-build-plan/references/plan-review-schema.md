# Plan review schema

The review `review-build-plan` saves to
`.agents_workspace/product/review/plan/<YYYYMMDD-HHMMSS>-<plan-slug>.yaml`, with its `.md`
rendered beside it, one file per plan, edited in place by every later review of that plan. A
reference to it names the `.yaml`. Its layout is `../assets/plan-review.template.md`, relative to
this file. `<plan-slug>` is the plan's slug: its file stem with any leading `YYYYMMDD-HHMMSS-`
removed. A new review is written as `plan-review/v3` YAML, per the section at the end. An older
`plan-review/v2` file is converted in place when a new round finds it, per the Review lifecycle,
and a `plan-review/v1` review, a `.md` with no YAML beside it, stays as written.

## Review lifecycle

Every saved review follows these rules, whatever its kind. The section is copied word for word
into each review format's schema, and only the Targets line differs.

- **Name:** `.agents_workspace/product/review/<kind>/<YYYYMMDD-HHMMSS>-<target>.yaml`, the time
  from one `date +%Y%m%d-%H%M%S` call when the file is first saved, never changed after. It
  carries no session id, because several sessions edit a review in place.
- **Lookup:** match names in the kind's folder against
  `^\d{8}-\d{6}-([0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}-)?<target>\.yaml$`, so an older name
  with a session id counts and `layout` never matches `workspace-layout`, and take the newest by
  time prefix. With none, save a new file. Older duplicates are left as written.
- **Convert:** a found file of the kind's older YAML version is rewritten in place to the new one,
  its content becoming round 1 and each of its findings `open`, keeping its name.
- **Cold round:** the reviewer reads the target before the review file, and a subagent reviewer
  gets the target and never the file, so earlier rounds cannot anchor it.
  A fix-check round, in a skill that has one, gets the previous round's blocking findings and the
  lines each fix changed, never the file.
- **Re-check:** before a round is merged, each `open` finding is read against the current target
  and set `fixed`, with the resolution `found fixed in round <n>`, where the target no longer has
  the defect.
- **Merge:** a finding that repeats an `open` one is not added again, and one that repeats a
  `fixed` one reopens it with a note in its resolution.
- **Tick off:** the session that makes a fix sets the finding's status and resolution (the edit,
  commit or PR, or why it will not be fixed) when it knows of the review file.
- **Targets:** a plan review's target is the plan's slug.

## Body

- **Verdict:** the latest round's verdict, `Ready to build`, `Revise first`, or `Rethink`, per
  the verdict table in the skill, with the round number.
- **Findings table:** one row per finding across every round, numbered from 1. Round is the round
  that raised it. Severity is `blocking` or `advisory`. Plan line is the plan line quoted. Finding
  says what is wrong, Fix is the edit, and Status is `open`, `fixed: <resolution>` or
  `won't fix: <resolution>`.
- **Rounds:** one section per round, oldest first, with its date and verdict, then:
  - **Lenses:** the lenses run, for example `Scope, Engineering`, then each lens skipped with its
    reason, for example `Skipped developer experience: no developer callers.`
  - **Questions for the owner:** each question only the plan's owner can answer, with a
    recommended answer. `None` when empty.
  - **Unverified:** findings not checked against the code or the repo, each with why. `None` when
    empty.
  - **Fixes made:** fix mode only: what was edited and what was left open. Omit the section
    outside fix mode.

## plan-review/v3: YAML with generated Markdown

A `plan-review/v3` review is a copy of `../assets/plan-review.template.yaml`, and the `.md` of the
same name is generated from it in the layout above, beside it. The YAML is the source: agents read
and edit it, and nobody edits the Markdown, which opens with `generated_from: <file>.yaml` and a
do-not-edit `generated_note`. The format in code is `plan-review-model.py` beside this file, and
`scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version, as for a `v2` file before it is converted.
Field paths count from 0, so `findings.0` is finding 1.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `plan-review/v3`. `plan`: the path of the plan reviewed.
- `rounds`: at least one, oldest first, each with `date` (an unquoted date), `verdict`, `lenses`
  (at least one), `skipped` (`lens` and `reason` per lens skipped), `questions` (`question` and
  `recommended`), `unverified` (`finding` and `why`), and `fixes_made`: one line per edit made or
  left open, in fix mode, and `null` outside it, which leaves the section out.
- `findings`: each with `round` (the 1-based round that raised it), `lens`, `severity`
  (`blocking` or `advisory`), `plan_line`, `finding` and `fix`, each one line, `status` (`open`,
  `fixed` or `won't fix`), and `resolution` (optional), required exactly when `status` is not
  `open`. The renderer numbers them from 1, so no number is stored.
- In each round, `Ready to build` allows no blocking finding that round raised, and
  `Revise first` needs one.
- An empty list is `[]` and renders as `None`, or `No findings.` for `findings`.

**Quote a value that holds `: ` or ` #`, or starts with a quote**, because YAML reads ` #` as a
comment, so a quoted plan line is written `plan_line: 'Phase 3 Check: "the app runs"'`.
Every value is strict, so quote a value such as `1.10` that must stay text.
