# Strategy

How this repo turns [`VISION.md`](VISION.md) into one system. The vision says what the library is
for and the principles that settle a decision. This file says how the plugins fit together to get
there, and how the next piece of work is chosen. It holds up against the vision. Where the two
disagree, the vision wins until it is changed on purpose.

Adopted 2026-10-10. Not yet tested by a reference run (see Measuring progress), so expect it to
change once one runs.

## The concept: one lifecycle, many entry points

The plugins started as a catalogue: one plugin per use case, picked and installed one at a time.
That is granular, but it is not a system. Nothing said how the output of one plugin becomes the
input of the next, so every plugin was its own island, and a new user had no route to follow.

Other skill libraries hold together through one organizing idea: a mandatory process loaded at
session start, a chain of steps where each leaves a file for the next, or a team of roles installed
at once. This repo keeps its granularity and adds the second kind of idea without the first:

- **One lifecycle.** The four stages in the vision, Shape, Build, Prove, and Tell, are a route, not
  only a filing system. A product moves through them in order.
- **Many entry points.** A person or agent can start at any stage: plan a feature in an existing
  codebase, audit an app that is already built, or write a launch post. Each plugin works installed
  alone.
- **Handoff files join the stages.** Each stage writes files the next stage reads. With several
  plugins installed, they chain through those files. Nothing routes, injects, or enforces the
  order.

## The stages

| Stage | The question it answers                                | Plugins                                                                                                                                                                                                         |
| ----- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Shape | What should exist, for whom, and is it worth building? | `ceh-business-plan`, `ceh-competitor-analysis`                                                                                                                                                                  |
| Build | How is it built? Then build it: code, UI, docs         | `ceh-build-planning`, `ceh-build-from-plan`, `ceh-python-service`, `ceh-python-library`, `ceh-web-frontend`, `ceh-ui-design`, `ceh-ag-ui`, `ceh-git-datastore`, `ceh-documentation`, `ceh-codebase-explanation` |
| Prove | Does it work, is it safe, and can a person use it?     | `ceh-testing`, `ceh-usability-audit`, `ceh-check-build-against-plan`, `ceh-security-audit`                                                                                                                      |
| Tell  | Who should find it, and what do they read?             | `ceh-blog`, `ceh-seo`                                                                                                                                                                                           |

