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

| Stage | The question it answers                                | Plugins                                                                                                                                                         |
| ----- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Shape | What should exist, for whom, and is it worth building? | `ceh-product-direction`, `ceh-competitor-analysis`                                                                                                              |
| Build | How is it built? Then build it: code, UI, docs         | `ceh-build-plan`, `ceh-python-service`, `ceh-python-library`, `ceh-web-frontend`, `ceh-ui-design`, `ceh-ag-ui`, `ceh-documentation`, `ceh-codebase-explanation` |
| Prove | Does it work, is it safe, and can a person use it?     | `ceh-testing`, `ceh-usability-audit`, `ceh-check-build-against-plan`, `ceh-security-audit`                                                                      |
| Tell  | Who should find it, and what do they read?             | `ceh-blog-and-seo`                                                                                                                                              |

The vision's Core plugins (`ceh-every-session`, `ceh-coding-conduct`, `ceh-git-workflow`,
`ceh-testing`) apply at every stage, and `ceh-testing` also sits on the route in Prove. The
On demand plugins (`ceh-workflow-builder`, `ceh-workflow-runner`, `ceh-session-learning`,
`ceh-session-orchestration`) sit
outside the route, installed for an activity that can come at any stage: turning repeated work
into a workflow and running it, splitting a session's work across worker sessions, or learning
from a session. How a stage, a plugin
and a skill nest is in the vision's How the library is cut.

**Build planning belongs to Build, not Shape.** Shape decides what and whether, once per product.
A build plan decides how, and it recurs for every feature inside the build loop:
`ceh-build-plan:write-build-plan` itself triggers on "how should we build this". Keeping it in
Shape would send "add a feature to my app" through the business-plan stage, the wrong door for a
new user. The two stay connected through the vision and the strategy, both read by the build plan.
It never reads the business plan: the business plan flows one way, so its dated tests do not
become a plan's goals (`decision-business-plan-readers.md`).

## The spine: handoff files

Every path below is under `.agents_workspace/product/` in the target repo.

| Stage | Reads                                                                                                                                         | Writes                                                                                                      |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Shape | an idea, a conversation, the repo                                                                                                             | `business/BUSINESS_PLAN.yaml`, `VISION.yaml`, `STRATEGY.yaml` and `PRD.yaml`, each with its generated `.md` |
| Build | `VISION.yaml`, `STRATEGY.yaml`, `PRD.yaml` and `ARCHITECTURE.yaml` when present, each checked first (the `.md` when no YAML exists), the repo | `plan/<slug>.yaml` and its generated `<slug>.md`, the code, `ARCHITECTURE.yaml` and its generated `.md`     |
| Prove | the plan, the code                                                                                                                            | `EVIDENCE.yaml` and its generated `EVIDENCE.md`: tests, QA, security, usability, performance                |
| Tell  | `business/BUSINESS_PLAN.yaml`, `EVIDENCE.yaml`, each checked first (the `.md` when no YAML exists)                                            | posts, listings, SEO pages                                                                                  |

Shape to Build: `ceh-product-direction` writes `VISION.yaml` and `STRATEGY.yaml`, and
`ceh-build-plan` reads them, putting what a plan would contradict under Open, and writes the
plan that it builds from and `ceh-check-build-against-plan` reads. `ceh-product-direction` also
writes `PRD.yaml`, the product's features with their requirements, acceptance criteria and
status, so the next plan is picked from a list: `ceh-build-plan:write-build-plan` plans a feature
from its requirements and links the plan back, `ceh-build-plan:implement-from-plan` marks it
built, and `ceh-every-session:whats-next` names the next one to plan. `ceh-product-direction` also writes
`business/BUSINESS_PLAN.yaml`, which no Build skill reads. Prove to
Tell: `ceh-testing:write-evidence-report` rolls the checks' reports into `EVIDENCE.yaml`, and
`ceh-blog-and-seo:draft-post` and `ceh-blog-and-seo:write-project-listing-text` read it with `business/BUSINESS_PLAN.yaml`. Each YAML has its
Markdown rendered beside it, and a reader takes the `.md` only where no YAML exists.

Three rules hold for every handoff file:

1. **A missing input is drafted, not demanded.** A plugin whose input file is missing drafts one
   from what exists and marks the gaps, so it still works installed alone (vision principle 6).
2. **Reading a handoff file is not a plugin dependency.** It adds no `dependencies` entry, so it
   never forces an extra install. A format two plugins share is duplicated into both and registered
   in `docs/CROSS_REFERENCES.md`, as `plan-schema.md` already is.
