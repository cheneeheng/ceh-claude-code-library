# General review schema

The review `review-anything` saves to
`.agents_workspace/product/review/general/<YYYYMMDD-HHMMSS>-<target>.yaml`, with its `.md`
rendered beside it, one file per target, edited in place by every later review of that target. A
reference to it names the `.yaml`. Its layout is `../assets/general-review.template.md`, relative
to this file. `<target>` names the subject, by the first of these that applies:

- A kebab-case name the user gives.
- One file or folder: its path relative to the repo root, or to the working directory outside a
  repository, with every `/` and `.` replaced by `-`, so `docs/STRATEGY.md` is
  `docs-STRATEGY-md`. The repo root itself is the repo folder's name.
- Several paths: their common folder, named the same way, when they share one below the root,
  otherwise the first path followed by `-and-<n>-more`.

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
- **Re-check:** before a round is merged, each `open` finding is read against the current target
  and set `fixed`, with the resolution `found fixed in round <n>`, where the target no longer has
  the defect.
- **Merge:** a finding that repeats an `open` one is not added again, and one that repeats a
  `fixed` one reopens it with a note in its resolution.
- **Tick off:** the session that makes a fix sets the finding's status and resolution (the edit,
  commit or PR, or why it will not be fixed) when it knows of the review file.
- **Targets:** a general review's target is named as at the top of this file, and a found file
  whose `subject` differs from the subject at hand is not the target's file: the review is saved
  as a new file whose target ends in `-2`, or the next free number.

## Body

- **Verdict:** the latest round's verdict, `Done`, `Not yet`, or `Cannot judge`, with the round
  number and what flips or settles it.
- **Subject** and **Criteria:** the paths reviewed, and what they were judged against.
- **Findings:** one bullet per finding across every round: the location, the label `[blocking]`,
  `[advisory]`, or `[question]`, the comment, then the round that raised it and its status,
  `open`, `fixed: <resolution>` or `won't fix: <resolution>`.
- **Rounds:** one section per round, oldest first, with its date, verdict and verdict detail, its
  summary, and what that round did not cover.

## general-review/v1: YAML with generated Markdown

A `general-review/v1` review is a copy of `../assets/general-review.template.yaml`, and the `.md`
of the same name is generated from it in the layout above, beside it. The YAML is the source:
agents read and edit it, and nobody edits the Markdown, which opens with
`generated_from: <file>.yaml` and a do-not-edit `generated_note`. The format in code is
`general-review-model.py` beside this file, and `scripts/artifact.py` in the skill checks and
renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/<file>.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/<file>.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `findings.0` is the
first finding.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `general-review/v1`. `target`: as in the file name.
- `subject`: a list of the paths reviewed, at least one. `criteria`: a list of what the subject
  was judged against, at least one: file paths or stated sentences.
- `rounds`: at least one, oldest first, each with `date` (an unquoted date), `verdict` (`Done`,
  `Not yet` or `Cannot judge`), `verdict_detail` (what flips or settles the verdict, one line),
  `summary` (a `|` block) and `not_covered` (a list of what the round did not judge and why, `[]`
  when none).
- `findings`: each with `round` (the 1-based round that raised it), `location` (a path, optionally
  followed by `:<line>`, with no spaces, and for something missing the file or folder it belongs
  in), `label` (`blocking`, `advisory` or `question`), `comment` (one line), `status` (`open`,
  `fixed` or `won't fix`), and `resolution` (optional), required exactly when `status` is not
  `open`. An empty list is `[]` and renders as `None`. There is no cap on findings.
- In each round, over the findings that round raised, `Done` allows no blocking finding and
  `Not yet` needs one. `Cannot judge` sets neither, and is for a subject or criteria the reader
  could not read.

The `independent-reader` agent's `<location> | <label> | <comment>` line maps to `location`,
`label` and `comment`, and its `## Not covered` to the round's `not_covered`.

**Quote a one-line value that holds `: ` or ` #`, or starts with a quote or a backtick**, because
YAML reads ` #` as a comment and refuses a plain value that starts with a backtick.