The every-step plugins (`ceh-every-session`, `ceh-coding-conduct`, `ceh-git-workflow`, and the rest
of the vision's Every step row) sit outside the route. They apply at every stage.

**Build planning belongs to Build, not Shape.** Shape decides what and whether, once per product.
A build plan decides how, and it recurs for every feature inside the build loop:
`ceh-build-planning:write-build-plan` itself triggers on "how should we build this". Keeping it in
Shape would send "add a feature to my app" through the business-plan stage, the wrong door for a
new user. The two stay connected through the handoff: the build plan reads `product/BUSINESS_PLAN.md` when
one exists.

## The spine: handoff files

| Stage | Reads                                             | Writes                                                             |
| ----- | ------------------------------------------------- | ------------------------------------------------------------------ |
| Shape | an idea, a conversation                           | `product/BUSINESS_PLAN.md`                                         |
| Build | `product/BUSINESS_PLAN.md` when present, the repo | `product/plans/<slug>.md`, the code, `product/ARCHITECTURE.md`     |
| Prove | the plan, the code                                | `product/EVIDENCE.md`: tests, QA, security, usability, performance |
| Tell  | `product/BUSINESS_PLAN.md`, `product/EVIDENCE.md` | posts, listings, SEO pages                                         |

Shape to Build: `ceh-business-plan` writes `product/BUSINESS_PLAN.md`, and `ceh-build-planning` reads
it and writes the plan that `ceh-build-from-plan` and `ceh-check-build-against-plan` read. Prove to
Tell: `ceh-testing:write-evidence-report` rolls the checks' reports into `product/EVIDENCE.md`, and
`ceh-blog:draft-post` and `ceh-seo:write-project-listing-text` read it with `product/BUSINESS_PLAN.md`.

Three rules hold for every handoff file:

1. **A missing input is drafted, not demanded.** A plugin whose input file is missing drafts one
   from what exists and marks the gaps, so it still works installed alone (vision principle 6).
2. **Reading a handoff file is not a plugin dependency.** It adds no `dependencies` entry, so it
   never forces an extra install. A format two plugins share is duplicated into both and registered
   in `docs/CROSS_REFERENCES.md`, as `plan-format.md` already is.
3. **Every saved output has a versioned template.** A skill that saves a file fills a
   `<schema>.template.md` in a `references/` folder, whose frontmatter opens with
   `schema: <schema>/v<N>`, and the saved file keeps that line, so a reader can tell which format a
   file follows. The version goes up when a required field or heading is renamed or removed,
   because that is the change that breaks a reader. `validate.py` checks that each template opens
   with its schema line, is cited by its plugin, and matches its copies in other plugins. The
   reference run may still revise a format, through a version bump.

## Where files live: commit what the next stage reads

The test is who reads the file.

- **Committed in the target repo:** every handoff file, because another stage or another session
  reads it as input. It has to survive a fresh clone, and a person can review it in a pull request.
  This follows vision principle 2: a decision that shapes the repo for others belongs in a
  committed file.
- **Local in `.agents_workspace/`:** what only one session or its author reads. The decision log,
  session handoffs, research notes, questionnaires, competitor analyses, reviews and audits whose
  author acts on them (plan, code, and test-suite reviews, blog drafts outside a blog repo), and
  scratch work. A skill whose output would be lost with the chat saves it here.

**`product/` for the builders, `docs/` for users.** Committed handoff files go in `product/` in the
target repo. `docs/` holds only what users of the product read, so a docs site built from it never
publishes a plan or a business plan.

Committing every file a stage writes would bloat the repo, so committed handoff files have a
lifecycle:

- **Plans are kept.** A built plan stays in `product/plans/` with `status: built` and an append-only
  Record of how it was planned, reviewed, built, checked, proven, and merged, so the plan is the
  audit trail of its change. Its lasting decisions are also copied to the Key Decisions log in
  `product/ARCHITECTURE.md`. Planning stays cheap because `ceh-build-planning:write-build-plan` reads
  only the frontmatter of built plans.
- **Fix records are kept.** A bug fix does not go through a build plan, because the bug already
  says what to build. What it needs is the reason, so every fix commits
  `product/fixes/<slug>.md` with its symptom, diagnosis, cause, and regression tests, written by
  `ceh-coding-conduct:find-root-cause` and `ceh-testing:test-a-bug-fix`. A fix that changes a
  contract or the design is a feature, and goes through `ceh-build-planning:write-build-plan`.
- **Retro reports are kept when their fixes land here.** A retro looks back over one session
  (`ceh-session-diagnosis:diagnose-session`) or a period (`ceh-git-workflow:review-recent-work`)
  and routes each issue to the skill that fixes it: a bug to `find-root-cause`, a design change to
  `write-build-plan`, an agent mistake to `prevent-repeat-mistake`, a working rule to
  `record-project-decisions`. The agent acts on every route in the repo in the same session, and
  commits those issues to `product/retros/<date>-<kind>.md`, scrubbed when they quote a transcript,
  because the routed work reads them. Issues whose fix lands outside the repo, in user settings,
  an installed plugin, or Claude Code, stay local in `.agents_workspace/retros/` for the user.
  `prevent-repeat-mistake` saves its own report the same way, split by where each fix lands.
- **The evidence report is append-only.** `product/EVIDENCE.md` is one file per product, and each run
  adds a dated section at the top, so the section a plan's Record cites never changes. The separate
  QA, performance, security, and usability reports stay local: only the roll-up is read by another
  stage.

## How work is chosen

**A new skill or plugin has to fix a break on the spine:** a handoff a stage cannot use, a stop for
a human the vision does not allow, or a moment where the agent improvised because no skill covered
it. "A competitor has it" does not count, and neither does "it would be useful." This makes vision
principle 9 (small surface, sharp edges) a rule for choosing work.

The rule governs new components only. Fixes to existing components, and the every-step plugins,
follow the usual rules in `CLAUDE.md`, still bound by the vision.

Done on 2026-10-10, when the strategy was adopted: Prove writes the evidence report, through a
roll-up skill in `ceh-testing` because it is the Prove plugin every stack plugin already installs,
and Tell reads it with `BUSINESS_PLAN.md` instead of drafting from scratch.

The likely order next, judged from the current gaps and not yet confirmed by a run:

1. **The learning loop catches recurring overrides.** The vision says an override that keeps
   recurring is a plugin defect. `ceh-every-session:prevent-repeat-mistake` fixes one once a human
   names it, and `ceh-session-diagnosis:diagnose-session` finds one inside a session, but nothing
   notices one recurring across sessions.
2. **Parallel builds.** Only what Claude Code's native worktrees and subagents lack, per the
   vision's non-goal on rebuilding Claude Code.

## Measuring progress: the reference run

One real, small product is taken from idea to launch through the plugins, headless where possible.
The run records:

- every stop for a human, and whether the vision allows it (a fact only a human has, or an
  irreversible action) or it was a gap in the guidance;
- every point where the agent improvised because no skill covered the moment;
- every handoff where the next stage could not use the previous stage's file.

These counts give vision Goal 1 ("agents finish tasks without a human") a number to track. The first
run uses today's plugins unchanged and sets the baseline. After each fix, run again and compare.
The run makes real model calls, so it waits for an explicit human go-ahead. It has not run yet.

## A guide shows the route, not bundles

[`GETTING_STARTED.md`](GETTING_STARTED.md) shows the route: a core installed once, then a list of
moments in stage order, each naming the plugin to install, the command that starts it, and the
handoff file it writes. It shows the route without enforcing or installing it.

Scenario bundles did this job until 2026-10-10 and were retired. Three were cut by stack and two by
stage, so they mixed the two axes this file keeps apart. A stack bundle installed all of Build and
Prove at once, which breaks vision Goal 4 and principle 6, and a bundle refused to let any plugin
it installed be disabled. A document carries the route at no install cost. The bundles are in
`archive/`.

## What not to do

- **No mandatory router or orchestrator for the sake of cohesion.** Both conflict with "moments,
  not topics" and "load only what the moment needs." The handoff files give the shape without that
  cost.
- **No shared base plugin for handoff formats.** It would force an extra install on every run.
  Formats are duplicated, per the Shared-Standards Duplication Policy in `CLAUDE.md`.

## Where the repo does not match yet

This list shrinks as the gaps close. Remove a line in the PR that closes it.

No known gaps as of 2026-10-10.

## Open questions

- **The reference run's product.** Deferred. It must be small enough to finish in days, use a
  stack with a plugin, and be something worth publishing, so Tell has a real audience.

## Changing this file

Change it in a pull request with a `CHANGELOG.md` entry. A change that the vision does not allow
changes the vision first, in its own PR, per that file's Changing this file section.