3. **Every saved output has a versioned template and a schema.** A skill that saves a file fills a
   `<schema>.template.md` in an `assets/` folder, whose frontmatter opens with
   `schema: <schema>/v<N>`, and the saved file keeps that line, so a reader can tell which format a
   file follows. The template is a bare skeleton to copy, and `references/<schema>-schema.md`
   beside it explains every field and section. The version goes up when a required field or
   heading is renamed or removed, because that is the change that breaks a reader. `validate.py`
   checks that each template opens with its schema line, holds no explanation, has its schema, is
   cited by its plugin, and matches its copies in other plugins. The reference run may still revise
   a format, through a version bump. A format can instead be YAML checked by a model: a
   `<schema>.template.yaml`, a `<schema>-model.py` beside the schema whose pydantic model checks
   every field and whose renderer writes the Markdown, and that Markdown saved beside the YAML
   with `generated_from:` in its frontmatter. The build plan, `plan/v2`, is the trial.

## Where files live: one product folder

Every file a lifecycle stage saves goes in `.agents_workspace/product/` in the target repo, under
the same name and sub-path wherever it is read. One folder means a person reviewing the artifacts
sees them all in one place, and a reference from one artifact to another never crosses folders. A
repo whose `CLAUDE.md` names another location keeps it.

- **`.agents_workspace/product/`** holds every lifecycle artifact: the vision and strategy, plans,
  the architecture document, the evidence report, fix records, retros, the reviews (plan, code,
  business plan, stress test, general), the audits (test suite, security, usability, general), QA
  and performance
  reports, blog
  drafts outside a blog repo, scratch work such as design variants and learning notes, and the
  business material in `business/`.
- **`.agents_workspace/workflow/`** holds `ceh-workflow-builder` specs and drafts and the run state
  of the workflows it generates, the default of `$CEH_WORKFLOW_BUILD_DIR` and
  `$CEH_WORKFLOW_RUN_DIR`.
- **`.agents_workspace/experiment/`** holds experiments, such as the orchestration-lab runs.
- **`.agents_workspace/` itself** holds the session tools: the decision log, session handoffs,
  research notes, questionnaires, the codebase explanation, and competitor analyses.

A reference to a format with a YAML source names the `.yaml`, never its generated `.md`. No skill
assumes `.agents_workspace/` is a git repo. Where it is one, a nested repo pushed to a private
remote, its history versions the artifacts, which vision principle 2 accepts as the versioned
workspace. Where it is a plain folder, the project decides whether to commit or ignore it.
Git-ignoring single product files per repo was rejected: nothing makes anyone remember it, and it
breaks silently when a file name changes.

**Business material stays out of committed product documents.** The business plan, the investor
deck, and the outreach notes hold pricing, unit economics, kill criteria, and investor contacts.
Only Tell reads the business plan, for audience and positioning, and works without it (rule 1
above). No skill that writes a product document the builders read (vision, strategy, product
requirements, build plan, architecture) reads it, because its tests, stages and dates would become that document's goals.

**`.agents_workspace/product/` for the builders, `docs/` for users.** `docs/` holds only what users
of the product read, so a docs site built from it never publishes a plan.

Keeping every file a stage writes would bloat the folder, so the artifacts have a lifecycle:

- **Vision and strategy are revised in place.** One of each per repo, kept, because every later
  stage reads them.
- **The product requirements are revised in place.** One `PRD.yaml` per repo. A feature keeps its
  id for good, and one that is dropped moves to the non-goals with its reason. A built feature a
  later version changes becomes a replaced feature: it moves to `replaced` with its successor,
  its reason and its plans, so the feature list is always the product as it is now.
- **Plans are kept.** A built plan stays in `plan/` with `status: built` and an append-only
  Record of how it was planned, reviewed, built, checked, proven, and merged, so the plan is the
  audit trail of its change. Its lasting decisions are also copied to the Key Decisions log in
  `ARCHITECTURE.yaml`. The decisions several features share are written before the first plan,
  by `ceh-build-plan:write-technical-design`, into the file's Technical Design section, one
  entry per topic that is edited in place while the log keeps its history, with a diagram of
  what is not built yet marked `planned`. Every plan reads the section and the log and follows
  them, so one feature's plan never decides
  the stack for the rest. Planning stays cheap because `ceh-build-plan:write-build-plan` reads
  only the frontmatter of built plans.
- **Fix records are kept.** A bug fix does not go through a build plan, because the bug already
  says what to build. What it needs is the reason, so every fix saves
  `fix/<YYYYMMDD-HHMMSS>-<slug>.yaml` (`fix-record/v3`, one record per functionality, its `.md`
  rendered beside it) with its symptom,
  diagnosis, cause, and regression tests, written by
  `ceh-coding-conduct:find-root-cause` and `ceh-testing:test-a-bug-fix`. A fix that changes a
  contract or the design is a feature, and goes through `ceh-build-plan:write-build-plan`.
