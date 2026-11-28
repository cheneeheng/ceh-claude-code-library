# Code review schema

The review `write-code-review` saves to
`.agents_workspace/product/review/code/<YYYYMMDD-HHMMSS>-<branch>.yaml`, with its `.md` rendered
beside it, when its comments are not posted on a PR, one file per branch, edited in place by every
later review of that branch. A reference to it names the `.yaml`. Its layout is
`../assets/code-review.template.md`, relative to this file. `<branch>` is the branch name with
every `/` replaced by `-`, so `feat/export` is saved as `<time>-feat-export.yaml`. A new review is
written as `code-review/v3` YAML, per the section at the end. An older `code-review/v2` file is
converted in place when a new round finds it, per the Review lifecycle, and a `code-review/v1`
review, a `.md` with no YAML beside it, stays as written.

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
- **Targets:** a code review's target is the branch, with every `/` replaced by `-`.

## Body

- **Verdict:** the latest round's verdict, `Approve`, `Request changes`, `Comment`, or
  `Cannot verify`, per the verdict table in the skill, with the round number and what must change
  to flip it to approve, or what settles it.
- **Line comments:** one bullet per finding across every round: the `path:line`, the label
  `[blocking]`, `[advisory]`, or `[question]`, the comment, then the round that raised it and its
  status, `open`, `fixed: <resolution>` or `won't fix: <resolution>`.
- **Rounds:** one section per round, oldest first, with its date, verdict and verdict detail, then
  its summary: one or two sentences on what the change does and the overall read.

## code-review/v3: YAML with generated Markdown

A `code-review/v3` review is a copy of `../assets/code-review.template.yaml`, and the `.md` of the
same name is generated from it in the layout above, beside it. The YAML is the source: agents read
and edit it, and nobody edits the Markdown, which opens with `generated_from: <file>.yaml` and a
do-not-edit `generated_note`. The format in code is `code-review-model.py` beside this file, and
`scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version, as for a `v2` file before it is converted.
Field paths count from 0, so `findings.0` is the first finding.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `code-review/v3`. `branch`: the branch reviewed, as written in git.
- `rounds`: at least one, oldest first, each with `date` (an unquoted date), `verdict`,
  `verdict_detail` (what flips or settles the verdict, one line) and `summary` (the summary
  comment in a `|` block, with its Against the spec and Dismissed lists when the skill writes
  them).
- `findings`: each with `round` (the 1-based round that raised it), `location` (a `path:line`
  with no spaces), `label` (`blocking`, `advisory` or `question`), `comment` (one line), `status`
  (`open`, `fixed` or `won't fix`), and `resolution` (optional), required exactly when `status` is
  not `open`. An empty list is `[]` and renders as `None`.
- In each round, over the findings that round raised, `Approve` allows no blocking finding,
  `Request changes` needs one, and there are at most five.

**Quote a one-line value that holds `: ` or ` #`, or starts with a quote or a backtick**, because
YAML reads ` #` as a comment and refuses a plain value that starts with a backtick.