- **Retro reports are kept.** A retro looks back over one session
  (`ceh-session-learning:diagnose-session`) or a period (`ceh-git-workflow:write-period-retro`)
  and routes each issue to the skill that fixes it: a bug to `find-root-cause`, a design change to
  `write-build-plan`, an agent mistake to `prevent-repeat-mistake`, a working rule to
  `record-project-decisions`. The agent acts on every route in the repo in the same session, and
  saves one report to `retro/<YYYYMMDD-HHMMSS>-<session-id>-<kind>.md` holding both the issues
  fixed in the repo and those whose fix lands outside it, in user settings, an installed plugin,
  or Claude Code, scrubbed when it quotes a transcript. `prevent-repeat-mistake` saves its own
  report the same way.
- **The evidence report is append-only.** `EVIDENCE.yaml` is one file per product, and each run
  adds a dated section at the top, so the section a plan's Record cites never changes. The separate
  QA, performance, security, and usability reports are read only by the roll-up.

### A review, an audit or a retro

The three words name different kinds of artifact, per
`.claude/rules/decision-review-audit-retro.md`. Two questions sort a request:

1. Is it about how the work went, not the work itself? Then it is a retro.
2. Otherwise, has the work been marked done or shipped? No is a review, yes is an audit.

The state of the work decides, not the word the user typed: "review this" about a merged document
is an audit.

|            | Review                                           | Audit                                                   | Retro                                             |
| ---------- | ------------------------------------------------ | ------------------------------------------------------- | ------------------------------------------------- |
| Subject    | The work itself                                  | The work itself                                         | How the work went                                 |
| When       | Finished, but not yet marked done or shipped     | Already marked done or shipped                          | After the work, looking back                      |
| Who checks | Someone the author asks                          | A reader independent of whoever built and checked it    | The people who did the work                       |
| Examples   | A plan before the build, a diff before the merge | A merged codebase, a shipped interface, a published doc | A session that went wrong, a month of merged work |
| Ends in    | A verdict: done, or not yet                      | Findings on its state                                   | Learnings that change the next piece of work      |
| Saved to   | `review/<kind>/`                                 | `audit/<kind>/`                                         | `retro/`                                          |
| After that | Edited in place as its findings are fixed        | Written once, so a rerun is a new file                  | Written once, so a rerun is a new file            |

A subject with a skill of its own goes to that skill. Any other review goes to
`ceh-every-session:review-anything`, and any other audit to `ceh-every-session:audit-anything`.
The two generic skills go beyond the table in two places: a review may end in `Cannot judge` when
the reader could not read the subject or the criteria, and the word typed decides only when the
state of the work cannot be told.

The file-name forms are in `decision-saved-file-names.md`: a review carries no session id, and an
audit and a retro carry one. A new skill, schema or folder takes the word that matches.

A review is edited in place because the author reads one file until the verdict is done. An audit
is a record of what was found at one time, so fixing its findings does not change it, and the next
audit shows whether they held. For an agent, an independent reader is one that has not seen the
session that built the work.

## How work is chosen

**A new skill or plugin has to fix a break on the spine:** a handoff a stage cannot use, a stop for
a human the vision does not allow, or a moment where the agent improvised because no skill covered
it. "A competitor has it" does not count, and neither does "it would be useful." This makes vision
principle 9 (small surface, sharp edges) a rule for choosing work. A new skill also passes the
vision's moment test, whose third step, the step the agent gets wrong without the skill, is where
a break on the spine shows.

The rule governs new components only. Fixes to existing components, and the Core and On demand
plugins, follow the usual rules in `CLAUDE.md`, still bound by the vision.

Done on 2026-10-10, when the strategy was adopted: Prove writes the evidence report, through a
roll-up skill in `ceh-testing` because it is the Prove plugin every stack plugin already installs,
and Tell reads it with `BUSINESS_PLAN.md` instead of drafting from scratch.

The likely order next, judged from the current gaps and not yet confirmed by a run:

1. **The learning loop catches recurring overrides.** The vision says an override that keeps
   recurring is a plugin defect. `ceh-every-session:prevent-repeat-mistake` fixes one once a human
   names it, and `ceh-session-learning:diagnose-session` finds one inside a session, but nothing
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
`tools/setup/setup.py` is a second way through the same route, not a bundle: it installs only the
plugins the person picks, each after a yes, plus the tools and settings no plugin can install for
itself.

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
  Formats are duplicated, per `.claude/rules/decision-shared-standards-duplication.md`.

## Where the repo does not match yet

This list shrinks as the gaps close. Remove a line in the PR that closes it.

None.

## Open questions

- **The reference run's product.** Deferred. It must be small enough to finish in days, use a
  stack with a plugin, and be something worth publishing, so Tell has a real audience.

## Changing this file

Change it in a pull request with a `CHANGELOG.md` entry. A change that the vision does not allow
changes the vision first, in its own PR, per that file's Changing this file section.
