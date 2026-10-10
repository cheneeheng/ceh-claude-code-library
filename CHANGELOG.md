# Changelog

This repo has no releases. Every pull request adds its entry under a section headed by the date the
PR was opened, `YYYY-MM-DD`, and PRs opened on the same day share one section. Each plugin keeps its
own [Semantic Versioning](https://semver.org/) version, listed per section under
`### Plugin versions` and tracked in [`docs/PLUGIN_VERSIONS.md`](docs/PLUGIN_VERSIONS.md). Notes
before this repo live in
[agent-skills](https://github.com/cheneeheng/agent-skills/blob/main/CHANGELOG.md).

---

## 2026-10-10

The repo gets a strategy, `docs/STRATEGY.md`, to sit beside the vision. The plugins were a
catalogue: granular, but with nothing saying how one plugin's output becomes the next one's input.
The strategy names the system, one lifecycle with many entry points: the vision's four stages are a
route, and committed handoff files join them without a router. It moves build planning from Shape to
Build, sets which files a target repo commits (whatever a later stage reads, with built plans
distilled and deleted), and makes fixing a break on that route the test for new work. No plugin
changes yet. The gaps it opens are listed in its own "Where the repo does not match yet" section.

A second PR the same day closes every one of those gaps, so the route now runs end to end. The
vision moves build planning to Build and links the strategy. It lands in this PR rather than its
own because the user asked for one PR. Plans now leave the repo once built: their lasting decisions
move to a committed `docs/ARCHITECTURE.md` and the file is deleted, so `docs/plans/` holds only
work in flight. A new `ceh-testing` skill rolls the scattered Prove reports into one committed
`docs/EVIDENCE.md`, which the blog and listing skills read with `BUSINESS_PLAN.md`, so a launch
post claims only what was proven. Each scenario bundle README now shows its route.

A third PR the same day retires the five scenario bundles and replaces them with
`docs/GETTING_STARTED.md`. The bundles no longer fit the strategy: three were cut by stack and two
by stage, a stack bundle installed all of Build and Prove at once (up to 13 plugins), and none let
the user disable a plugin it pulled in. The guide installs a small core once, then one plugin per
stage as the user reaches it, at project scope. The vision, strategy, `CLAUDE.md`, the README and
the validator change with it, in this one PR at the user's request. Anyone who installed a bundle
keeps its plugins: uninstall the bundle and reinstall from the guide.

A fourth PR the same day fixes where a newcomer gets stuck in the guide. Five cold persona walkers
read it, and every one had to assemble the stack-plugin command from the README by hand. Nothing
told them how to check what was installed, whether a re-run was safe, or that new skills need a
reload. The guide now opens with a prompt to paste into Claude Code, which asks what you are about
to do and installs only that. The user tested it live in a fresh config: Claude asked first,
installed only the core and the plugin for the stated moment, and the skills appeared after
`/reload-plugins`. A setup script was considered and rejected: a session needs nothing installed
first, and a script would need four copies to keep in sync. No plugin changes.

A fifth PR the same day clears the remaining walker findings. The guide named
`ceh-business-plan:find-product-market-fit` as the first Shape step, but that skill cannot be
typed. The entry point is `/ceh-business-plan:develop-business-plan`, so every moment now names the
slash command that starts it. The README's paste-ready block of all 26 plugins at user scope is
gone, because walkers kept copying it instead of following the guide. No plugin changes.

A sixth PR the same day makes the guide work for someone who does not write code. Five cold walkers
played a person with a product idea who neither codes nor uses git. One stalled, because the guide
only ever said to run installs "in that repo", and nobody without git has a repo. Project scope
works in any plain folder, which was checked in an isolated config, so the guide now says so. The
guidance on skipping the coding plugins now comes before their install commands rather than
after. No plugin changes.

A seventh PR the same day cuts every skill description to 300 characters or fewer. The skill
listing has a budget of 1% of the context window, and Claude Code drops whole descriptions once it
overflows: in a session with nine of these plugins installed, nine skills showed up with a name and
no description, so nothing could trigger them. The skill descriptions totalled about 44,000
characters, and over 9,000 of those went on "Not for X (use Y)" clauses, many pointing at plugins
the user may not have installed. Each description now keeps the moment, two or three trigger phrases,
and at most one pointer to its nearest look-alike. The skill bodies still carry the full routing.
`validate.py` enforces the cap. The same PR states a rule for the invocation flags: a skill only the
model loads sets `user-invocable: false`, and a skill only the user may start sets
`disable-model-invocation: true`. That moves `design-test-cases`, `write-plain-language`, and
`audit-error-messages` to model-only. No new user-only skill was added, because the library is
agents-first and a user-only skill cannot be loaded by a request, an agent, or a workflow stage.

An eighth PR the same day applies the same cap to agents, whose descriptions also load into every
session. Twelve of the thirteen were over it. Each one now says when to delegate (proactively, only on request, or which skill
dispatches it), two trigger phrases, and whether it is read-only. Why isolation helps moves to the
body, where it already was. Skills and agents now share one 300-character cap, and all
descriptions together come to 26,768 characters. The repo-local `add-plugin-component` skill, about
700 characters, is cut to fit as well.

A ninth PR the same day adds `ceh-orchestration-lab` to the vision's lifecycle table, under Every
step and marked experimental. It was the only published plugin missing there, though the README and
`CLAUDE.md` already listed it, while the vision claimed no known gaps. A short note says the plugin
is an experiment and leaves the table, to `archive/` or as a standard, when the experiment ends. No
plugin changes.

A tenth PR the same day moves the per-skill and per-agent tables out of the README into
`docs/CATALOG.md`. They were about 300 of the README's 516 lines, a third copy of what each plugin
README and `SKILL.md` description already say, and they buried what the repo is and how to install
it. The README keeps the Plugins and lifecycle-stage tables. The manual install section is
rewritten: it told users to list plugin paths under a `plugins` key in `settings.json`, which Claude
Code does not read. A local clone is now added as a marketplace, or one plugin loaded with
`--plugin-dir`. No plugin changes.

An eleventh PR the same day fixes the same wrong install block in the `ceh-git-datastore` README,
the one plugin README that still had it.

A twelfth PR the same day lets a user say "set up <repo URL>" instead of pasting the setup prompt.
A fetch of the repo page showed Claude reading the whole README but finding nothing addressed to
it, so it had to guess the steps. The README now opens with a short note to Claude Code that carries
the paste-in prompt's rules and links the raw guide. The guide does not advertise the short form
yet, because no live session has run it. The README's Tools and Formatting sections, which serve
maintainers, move to a new `CONTRIBUTING.md`. No plugin changes.

A thirteenth PR the same day follows a live test of that note in an isolated config. Claude asked
first, installed only the right plugins, and asked for `/reload-plugins`, but it cloned the repo
into the user's folder to read the guide. The note and the guide now say not to clone: read the
guide from its URL and add the marketplace by name. The README's "From a local clone" section is
marked as not part of this setup. With the test passed, the guide leads with the short form,
`setup <repo URL>`, and keeps the long prompt as a fallback. No plugin changes.

A fourteenth PR the same day changes what the user types. In three more live runs, one still cloned
the repo, into the project folder, and deleted it afterwards. The decision to clone comes from
"setup" next to a repo URL, before Claude reads any note. So the guide now has the user type
"install the Claude Code plugins from" the raw guide URL, which is a file, not something Claude can
clone. The guide gets its own note to Claude, which replaces the long paste-in prompt. The README
note stays for anyone who still types the repo URL. No plugin changes.

A fifteenth PR the same day moves the output style from `ceh-coding-conduct` to
`ceh-every-session`. Its response format and honesty rules hold however Claude Code is used, so
they pass the every-session admission test better than a coding plugin. The style drops its coding
rules ("code first", "reading code is inferred", the bug-fix example) for activity-neutral ones,
and is renamed `CEH Every Session`. It keeps `keep-coding-instructions: true`, because `false` would
strip Claude Code's engineering instructions from every coding session. The getting-started guide
now makes `ceh-every-session` the one install for everyone, instead of an optional row, so the style
reaches every user. A hard dependency from every plugin on it was considered and rejected: it breaks
the every-run rule for edges and VISION principle 6, and it would force the plugin's hooks onto users
who never chose them.

### Plugin versions

| Plugin                         | Version |
| ------------------------------ | ------- |
| `ceh-ag-ui`                    | 1.1.2   |
| `ceh-blog`                     | 1.0.7   |
| `ceh-build-from-plan`          | 1.0.2   |
| `ceh-build-planning`           | 1.1.2   |
| `ceh-business-plan`            | 1.1.3   |
| `ceh-check-build-against-plan` | 1.0.3   |
| `ceh-codebase-explanation`     | 1.2.3   |
| `ceh-coding-conduct`           | 2.2.4   |
| `ceh-competitor-analysis`      | 1.1.7   |
| `ceh-documentation`            | 1.0.5   |
| `ceh-every-session`            | 2.5.0   |
| `ceh-git-datastore`            | 1.0.5   |
| `ceh-git-workflow`             | 1.2.4   |
| `ceh-orchestration-lab`        | 1.0.1   |
| `ceh-python-library`           | 1.0.3   |
| `ceh-python-service`           | 1.1.3   |
| `ceh-scenario-editorial`       | 1.1.1   |
| `ceh-scenario-ideation`        | 1.2.1   |
| `ceh-scenario-library`         | 1.2.1   |
| `ceh-scenario-service`         | 1.2.1   |
| `ceh-scenario-webapp`          | 1.2.1   |
| `ceh-security-audit`           | 1.0.1   |
| `ceh-seo`                      | 1.1.3   |
| `ceh-session-diagnosis`        | 1.0.2   |
| `ceh-session-to-skill`         | 1.0.1   |
| `ceh-testing`                  | 1.4.1   |
| `ceh-ui-design`                | 1.0.5   |
| `ceh-usability-audit`          | 1.1.5   |
| `ceh-web-frontend`             | 1.3.3   |
| `ceh-workflow-builder`         | 1.3.6   |
| `ceh-workflow-runner`          | 1.0.4   |

### Added

- `docs/STRATEGY.md`: the stages, the handoff files between them, where they live, how work is
  chosen, and the reference run that will measure progress.
- `ceh-testing:write-evidence-report`: runs the test suite once and rolls the latest QA,
  performance, security, usability, and plan results into a committed `docs/EVIDENCE.md`. Each
  area is marked passed, open issues, stale, or not run, and the report lists the claims a launch
  may make.
- A Route section in every scenario bundle README: the skill that fires at each stage, and what it
  reads and writes.
- `docs/GETTING_STARTED.md`: the first-time install route. The core at user scope, a table of
  moments in stage order naming the plugin, the skill that fires, and the file it writes, the
  stack plugins, and the plugins to add only when their moment arrives. Linked from the top of the
  README.

### Changed

- The five scenario bundles are retired: removed from the marketplace and moved to `archive/`, with
  their reason in `archive/README.md`. Their rows above record their last published versions.
- `docs/VISION.md` (Granular) and `docs/STRATEGY.md`: the install route is the guide, not bundles.
  STRATEGY records why the bundles were retired.
- `CLAUDE.md`: three tiers instead of four, one `plugins/standalone/` folder, and the guide in
  Structure and Key Files.
- README: the stage table replaces the tier table, and Install step 2 points to the guide.
- `validate.py` and `model-audit`'s `detect.py`: the scenario bundle checks and exclusions are
  gone. `docs/PLUGIN_DEPENDENCIES.md` drops the bundle sections and the bundle rule.
- `add-plugin-component`: a new plugin gets a row in the guide instead of a place in a bundle.
- `ceh-coding-conduct` and `ceh-orchestration-lab` READMEs: bundle mentions replaced with install
  guidance.
- `docs/GETTING_STARTED.md`: a "Let Claude set you up" section with a paste-in prompt, and a worked
  example for a new Python service with the planning install now and the build installs later. Step
  3 says project scope writes `.claude/settings.json`. Step 5 adds `/reload-plugins`,
  `claude plugin list`, safe re-runs, the `--scope project` uninstall, and that removing the
  marketplace removes its plugins.
- `docs/GETTING_STARTED.md`: the stage table becomes a list per stage that reads at 80 columns,
  each moment with the slash command that starts it. The Shape entry point is corrected to
  `/ceh-business-plan:develop-business-plan`. New lines cover how to confirm and undo the
  marketplace, that `/plugin` and `claude plugin` are the same command, what user scope and a hook
  are, the optional `ceh-every-session` install, and creating a branch before the first skill
  writes in a new repo.
- README: Install step 2 drops the 26-line `--scope user` command block and points to the guide.
  Step 3 adds `/reload-plugins`.
- `docs/STRATEGY.md` and `add-plugin-component`: describe the guide's moments as a list with slash
  commands, and drop the README `/plugin install` list from the new-plugin checklist.
- `docs/GETTING_STARTED.md`, for newcomers who do not write code:
  - project scope and the setup prompt say "a git repo or any plain folder"
  - the skip-the-coding-plugins guidance moves above the core install block, which gets an "If you
    write code in git repos" lead-in
  - the project-scope install pattern is stated once, in its own code block, above the moments
  - the branch advice applies only with `ceh-git-workflow`
  - committing `.claude/settings.json` applies only in a git repo
  - step 1 says how to resume after an interruption

- `CLAUDE.md`: lists `docs/STRATEGY.md` in Structure and Key Files.
- `docs/VISION.md`: `ceh-build-planning` moves from Shape to Build, and the scope section links
  `docs/STRATEGY.md`.
- Plan format, in all three copies: `docs/plans/` holds only plans not yet built. A built plan is
  distilled into `docs/ARCHITECTURE.md` Key Decisions and deleted, once any check against it has
  run.
- `ceh-build-from-plan:implement-from-plan`: a new Retire step runs the check against the plan when
  that plugin is installed, then distills and deletes the plan. The changelog entry it adds is
  conditional on the repo keeping one, here and in the plan format.
- `ceh-business-plan`: `derived_from` keeps a retired plan's path, which stays valid in git
  history, and `find-product-market-fit` reads `docs/ARCHITECTURE.md` and the README for an app
  whose plans are already retired.
- `ceh-testing:write-evidence-report`: with no plan in flight, the Plan area reads `none in flight`
  rather than `not run`.
- `ceh-codebase-explanation:document-architecture`: writes a committed `docs/ARCHITECTURE.md`
  instead of `.agents_workspace/ARCHITECTURE.md`, and moves an existing one there on first run.
- `ceh-blog:draft-post` and `ceh-seo:write-project-listing-text`: read `BUSINESS_PLAN.md` and
  `docs/EVIDENCE.md` first, and make no claim about an area the evidence marks stale, not run, or
  open.
- `docs/TESTING_WORKFLOW.md`, `docs/CROSS_REFERENCES.md`: the new skill's trigger row, and a new
  entry for the handoff paragraph the blog and SEO skills share.
- Every skill description over 300 characters, in 25 plugins: cut to the moment, two or three
  trigger phrases, and at most one "Not for" pointer. The skill descriptions total about 23,500
  characters, down from about 44,000.
- `validate.py`: a 300-character cap on skill descriptions (agents keep 600), and the
  description-total ratchet lowered from 51,186 to 30,010.
- `ceh-testing:design-test-cases`, `ceh-usability-audit:write-plain-language`, and
  `ceh-usability-audit:audit-error-messages` are model-only (`user-invocable: false`). The model
  still loads them on a request; they leave the `/` menu.
- `plugins/CLAUDE.md`: the description cap and its reason, and a three-row table for the invocation
  flags (model only, user only, both). The `add-plugin-component` skill template and checklist and
  `tools/validate-plugins/README.md` say the same.
- Every agent description, in six plugins: cut to 300 characters or fewer, keeping the delegation
  signal ("Use proactively", "only when the user explicitly asks", or the dispatching skill).
- `validate.py`: one 300-character cap for skills and agents, replacing the separate skill cap, and
  the description-total ratchet lowered from 30,010 to 26,768.
- `add-plugin-component`: its own description is cut from about 700 to 300 characters, and the agent
  template, `plugins/CLAUDE.md`, and `tools/validate-plugins/README.md` state the agent cap.
- `docs/VISION.md`: `ceh-orchestration-lab` (experimental) in the Every step row of the lifecycle
  table, with a note on how it leaves the table.
- README: the Skills and Agents tables, with the plugin-agent notes, move to the new
  `docs/CATALOG.md`, linked from the top of the README. The 26-path manual install block becomes
  `/plugin marketplace add` on a local clone, plus `claude --plugin-dir` for a one-session trial.
- `CLAUDE.md`, `plugins/CLAUDE.md`, and `add-plugin-component`: new skill and agent rows go in
  `docs/CATALOG.md`, and a new plugin no longer adds a manual install path. `CLAUDE.md` now says the
  catalog row is a review rule, not a CI check, and drops a parked idea for a concept-map skill.
- `plugins/CLAUDE.md`: says `validate.py` enforces `user-invocable: false` on a skill a hook names.
- README: a note to Claude Code at the top on how to set the repo up, and the Tools and Formatting
  sections move to the new `CONTRIBUTING.md`, which `CLAUDE.md` lists in Key Files.
- README note and `docs/GETTING_STARTED.md`: setup never clones the repo. The guide leads with
  `setup https://github.com/cheneeheng/ceh-claude-code-library`, and the long prompt is the
  fallback.
- `docs/GETTING_STARTED.md`: the user types "install the Claude Code plugins from" the raw guide
  URL, and a note to Claude in the guide replaces the long paste-in prompt.
- The output style moves from `ceh-coding-conduct` to `ceh-every-session`, renamed from
  `CEH Coding Conduct` to `CEH Every Session`. Its rules and example no longer assume code, and the
  summary table gains a leading `#` column so rows can be referred to by number. Both
  plugin READMEs, the root README, and `docs/IDEAS.md` follow.
- `docs/GETTING_STARTED.md`: `ceh-every-session` is installed by everyone, first, and the note to
  Claude says to install it whatever the user is about to do.

### Fixed

- `ceh-git-datastore` README: the manual install block used a `plugins` key in `settings.json` that
  Claude Code does not read. It now adds a local clone as the marketplace, or loads the plugin for
  one session with `--plugin-dir`.

## 2026-10-09

Five ideas from `docs/IDEAS.md` are built. Until now nothing ran the hook scripts: `validate.py`
only syntax-checked them, so a broken guard still passed CI. Now `validate.py` pipes hand-built
tool calls into every hook and checks the exit code and output. Every hook also gets a kill
switch, `CEH_DISABLED_HOOKS`. The three deny guards send their full text three times per session,
then one numbered line, because an identical deny block repeated pushes the model into loops. Two
new skills cover moments nothing covered before: finding a bug's cause before fixing it, and
writing the failing test before new code by default. `docs/IDEAS.md` moves to one table per
section.

A new experimental plugin, `ceh-orchestration-lab`, moves the orchestration experiment from
synthetic tasks into real projects. Every batch of the synthetic benchmark was solved by Haiku
alone, so it could not separate the strategies. The plugin ships the two strategies a skill can
drive, and each run leaves a folder in the target project with the base commit, the plan or
briefs, every worker report, the token usage by model, and the user's verdict. Runs that show a
pattern can later become fixtures for a controlled rerun. The archived `ceh-orchestration` served
as background only. Nothing was copied from it.

Ten more ideas from `docs/IDEAS.md` are built, all from its Build section. Three new
`ceh-every-session` skills work on any kind of file, not only code: a research note in which
every claim is cited, a plan stress-test that asks in rounds with a recommended answer each time,
and a fix for a mistake that keeps coming back, placed at the strongest level that would have
caught it. The last one merges the Session retro and `/correct` ladder ideas. It moved from
`ceh-coding-conduct` to `ceh-every-session` because the same ladder holds for notes, plans, and
strategy documents. `code-review` can now hand a large diff to two new read-only stack reviewers
that run in parallel, one in `ceh-python-service` and one in `ceh-web-frontend`, so the
cross-cutting git plugin carries no stack-specific rules. Retros, performance measurement, a
committed glossary, worktree isolation, motion rules, and a context budget report fill the rest.

A third batch of ten Build ideas follows, chosen from the entries that need no observed failure, no
further trial, and no change to `ceh-plan-build-review`, which is due for a rework of its own.
`code-review` now checks a linked spec on its own axis, so a style nit can never outrank a missing
requirement, and offers an opt-in panel that sends one brief to several models and ranks findings
by agreement. Four new skills cover moments nothing covered before: sketching types and boundaries
before code, exploring the running app for bugs, proving a migration left the UI's look unchanged,
and turning a validated business plan into investor materials. `refactor-repo` proposes shallow
modules to deepen, `design-ui` builds a variants board when the direction is open, and
`explain-until-understood` can keep a learning file across sessions. The developer-experience
walkthrough became one paragraph in `simulate-newcomer-first-run`, because that skill and
`audit-interface` already covered the install path and the API, and the only gap was code samples
that fail when pasted.

`docs/VISION.md` now plans the split of `ceh-plan-build-review`. It was the only plugin listed in
three lifecycle stages, so a user who only wanted to check code against a plan had to install the
planner and the builder too. The lifecycle table names its three replacements, one per stage:
`ceh-build-planning`, `ceh-build-from-plan`, and `ceh-check-build-against-plan`. Principle 6 now
says a plugin covers one stage. Until the split lands, the gap is listed under "Where the repo does
not match yet".

The split itself follows. `ceh-plan-build-review` is archived, and three plugins replace it, one
per stage. Each works installed alone, so a user who enters at one stage installs only that stage.
`ceh-build-planning:write-build-plan` plans a new app or one feature in an existing codebase, which
the old app-only planner could not. `ceh-build-from-plan:implement-from-plan` now proves every
phase: it writes the failing test first, runs the phase's own check, and records the evidence in
the plan. Before, it ended with "items the user should verify manually".
`ceh-check-build-against-plan:check-build-against-plan` is report-only by default and also flags
built code the plan left out, which a test suite cannot see. The three share one short plan format,
committed under `docs/plans/`, in place of the `SKELETON` / `ITER_NN` families with their version
tags, pointers, and `depends_on` chains. `apply-small-fix-to-version` is not carried over, because
it existed only to keep that format in step with small fixes. The old stack-specific gotchas file
moved into the stack skills where each trap occurs, and the planning-time ones (implicit resource
creation, LLM roles and context) into the planner's design checklist. Middleware order was already
covered, and the async ORM trap fits no stack here, so both were dropped. So were the Docker volume
and SSE heartbeat traps, which no stack skill owns.

A triage of the open `docs/IDEAS.md` entries follows. Six are rejected for now, two wait on
`ceh-orchestration-lab` leaving experimental, one is dropped until the built-in `run` skill proves
short, the verify gate waits on evidence, and four are built. Two new plugins, each loaded only when
needed: `ceh-session-diagnosis` finds why a session went wrong from its transcript, and
`ceh-security-audit` audits the whole codebase, which Claude Code's `/security-review` does not,
since it checks only pending changes. Session diagnosis was first marked as an every-session
candidate. It became a plugin of its own because it fires only after something went wrong, and an
every-session description costs every session. `ceh-build-planning` gains a plan review before
anything is built. `code-review` and `check-build-against-plan` gain an opt-in gate where two fresh
reviewers must both pass. Neither sees the other or the session, so neither inherits the fixer's
belief that the fix worked.

`docs/IDEAS.md` becomes the backlog for every idea about this repo, wherever it came from, not only
the competitor analyses. It splits into Done and Open, on hold, and rejected, so what is left to
decide no longer hides among the built rows. A new open idea, a project rules generator for
`ceh-every-session`, writes the fixed facts of one project, such as "Svelte, not React", as rules
that bind code, planning, and writing tasks alike. Fan-out and long runs is scoped and put on hold:
fan-out and long runs are covered, and the stacked-PR remainder waits until stacked PRs are in use.
`CLAUDE.md` now says that everything added or changed must hold up against `docs/VISION.md`, not
only new plugins, ideas, and rules.

`docs/VISION.md` now opens with the same rule, so the vision and `CLAUDE.md` name the same set of
changes it governs. Before, the vision listed only new plugins, ideas, and rule changes. The
repo-local `add-plugin-component` checklist now starts with that check, so it runs where components
are actually added.

A project's decisions now have a committed home that every session reads. Until now the plugins
recorded a decision in the agent's git-ignored decision log, or in a committed file only when it
was an architecture or plan decision, so "Svelte, not React" or "EU small businesses only" bound
nothing in the next session. `ceh-every-session:record-project-decisions` writes each decision as
its own short rule file, `.claude/rules/decision-<topic>.md`, which Claude Code loads at launch with
the priority of `.claude/CLAUDE.md`, so code, planning, and writing tasks all follow it. One file
per decision keeps each one short, and retiring a decision deletes one file. Its seed mode
collects the choices installed skills leave open, the decisions already in the project's
documents, and a short list of areas, then asks only what the files do not answer.

`ceh-workflow-builder` and `ceh-workflow-runner` now match `docs/VISION.md`. Repetition is the
intake test: a workflow exists because the same steps run again in the same shape with only the
input changing, so the descriptions and examples speak of repeated product work (a weekly SEO
pass, a pre-release check) and the interview's triage states the test outright. The builder gains
the no-human path the vision's interview exception requires: headless, it drafts from what the
spec answers into the build directory, marks every open row, records its conservative choices as
assumptions, writes nothing into `.claude/skills/`, and ends with the questions a person must
answer. Both skills now say a stage goes to Claude Code's native capability wherever one covers
the step, and that the runner keeps only approvals between stages, world checks before a re-run,
resume state, and the `FLOW STATUS:` line, so it shrinks as Claude Code grows. The builder skill is
cut from 472 to 376 lines, mostly by dropping what `flow-config-schema.md` already says. The
cut is not eval-verified.

### Plugin versions

| Plugin                         | Version |
| ------------------------------ | ------- |
| `ceh-build-from-plan`          | 1.0.0   |
| `ceh-build-planning`           | 1.1.0   |
| `ceh-business-plan`            | 1.1.1   |
| `ceh-check-build-against-plan` | 1.0.1   |
| `ceh-codebase-explanation`     | 1.2.1   |
| `ceh-coding-conduct`           | 2.2.1   |
| `ceh-every-session`            | 2.4.0   |
| `ceh-git-workflow`             | 1.2.3   |
| `ceh-orchestration-lab`        | 1.0.0   |
| `ceh-python-service`           | 1.1.1   |
| `ceh-scenario-ideation`        | 1.2.0   |
| `ceh-scenario-library`         | 1.2.0   |
| `ceh-scenario-service`         | 1.2.0   |
| `ceh-scenario-webapp`          | 1.2.0   |
| `ceh-security-audit`           | 1.0.0   |
| `ceh-session-diagnosis`        | 1.0.0   |
| `ceh-testing`                  | 1.3.0   |
| `ceh-ui-design`                | 1.0.4   |
| `ceh-usability-audit`          | 1.1.3   |
| `ceh-web-frontend`             | 1.3.1   |
| `ceh-workflow-builder`         | 1.3.5   |
| `ceh-workflow-runner`          | 1.0.3   |

### Added

- `ceh-every-session` 2.4.0, `record-project-decisions`: one rule file per project decision under
  `.claude/rules/decision-<topic>.md`, loaded in every session. Record mode writes one decision, seed mode
  collects open choices from installed skills and the project's documents and asks the rest.
- `ceh-session-diagnosis` 1.0.0, a new plugin. `diagnose-session` finds the transcript, dispatches
  four `transcript-analyst` agents in parallel (instructions, tools, context, claims), re-reads
  every cited line a conclusion rests on, and classes each root cause as request, guidance,
  environment, model, or Claude Code, with the file its fix goes to. A copy for sharing is
  scrubbed, then audited by a fresh subagent for up to three rounds.
- `ceh-security-audit` 1.0.0, a new plugin. `audit-codebase-security` maps entry points, trust
  boundaries, assets, and attackers before reading for bugs, traces each entry point through nine
  categories, quotes both the source and the sink of every finding, and saves the report under
  `.agents_workspace/` so an unfixed hole is never committed. It runs the dependency check only
  with consent to the network, never touches a live host, and never copies a secret's value.
- `ceh-build-planning:review-build-plan`: reviews a plan or spec before anyone builds from it,
  from a fresh subagent when the same session wrote it, through scope, engineering, design, and
  developer-experience lenses, with every finding quoting its plan line and a Ready, Revise, or
  Rethink verdict.
- `ceh-coding-conduct:find-root-cause`: reproduce the symptom with one command, list 3 to 5
  falsifiable hypotheses, gather evidence one variable at a time, and confirm the cause by a
  prediction before any fix. After two failed fixes it checks the premise every attempt shared.
- `ceh-testing:write-test-first`: red, green, refactor per slice of new behavior, by default
  rather than on request, with the failure seen before the code quoted in the hand-over.
- `CEH_DISABLED_HOOKS`: a comma-separated list of hook script names to skip, read by every hook
  in `ceh-coding-conduct`, `ceh-every-session`, and `ceh-git-workflow`.
- `validate.py` hook fixtures: every script a `hooks.json` runs needs fixtures, and each fixture
  checks the exit code and output for a hand-built payload. No model call is made.
- `ceh-orchestration-lab` 1.0.0, experimental and in no bundle:
  - `plan-then-implement`: this session writes one complete plan and one `implementer` subagent
    carries it out, with at most one fix-up resume.
  - `orchestrate`: this session briefs and reviews in a loop while `implementer` subagents do
    every edit and test run.
  - The `implementer` agent, whose model each run sets.
  - `scripts/token_usage.py`, which reads a session's transcripts and reports tokens by model
    from the run's start.
  - A shared run-log procedure in `references/run-log.md`, which writes
    `.agents_workspace/orchestration-lab/<stamp>_<session-id>/` per run plus a `runs.md` index.
- `ceh-every-session:write-research-note`: a background agent answers one question from primary
  sources into `.agents_workspace/research/`, every claim cited, and the session re-fetches the
  citations the answer rests on.
- `ceh-every-session:stress-test-plan`: questions a plan in rounds of at most four, only once a
  question's prerequisites are settled, each with a recommended answer. Facts come from a
  subagent, and the outcome is written back as `## Decisions` and `## Open`.
- `ceh-every-session:prevent-repeat-mistake`: names a repeated mistake from quoted evidence, picks
  the strongest fix (remove the cause, a Claude Code setting, a check, written guidance last),
  proves it fails on the real mistake, and only drafts changes to `CLAUDE.md`, settings, memory,
  or hooks.
- `ceh-git-workflow:write-engineering-retro`: what shipped and how work flowed over a period, from
  git history and `gh`, with at most three changes and no per-person counts.
- `ceh-testing:measure-performance`: vet a measurement against its noise, baseline, profile, and
  keep one change per measurement and one commit per win.
- `ceh-codebase-explanation:maintain-glossary`: settles one word and one definition per concept
  in a committed `GLOSSARY.md` and reports files still using a rejected alias.
- `ceh-python-service:python-service-reviewer` and `ceh-web-frontend:web-frontend-reviewer`:
  read-only reviewer agents that load only the plugin skills whose files the diff touches.
- `model-audit budget` (repo-local): `scripts/context_budget.py` reports per plugin what its
  descriptions and context-injecting hooks add to each session, prompt, and subagent, with no
  model call.
- `ceh-coding-conduct:sketch-design`: types, signatures, and module boundaries before code, then
  four checks on the sketch: illegal states, operations that run twice, shared state, and the
  smallest interface.
- `ceh-testing:explore-app-for-bugs`: charters over the changed areas of the running app, each bug
  reproduced twice with its evidence, into `.agents_workspace/qa/`. Report-only unless fix mode is
  asked for.
- `ceh-web-frontend:check-visual-parity`: deterministic Playwright screenshots of the old version
  as the baseline, the new version compared on the same machine, and every diff explained.
- `ceh-business-plan:write-investor-materials`: a deck outline and outreach notes from a validated
  plan, every slide citing its plan section and confidence tag, and an ask tied to the milestones
  it reaches. `develop-business-plan` routes "write a pitch deck" to it.
- `ceh-build-planning` 1.0.0, `write-build-plan`: triage, In and Out scope, detail only as far as
  the build is foreseeable, the design decisions a builder would otherwise stop on, and phases that
  each end in a runnable check, saved to `docs/plans/<slug>.md`.
- `ceh-build-from-plan` 1.0.0, `implement-from-plan`: phase by phase, test first, only what the
  phase names, the phase's check run after the last edit, and the evidence recorded in the plan.
  It stops after two fixes of the same failure, and writes a minimal plan first when none exists.
- `ceh-check-build-against-plan` 1.0.0, `check-build-against-plan`: every plan item marked Built,
  Gap, Deviation, Extra, Failing, or Cannot verify with quoted evidence, and each phase check
  rerun. Report-only unless asked to fix.
- `docs/IDEAS.md`: the Project rules generator idea, open, for `ceh-every-session`.

### Changed

- `ceh-workflow-builder` 1.3.5: `build-agentic-workflow` gets a Headless build path (a draft in the
  build directory plus closing questions, open rows never filled, nothing in `.claude/skills/`), a
  native-first rule for stage backends, and a trim from 472 to 376 lines that is not eval-verified.
  `interview-workflow-task` opens with an explicit repetition test. Descriptions, READMEs and
  `docs/ARCHITECTURE.md` speak of repeated product work and drop "building is interactive only".
- `ceh-workflow-runner` 1.0.3: `run-agentic-workflow` states that stages go to native capabilities
  and the runner keeps only approvals, world checks, resume state and the `FLOW STATUS:` line.
- `docs/IDEAS.md` holds every idea for the repo, in two tables: Done, and Open, on hold, and
  rejected. Fan-out and long runs is scoped into three parts and put on hold.
- `CLAUDE.md`: every addition or change must hold up against `docs/VISION.md`.
- `docs/VISION.md`: its opening says every addition or change must hold up against it, matching
  `CLAUDE.md`.
- `.claude/skills/add-plugin-component` step 1: check every new or changed component against
  `docs/VISION.md`, and record a rejection in `docs/IDEAS.md`.
- `branch-guard`, `bulk-read-guard`, and `bulk-read-bash-guard` send their full deny text for
  the first three denials in a session, then one line with the denial's number. Every deny names
  the setting that switches the guard off.
- `docs/IDEAS.md` lists each section as one table instead of one heading per entry.
- `docs/IDEAS.md` triage: Shared-block generator, Transcript reflection, Fact-forcing edit gate,
  Human-steps wizard, Parallel ticket frontier, and Deploy and canary are rejected for now. Sweep on
  Sonnet and Arena with a hidden rubric wait on `ceh-orchestration-lab`. Generated verify skill
  and Trigger-by-name eval cases are dropped for now. Verify gate waits on evidence, and Fan-out
  and long runs needs its scope settled in a follow-up session.
- `ceh-git-workflow:code-review` gains an opt-in Gate mode: two fresh reviewers on the Panel mode
  brief, Approve only when both approve, up to three rounds.
- `ceh-check-build-against-plan:check-build-against-plan` gains step 5, an opt-in gate on fix
  mode: two fresh reviewers recheck the fix, both must pass, the fixer touches only what they
  flagged, and the loop stops after three rounds.
- `ceh-build-planning`'s plan format moves from `write-build-plan`'s `references/` to the plugin's
  `references/`, now that two of its skills read it.
- `ceh-git-workflow:code-review` gains step 2: on a diff with more than about 200 changed lines in
  covered files, or on request, it dispatches the installed stack reviewers in parallel and merges
  their findings before the five-`[blocking]` cap.
- `ceh-git-workflow:branch` offers a Claude Code worktree for a long run while the user keeps
  working in the same checkout.
- `ceh-ui-design:design-ui` gains a Motion section: durations and easing by token, `transform`
  and `opacity` only, no layout shift, and reduced motion honoured by script-driven animation too.
- `validate.py`: `MAX_TOTAL_DESCRIPTION_LEN` rises by the eight new descriptions only.
- `ceh-git-workflow:code-review` gains step 3, the spec checked on its own axis and reported in its
  own Against the spec list, a Fowler-smell baseline for repos with no written standards, and an
  opt-in Panel mode that sends one brief to two or three models and ranks findings by agreement.
- `ceh-coding-conduct:refactor-repo` inventories shallow modules worth deepening, shows each with
  its before and after interface, and settles its design questions before any code.
- `ceh-ui-design:design-ui` gains a Variants board: throwaway HTML options that each differ on one
  design-pass answer, iterated on feedback, also usable for logic prototypes.
- `ceh-codebase-explanation:explain-until-understood` can keep an opt-in learning workspace per
  subject, opened in a later session with two self-test questions.
- `ceh-usability-audit:simulate-newcomer-first-run` ends a library, CLI, or API walk at the first
  real call, and counts a pasted code sample that needs fixing as a stall.
- `ceh-testing` README no longer lists exploratory testing as out of scope.
- `validate.py`: `MAX_TOTAL_DESCRIPTION_LEN` rises by the four new descriptions and the pitch-deck
  trigger added to `develop-business-plan`.
- `docs/VISION.md`: the lifecycle table replaces `ceh-plan-build-review` with one plugin per
  stage, principle 6 adds that a plugin covers one lifecycle stage, and "Where the repo does not
  match yet" lists the pending split.
- `docs/VISION.md`: the split has landed, so "Where the repo does not match yet" lists no gaps.
- The three stack bundles install all three plan plugins in place of `ceh-plan-build-review`, and
  `ceh-scenario-ideation` installs `ceh-build-planning` only, since ideation builds nothing yet.
- `ceh-business-plan` reads build plans from `docs/plans/`, and its `derived_from` names plans by
  path instead of `SKELETON` / `ITER_NN` stems.
- `ceh-git-workflow:code-review` points a whole-codebase plan check at
  `ceh-check-build-against-plan:check-build-against-plan`.
- `ceh-python-service`: `write-fastapi-endpoints` adds that another user's resource answers like a
  missing one, that `@lru_cache` settings need clearing in tests, and that a cookie set by several
  endpoints needs identical parameters. `write-postgresql-code` forbids `SELECT MAX(n) + 1`
  numbering.
- `ceh-web-frontend`: `write-react-vite-code` adds the StrictMode double effect and module-level
  config objects. Both it and `write-sveltekit-code` add three API-client traps: `credentials:
"include"`, one shared token refresh, and `fetch` streaming instead of `EventSource`.
- `docs/CROSS_REFERENCES.md`: one "Build plan format" entry replaces the four `plan-build-review`
  schema entries, and the review rules point at `check-build-against-plan`.

### Removed

- `ceh-plan-build-review` is archived to `archive/ceh-plan-build-review/`, with its four skills
  (`plan-fullstack-app`, `implement-from-plan`, `review-against-plan`,
  `apply-small-fix-to-version`) and its reference files. It leaves the marketplace.

---

## 2026-10-08

A third batch of 15 quick ideas from `docs/IDEAS.md` lands. Reviews get stricter about evidence: a
finding that quotes no code is reported as unverified, a brief cannot cap a finding's severity,
and a review can end in "cannot verify". The receiving side of a review gets its own skill,
`ceh-git-workflow:address-review-comments`, which checks each comment against the code before
acting on it. `ceh-every-session:write-questionnaire` hands open questions to someone outside the
session. `validate.py` now caps the total size of all descriptions with a ratchet, and checks for
invisible characters, personal absolute paths, and components missing from their plugin README.
The phase-boundary idea was dropped for now, because no observable event marks a phase's end.

`docs/IDEAS.md` now covers all five competitor analyses: superpowers, ECC, and mattpocock/skills
join gstack and pstack. Their "What we take" ideas add 40 adopt-now and 15 build entries, and 11
more merge into existing entries as extra sources. The testing ideas follow the analyses' reworked
judgment, which no longer discounts an idea for writing or running tests unasked: "Test-first by
default" is new, and "Opt-in verify gate" becomes "Verify gate". Every guard against dangerous
commands stays rejected, because Claude Code's built-in auto mode is good enough. No plugin version
changes.

The repo now has a stated vision in `docs/VISION.md`: guidance for autonomous agents, written for
agents first and humans second, across a product's life from idea to working software to the people
who should find it. The agent decides by default and asks a human only for facts no one else has
or before an irreversible or outward-facing action. Only an explicit human instruction overrides a
standard. The plugins that contradicted it now follow it. The coding contract and four
`ceh-testing` skills treat proving a change as part of the task, so the agent writes and runs the
tests that show its change works without being asked. Only slow or paid runs wait for a request.
The contract also lets the agent make local, reversible state changes, and a calling agent can
narrow a subagent's scope but no longer counts as user-level authority. The interview skills in
`ceh-business-plan`, `ceh-blog`, and `ceh-workflow-builder` keep adaptive questioning and gain a
path for a run with no human.

Names now say what a component does. `docs/VISION.md` gains principle 10, "Names say what they
do", because the name is the only part an agent always sees in full: descriptions get truncated in
the skill listing. The `ceh-` prefix is exempt as a namespace. Every name that failed the test is
renamed in the same PR. `ceh-core` becomes `ceh-every-session`, named for its admission rule.
`ceh-coding-agent` covered too much, so it splits into `ceh-coding-conduct` (the contract,
write-less-code, refactoring, the output style, the hooks) and the new `ceh-codebase-explanation`
(`explain-codebase`, `explain-until-understood`, `document-architecture`). Both renames break
existing installs: uninstall the old plugin and install the new one, or reinstall a scenario
bundle. Three skills, one agent, and one hook script get names that say what they do. `ceh-ag-ui`
keeps its name as a term of art.

The repo is audited against its vision, and every gap the audit found is closed in one PR, except
the coding hooks, which stay an open question. Skills that stopped for a human now ask once, up
front, with a recommended answer, and every one of them has a path for a run with no human:
`plan-fullstack-app` no longer asks one question per turn, the five business-plan specialists draft
and list their questions, and the plan-family, theme, cluster, and bump-level stops take a
conservative default and say so. Every skill and agent description now fits 600 characters, which
`validate.py` enforces, along with five rules it previously left to review. 61 rules gain the reason
behind them (principle 8). The Cytoscape skill drops its API and stylesheet references, which
restated the library docs. `docs/VISION.md` lists the gaps still open. Every standalone plugin
takes a PATCH bump. One deviation: the vision asks for its own changes in a separate PR, but the
author asked for this audit as one PR.

The two gaps the audit left open are closed. The coding hooks stay as they are, now with the
evidence for each recorded in the `ceh-coding-conduct` README. A softer "load it when you write
code" directive was tried, and the model never loaded the contract. The less-code ladder is a
standing standard, not a moment, so no description fires it, and loaded once it drifted out of
effect in long sessions. Only the three coding scenario bundles install the plugin, so sessions
that write no code elsewhere do not pay for the hooks. Because the hook delivers `write-less-code`,
its description drops its trigger phrases and becomes one line. `design-ui`'s `examples.md` drops
from 551 to 200 lines and keeps only the finishing-recipe markup, the part the core rules' prose
does not already carry.

Handoff becomes a general save and load. `ceh-every-session:hand-off-session` saves a session's
working state to a handoff file on request and loads one back in a later session, checking it
against the repo before resuming. `usage-limit-handoff` keeps its stop protocol and now saves
through it, so the two share one file format and one index. `explain-codebase` now explains
knowledge-base repos of Markdown or text notes as well as code: a component there is a topic area,
links replace calls, and reading paths replace request flows.

Five adopt-now ideas from `docs/IDEAS.md` land as rules in existing skills. The coding contract
lists the one-way doors it never auto-decides, requires a success claim to cite output from after
the last edit, and proves a repeated change complete with a command. `audit-interface` traces every
control, and `analyze-competitor` backs each coverage rating with evidence from both sides. Five
more tighten `ceh-git-workflow`: `code-review` checks scope drift first, names three more lenses,
caps blocking comments at five, and lists what it dismissed. `pull-request` re-checks the patch id
before merging, and `update-readme` hunts the claims a change made false. The last seven finish
the shortlist: a PR body that shows a before and after and names its risk, worktree cleanup after
a merge, a certainty ladder for refactors, a test-polluter bisect, a brief for every subagent, a
plain re-pitch for "wait, what?", and a validator check that the changelog carries every bump.

A second batch of quick ideas from `docs/IDEAS.md` lands as prose in existing skills. The testing
skills agree the test's seam first, call the code the way users do, see the test fail first, and
give each new test a `protects` / `fails_when` / `why_new` line that `audit-test-suite` also uses to
find tests to delete. `write-less-code` looks for an existing helper, package, or skill before
writing custom code, `refactor-repo` hunts information leakage, the React skill gains render-cost
rules, `draft-post` captures the author's voice once in a profile file that `edit-post` reads, and
`compare-competitors` scores each capability 1 to 5 against cited evidence, with no total. The
component templates name a strong model for any agent that gives a final verdict and cut sentences
that change nothing, and `add-plugin-component` describes a five-run micro-test for a doubtful
wording. Two ideas turned out to be built already (Finish-branch menu, On-page SEO metadata), and
"Mine the implied spec" is closed as covered by `verify-behavior-preserved`.

The three ideas that batch deferred are built. `ceh-codebase-explanation:trace-code-rationale`
answers "why is it like this" from git log, blame, PRs, and issues, citing every claim and naming
what the history does not record. It is a new skill because it reads history rather than the
current code. The new `ceh-session-to-skill` plugin turns a task just finished in the session into
a `SKILL.md`, built from the steps that worked, with no interview. It is its own plugin because its
use case, capturing a finished run, differs from the builder's interview-first one, and the two
descriptions now route to each other. `run-agentic-workflow` stops a retry whose failure matches
the attempt before, and fails a stage that edited its own gate's check.

### Plugin versions

| Plugin                     | Version |
| -------------------------- | ------- |
| `ceh-ag-ui`                | 1.1.1   |
| `ceh-blog`                 | 1.0.5   |
| `ceh-business-plan`        | 1.0.7   |
| `ceh-codebase-explanation` | 1.1.0   |
| `ceh-coding-agent`         | 1.0.2   |
| `ceh-coding-conduct`       | 2.0.5   |
| `ceh-competitor-analysis`  | 1.1.5   |
| `ceh-documentation`        | 1.0.4   |
| `ceh-every-session`        | 2.2.0   |
| `ceh-git-datastore`        | 1.0.3   |
| `ceh-git-workflow`         | 1.1.0   |
| `ceh-plan-build-review`    | 1.1.2   |
| `ceh-python-library`       | 1.0.2   |
| `ceh-python-service`       | 1.0.2   |
| `ceh-scenario-editorial`   | 1.1.0   |
| `ceh-scenario-ideation`    | 1.1.0   |
| `ceh-scenario-library`     | 1.1.0   |
| `ceh-scenario-service`     | 1.1.0   |
| `ceh-scenario-webapp`      | 1.1.0   |
| `ceh-seo`                  | 1.1.1   |
| `ceh-session-to-skill`     | 1.0.0   |
| `ceh-testing`              | 1.0.6   |
| `ceh-ui-design`            | 1.0.2   |
| `ceh-usability-audit`      | 1.1.2   |
| `ceh-web-frontend`         | 1.1.4   |
| `ceh-workflow-builder`     | 1.3.4   |
| `ceh-workflow-runner`      | 1.0.2   |

### Added

- `ceh-git-workflow:address-review-comments`: verify each review comment against the code, fix
  what holds, push back with quoted evidence on what does not, reply to every thread
- `ceh-every-session:write-questionnaire`: turn open questions into a self-contained file someone
  outside the session answers, then read the answers back
- `validate.py`: a ratchet on the total description size, and hygiene checks for invisible
  Unicode, personal absolute paths, and components missing from their plugin README
- `docs/VISION.md`: identity, vision, autonomy limits, override rule, product-lifecycle scope,
  goals, non-goals, nine principles, and their priority order when they conflict
- `ceh-business-plan:develop-business-plan`, `ceh-business-plan:find-product-market-fit`,
  `ceh-blog:draft-post`, `ceh-workflow-builder:interview-workflow-task`: a "No human to answer" path
  that drafts or records gaps, asks nothing, and ends with the questions a person must answer
- `docs/VISION.md` principle 10, "Names say what they do", with the `ceh-` prefix exempt as a
  namespace. `plugins/CLAUDE.md` links its naming rule to it and extends the rule to plugins and
  scripts
- `ceh-codebase-explanation` 1.0.0: `explain-codebase`, `explain-until-understood`, and
  `document-architecture`, moved unchanged from `ceh-coding-agent`. The service, library, and
  webapp scenario bundles install it, so a bundle install keeps every skill it had
- `validate.py`: a 600-character description cap, explicit `disable-model-invocation`,
  `user-invocable`, and `license` on every skill, `docs/PLUGIN_VERSIONS.md` matching every
  `plugin.json`, no `dependencies` in a marketplace entry, cross-cutting plugins depending only on
  cross-cutting plugins, and `user-invocable: false` on every skill a hook script names
- A "No human to answer" path in `sharpen-strategy`, `stress-test-unit-economics`,
  `plan-go-to-market`, `run-premortem`, and `set-operating-plan`, registered in
  `docs/CROSS_REFERENCES.md`, and a headless default in `refactor-repo`, `design-ui`, `release`,
  `repurpose-post`, and the plan-build-review skills
- `docs/IDEAS.md`: "Sweep on Sonnet, judge on Opus" and "Scope the coding hooks"
- `docs/ENVIRONMENT_VARIABLES.md`: `NODE_ENV`, read by `ceh-web-frontend`'s `run-e2e.sh`
- `ceh-every-session:hand-off-session`: save a session to a handoff file and load it back
- `agent-coding-contract`: a One-way doors list under Stop conditions, and a "Build the lever"
  core rule
- `audit-interface`: a trace of every control in step 3, with an observed no-op ranked as a finding
- `code-review`: a scope-drift step before the review order, a Dismissed list in the summary, and
  swallowed-error, stale-comment, and weak-type checks in the order
- `pull-request`: a patch-id re-check in the pre-merge gate, and a scope check in self-review
- `update-readme`: step 4, grep the README for every name the diff removed or renamed
- `pull-request`: a before/after line and a `## Risk` section (door and blast radius) in the PR
  body, and worktree cleanup after merge that asks before removing a worktree it did not create
- `verify-behavior-preserved`: step 0, name the fact the change's safety rests on and the rung of
  evidence reached
- `audit-test-suite`: bisecting for the test that pollutes another
- `agent-coding-contract`: what every subagent prompt must carry
- `explain-until-understood`: a plain re-pitch for "wait, what?" before the ladder
- `validate.py`: each plugin's newest `CHANGELOG.md` Plugin versions row matches `plugin.json`, and
  `docs/PLUGIN_VERSIONS.md` dates it to that section
- `design-test-cases`: a "Before the first test" section (name the seam, call the code the way
  users do, see it fail first, no tautological tests) and a value line per new test
- `test-a-bug-fix`: the reproducer calls the public entry point with a literal expected value, and
  the hand-over gives each test a value line
- `audit-test-suite`: step 1 lists a test with no nameable `fails_when` or a duplicate `why_new` as
  a deletion candidate
- `write-less-code`: one search for an existing helper, installed package, or skill before custom
  code
- `refactor-repo`: information leakage in the Phase 1 inventory
- `write-react-vite-code`: a Render cost section
- `draft-post`: a voice profile written once to `.agents_workspace/blog-voice.md`, which
  `edit-post` reads
- `compare-competitors`: a Scores table, 1 to 5 per capability with evidence in each cell and no
  total
- `add-plugin-component`: a five-run micro-test for a doubtful wording, on request only
- `ceh-codebase-explanation:trace-code-rationale`: why code is the way it is, from git history,
  every claim cited
- `ceh-session-to-skill` 1.0.0, with `turn-session-into-skill`: one `SKILL.md` from the steps that
  worked in this session, corrections as rules and per-run values as arguments
- `run-agentic-workflow`: a no-progress stop on retries and a gate-edited check before a green
  gate counts

### Changed

- `code-review`, `review-against-plan`, `audit-test-suite`: quote or suppress, so a finding with
  no quoted code is reported as unverified. `code-review` and `review-against-plan` also judge from
  the code, not the brief, and gain a Cannot verify outcome
- `write-less-code`: check at the boundary and trust inside, and count reader load, not lines.
  `refactor-repo`: migrate callers then delete, and redesign when patches pile up
- CEH Coding Conduct output style: a claim below the table names its evidence in the same sentence
- `plan-fullstack-app`, `interview-workflow-task`: triage first, and a spike gets no plan or spec
- `configure-python-service-env`, `configure-python-library-env`, `configure-bun-vite-env`: a
  pre-commit hook step that runs lint and format on every commit
- `write-fastapi-endpoints`: cursor pagination and deprecation headers. `write-postgresql-code`:
  keyset paging and zero-downtime DDL
- `edit-post` and the `ceh-documentation` docs standard: an AI-writing tells list
- `add-plugin-component`: strictness-graded eval cases, and an "It's working if" line in the
  template's README guidance. `model-audit`'s filter pass also cuts prose that changes no behavior
- `agent-coding-contract`: "No implicit actions" requires a success claim to cite output from a
  command run after the last edit it covers
- `analyze-competitor`: every coverage rating cites the competitor's path or URL and our component,
  and a Covered or Partial rating with no component of ours becomes a Gap
- `code-review`: at most five `[blocking]` comments, the rest deferred to a rework note
- `usage-limit-handoff` saves its artifact through `hand-off-session` instead of carrying its own
  file format and index steps
- `explain-codebase` handles knowledge bases: topic areas as components, links as connections,
  reading paths as key flows

- `plan-fullstack-app` asks once, up front, with a recommended answer for each question, instead of
  one question per turn. With no human, it takes the recommended answers and lists them as
  assumptions
- Plan-build-review skills take the highest plan family and the highest-numbered ITER when the
  user names none, and say which, instead of stopping to ask
- `audit-interface` and `simulate-newcomer-first-run`: the 5/5 gate is the done condition, not a
  user's confirmation
- `ceh-git-workflow:code-review` and `ceh-coding-conduct:shrink-diff` name the built-in
  `/code-review`, `/security-review`, and `/simplify` and state what they add
- Every skill and agent description over 600 characters is cut to fit, keeping its routing clauses
- 61 rules across 19 plugins gain the reason behind them
- `ceh-web-frontend:visualize-graph-cytoscape`: `references/api.md` and `references/style.md` are
  removed, and `references/layouts.md` keeps lifecycle, re-running, and extension choice only
- `docs/VISION.md`: the scope test admits teaching a person who must approve or supply a fact, the
  "Every step" row covers repeatable work, and "Where the repo does not match yet" lists the open
  gaps
- `docs/IDEAS.md`: "Rejection records" points at this file instead of a new `OUT_OF_SCOPE.md`, and
  two new-guard ideas wait on evidence
- `README.md` drops the work-in-progress banner, and `CLAUDE.md` no longer calls the migration in
  progress
- `audits/2026-10-06/SUMMARY.md` notes the plugin renames

- **Breaking:** `ceh-core` is renamed `ceh-every-session` (2.0.0), and `ceh-coding-agent` is
  renamed `ceh-coding-conduct` (2.0.0), with its output style now `CEH Coding Conduct`. Reinstall
  under the new names. Every scenario bundle depends on the new names
- Skills and agent renamed: `ceh-plan-build-review:patch-built-version` →
  `apply-small-fix-to-version`, `ceh-seo:pitch-project` → `write-project-listing-text`,
  `ceh-usability-audit:walk-first-run` → `simulate-newcomer-first-run`, agent `novice-walker` →
  `newcomer-simulator`. Hook script `less-code-payload.sh` → `inject-less-code-reminder.sh`
- `ceh-documentation`, `ceh-git-datastore`, `ceh-testing`, `ceh-web-frontend`: routing mentions
  follow the renames

- `ceh-coding-agent:agent-coding-contract`: the Validation policy makes proving the change and
  local, reversible state changes always allowed. Slow or paid runs and irreversible or
  outward-facing actions need a request or advance authorization from a human. A calling agent can
  narrow scope but cannot switch a standard off or grant authorization
- `ceh-testing:test-a-bug-fix`, `verify-behavior-preserved`, `close-test-risk-gaps`,
  `audit-test-suite`: "When tests were not requested" becomes "What waits for a request", so each
  skill applies unasked and only slow or paid runs wait. `docs/CROSS_REFERENCES.md` and
  `docs/TESTING_WORKFLOW.md` follow
- `ceh-coding-agent` output style: the closing Security / Performance / Architecture / Dependency
  flag line is gone. Such a risk is now a row in the summary table, with a status, since the table
  already lists everything found but not asked for
- `README.md`, `CLAUDE.md`, and the `marketplace.json` description state the agents-first identity
  and point at `docs/VISION.md`
- `docs/IDEAS.md`: every entry checked against the vision, with notes on Finish-branch menu, Claim
  needs fresh evidence, and Test-first by default
- `docs/IDEAS.md`: ideas from all five competitor analyses, with the destructive-shell half of the
  fact-forcing gate rejected alongside Destructive-command guard
- `docs/IDEAS.md`: "Strictness-graded evals" gains the tempt-never-order rule for competing prompts
  and the promote-to-hook rule, a new "Hook fixture tests" entry, and "Fact-forcing edit gate" now
  says nothing checks the stated facts

- `ceh-coding-conduct` README: a "Why each hook exists" section records the failure each hook
  answers (principle 7). `docs/IDEAS.md` drops "Scope the coding hooks" and `docs/VISION.md` drops
  both open gaps
- `ceh-coding-conduct:write-less-code`: the description is one line with no trigger phrases, and
  `plugins/CLAUDE.md` says why a session-long standard needs none
- `ceh-ui-design:design-ui`: `references/examples.md` keeps the command dock, humanized table (now
  with its eyebrow header), lifecycle stepper, monogram, and recessed input. The core-rule
  examples, the scroll-spy script, and the scrollbar CSS are cut, since `SKILL.md` already states
  them

- Agent and skill templates: a final-verdict agent gets the most capable model, and both templates
  ask for sentences that change nothing to be cut
- `docs/IDEAS.md`: statuses for the second batch, Finish-branch menu and On-page SEO metadata marked
  built with no edit, Mine the implied spec closed as covered, and decision notes on Rationale from
  history, Skill from this session, and Loop failure review
- `build-agentic-workflow`: the description routes a task just done in the session to
  `ceh-session-to-skill`, and drops the "evaluating an existing skill" and plugin-repo routes to
  stay within 600 characters
- `docs/VISION.md`, `CLAUDE.md`, `README.md`: `ceh-session-to-skill` in the scope, tier, and plugin
  tables

## 2026-10-07

A new `ceh-competitor-analysis` plugin turns a competitor study into a repeatable workflow. Each
competitor, either a code repo or a product, gets one evidence-anchored report. A comparison then
puts every competitor beside our own work. Repos are shallow-cloned and read as untrusted data, never
run. Every count names the command that measured it. Every "oh wow" mechanism points at the file or
URL it came from, and every incorporate row names where it would land in our work. The comparison is
a comparison only, with no adoption roadmap unless asked.

A new `docs/IDEAS.md` backlog tracks future plugin, skill, and validator ideas taken from the
competitor analyses, with the reason each rejected idea was dropped. No plugin version changes.

The `design-ui` skill now settles navigation for long single pages. Its layout table matched 5
destinations to both the sidebar and the top-nav archetype, so a 5-section report could go either
way. The sidebar now starts at 6, and the surface kind decides before the count. A new "In-page
contents" rule puts a content page's section links in the top bar first, and falls back to a sticky
contents rail only when the bar cannot carry them: 6 or more sections, `h3` links, a bar already
full of site pages, or an app shell.

`design-ui` then moved out of `ceh-web-frontend` into a new standalone `ceh-ui-design` plugin. The
skill was already framework-agnostic, and plugins that render HTML without a frontend stack can now
depend on it alone. `ceh-competitor-analysis` is the first: both of its skills now render their
report as a styled HTML page beside the Markdown on every run, Tidewater by default. `ceh-ag-ui`
depends on `ceh-ui-design` instead of `ceh-web-frontend`, since `design-ui` was the only thing it
called. `ceh-web-frontend` depends on `ceh-ui-design` by deliberate exception to the every-run rule,
so installing the web stack still installs the design skill. The skill's invocation name changes
from `ceh-web-frontend:design-ui` to `ceh-ui-design:design-ui`.

The competitor-analysis pages read like a book: long paragraphs and wide tables a new reader had to
work through before getting to the point. Each report now leads with the decision, a one-line summary
and verdict over an Adopt now / Build / Skip board, so a glance is enough. Detail moves into
expandable cards. A shared page template in the plugin fixes the layout for both skills, so every
run renders the same shape. `docs/IDEAS.md` gains the nine ideas from the pstack analysis.

`docs/IDEAS.md` then started over from the re-run gstack and pstack analyses. It now holds only
their "What we take" ideas, 11 to adopt now and 7 to build, each with where it would land. The two
gstack guard-hook ideas stay out, and so do the ideas both analyses chose to skip. The earlier
entries and the Dropped section are gone; git history keeps them. No plugin version changes.

Competitor reports now account for everything a competitor ships. `analyze-competitor` rates every
skill, agent, workflow, or feature against our work as covered, partial, gap, or N/A, in a new
coverage section, and every partial or gap item must land in Adopt now, Build, or Skip, with each
row naming the items it covers. The analyst agent lists every component instead of a sample and
gives a first-pass rating, and the page template gains the coverage tables. Re-run this way, the
gstack and pstack analyses took 101 partial or gap items, and `docs/IDEAS.md` now holds the
resulting 22 adopt-now and 24 build ideas. gstack's two guard-hook ideas are listed as rejected,
because Claude Code's built-in auto mode is good enough.

### Plugin versions

| Plugin                    | Version |
| ------------------------- | ------- |
| `ceh-ag-ui`               | 1.1.0   |
| `ceh-competitor-analysis` | 1.1.2   |
| `ceh-ui-design`           | 1.0.0   |
| `ceh-usability-audit`     | 1.0.1   |
| `ceh-web-frontend`        | 1.1.0   |

### Added

- `ceh-competitor-analysis` 1.0.0: `analyze-competitor` and `compare-competitors` skills, and the read-only `competitor-analyst` agent that reads one competitor in isolation
- `docs/IDEAS.md`: backlog of future plugin, skill, and validator ideas, with a Dropped section
- `ceh-web-frontend` 1.0.1: `design-ui` "In-page contents" rule, with a worked contents-rail example in `references/examples.md`
- `ceh-ui-design` 1.0.0: standalone plugin holding the `design-ui` skill, its Meridian and Tidewater themes, and `examples.md`
- `ceh-competitor-analysis` 1.1.0: `analyze-competitor` and `compare-competitors` render each report as an HTML page via `ceh-ui-design:design-ui`, with a shared theme under `themes/`

### Changed

- `ceh-web-frontend` 1.1.0: `design-ui` removed (now `ceh-ui-design:design-ui`); depends on `ceh-ui-design`
- `ceh-ag-ui` 1.1.0: depends on `ceh-ui-design` instead of `ceh-web-frontend`; invocations renamed to `ceh-ui-design:design-ui`
- `ceh-usability-audit` 1.0.1: hand-off pointers renamed to `ceh-ui-design:design-ui`
- `ceh-competitor-analysis` 1.1.1: reports lead with a summary, verdict, and Adopt now / Build / Skip board, and both skills render from a shared `references/report-page.html` template with expandable cards; mermaid diagrams dropped
- `docs/IDEAS.md`: nine ideas from the pstack competitor analysis
- `docs/IDEAS.md`: replaced with the 18 adopt-now and build ideas from the gstack and pstack analyses, minus gstack's two guard hooks
- `ceh-competitor-analysis` 1.1.2: `analyze-competitor` rates every competitor component for coverage and requires every partial or gap item in "What we take"; the analyst lists every component with a first-pass rating; the page template gains coverage tables
- `docs/IDEAS.md`: expanded to 22 adopt-now and 24 build ideas covering every partial or gap item from both analyses, with the two guard hooks marked rejected

### Fixed

- `ceh-web-frontend` 1.0.1: `design-ui` archetype table no longer matches 5 destinations to both app shell and top-nav

---

## 2026-10-06

The root `CLAUDE.md` loads in every session, so it now carries only what a session cannot derive
and what applies repo-wide. Plugin-authoring rules load only when working under `plugins/`. No
plugin version changes.

A repo-local `model-audit` skill keeps the plugins aligned with Claude's per-model prompting guides.
It detects guides a plugin has not been checked against, runs headless `/doctor prompt-audit` and
pinned-agent tuning passes, and hands the reports over as a draft PR. It never merges or runs evals.
No plugin version changes.

The first model audit ran on `ceh-core` against the Fable 5.1, Opus 5.5 and Sonnet 5.5 guide
chains and kept no edits, so only its `tuning.json` state is new. The audit scripts now locate
plugins by path instead of assuming `plugins/standalone/`. No plugin version changes.

A second model audit ran on `ceh-coding-agent` and `ceh-git-workflow` against the same guide
chains, and every edit it proposed was kept. These edits remove stale wording and references to
things that do not exist, and make the base branch in `shrink-diff` explicit.

A third model audit ran on `ceh-blog` and `ceh-documentation` against the same guide chains, and
every edit it proposed was kept. It resolves two contradictions: the Launch template's product-line
hook against the no-pitch Opening rule, and runbook page numbers left with gaps under
`write-project-docs`. It also drops rules that other steps already cover. The removed "No fluff
drafts" rule left one point not covered anywhere else, so `draft-post`'s Length line now says
length follows the content, not the source material.

The `model-audit` workflow's weekly schedule is off for now, so it runs only on manual dispatch.
When it runs, it applies the proposed edits by default, since they land on the `audit/<date>`
branch behind a draft PR. Claude Code now comes from the native installer, because the npm package
is deprecated. No plugin version changes.

### Plugin versions

| Plugin              | Version |
| ------------------- | ------- |
| `ceh-blog`          | 1.0.1   |
| `ceh-coding-agent`  | 1.0.1   |
| `ceh-documentation` | 1.0.1   |
| `ceh-git-workflow`  | 1.0.1   |

### Added

- `audits/2026-10-06/`: the `ceh-core`, `ceh-coding-agent` and `ceh-git-workflow` audit reports
- `plugins/standalone/ceh-core/.claude-plugin/tuning.json`: model-audit state recording the guides `ceh-core` was checked against
- `tuning.json` model-audit state for `ceh-coding-agent` and `ceh-git-workflow`
- `audits/2026-10-06/`: the `ceh-blog` and `ceh-documentation` audit reports, with `SUMMARY.md` covering all five plugins audited that day
- `tuning.json` model-audit state for `ceh-blog` and `ceh-documentation`
- `.claude/skills/model-audit/`: the `/model-audit` skill, with the stdlib detector and parallel audit runner in `scripts/`, the filter and tuning prompts in `references/`, and the config and guide state in `assets/`
- `.github/workflows/model-audit.yml`: a weekly (Friday 06:00 UTC) or manual run that opens the audit draft PR
- `tools/model-audit/README.md`, a pointer to the skill folder

### Changed

- Move the Skills and Frontmatter Conventions sections from `CLAUDE.md` to a new `plugins/CLAUDE.md`, leaving a pointer
- Drop the plugin domain table from `CLAUDE.md`, which repeated the root `README.md` Plugins table, and the `find`/`grep` one-liners from Commands
- The `add-plugin-component` new-plugin checklist no longer asks for a `CLAUDE.md` Plugins table row
- `model-audit` `SKILL.md` gains a next-steps section for the reviewer (keep or drop edits, accept or reject pinned tuning, mirror shared content, bump, changelog, re-run failures, merge), and the skill's `README.md` an Arguments table saying what each argument does and its default
- `model-audit`: `--plugins` takes plugin paths from the repo root instead of bare names, and the stale scan finds every plugin under `plugins/` except scenario bundles instead of globbing `plugins/standalone/`
- `ceh-coding-agent:shrink-diff` diffs against the base-branch argument (default `main`) instead of a hard-coded `main`
- `ceh-coding-agent:explain-until-understood` points its honesty rules at the output style, not the contract, and `explain-codebase` drops a closing line about a mapper that does not exist
- `ceh-coding-agent` README: the `agent-coding-contract` row no longer claims a role section, and `explain-codebase` is listed as on demand, matching its model-invocable frontmatter
- `ceh-git-workflow:update-readme` folds the no-marketing rule into "Match existing voice" as plain, technical prose
- `ceh-blog:draft-post` and `edit-post`: the Project / Launch hook opens on the moment that led to building it, with what it does and who it's for inside the first paragraph, instead of a one-line product pitch
- `ceh-blog:draft-post` drops "No fluff drafts" and folds its source-length point into the Length line. `edit-post` drops "Diagnose before editing", "One question after" and "Draft is already good", which its Output, Step 4 and diagnosis sections already state
- `ceh-documentation:write-guides-and-runbooks`: under `write-project-docs`, the runbook renumbers its remaining pages from `OP-01` instead of leaving gaps
- `ceh-documentation:write-project-docs` says delegated skills read the shared `docs-standard.md` instead of shipping their own copy
- `.github/workflows/model-audit.yml`: the weekly schedule is commented out, `apply` defaults to true (scheduled runs always apply), Claude Code installs via `claude.ai/install.sh` instead of npm, `actions/checkout` is `@v6`, and a concurrency group stops runs overlapping

## 2026-10-05

Releases are retired. The changelog now grows one dated section per PR-open day, written in the
PR itself, instead of one section per tagged release.

The workflow runner splits out of `ceh-workflow-builder` into its own `ceh-workflow-runner` plugin.
Building a flow and running it are different moments, and a session that only runs a flow has no
use for the interview and builder skills.

### Plugin versions

| Plugin                 | Version |
| ---------------------- | ------- |
| `ceh-workflow-builder` | 1.3.0   |
| `ceh-workflow-runner`  | 1.0.0   |

### Added

- Add the `ceh-workflow-runner` plugin at 1.0.0, holding `run-agentic-workflow` and its own word-for-word copy of `flow-config-schema.md`, registered in `docs/CROSS_REFERENCES.md`

### Changed

- Move `run-agentic-workflow` from `ceh-workflow-builder` to `ceh-workflow-runner`. Generated `<name>-flow` skills now call `ceh-workflow-runner:run-agentic-workflow` and name that plugin in their `compatibility`. Flows emitted before this change still call `ceh-workflow-builder:run-agentic-workflow` and must have that line updated

- Replace the release process with per-PR changelog entries grouped by the date the PR is opened, in `CLAUDE.md`, the `add-plugin-component` checklist, `README.md`, and `docs/PLUGIN_VERSIONS.md`
- Rename the old release sections `v2026.10.02` and `v2026.10.03` to the date format, here and in `docs/PLUGIN_VERSIONS.md`
- Document in `CLAUDE.md` how landing a branch in this repo differs from `ceh-git-workflow:pull-request`
- `CLAUDE.md` now tells an agent to refuse any release request with a warning that releases are not used in this repo

## 2026-10-03

Built workflows become runnable without a human driving them. `ceh-workflow-builder` now emits a
`flow.yaml` config that a new generic runner executes, interactively or headless with `claude -p`,
with Claude Code dynamic workflows as an optional backend for big fan-out stages. The design rests
on empirical tests of how dynamic workflows behave headless, now recorded in the plugin's docs.

### Plugin versions

| Plugin                 | Version |
| ---------------------- | ------- |
| `ceh-workflow-builder` | 1.2.0   |

### Added

- Add the `ceh-workflow-builder:run-agentic-workflow` skill, a generic runner that executes a built workflow from its `flow.yaml`, interactively or headless (`claude -p`): stages, approvals between stages, gates, run state and resume, ending on a `FLOW STATUS:` line. Stages run as a skill, agent, script, inline instructions, or a saved Claude Code dynamic workflow, which is never assumed: a missing Workflow tool runs the declared fallback or fails, never imitates
- Add `ceh-workflow-builder/references/flow-config-schema.md`, the `flow.yaml` contract shared by the builder and the runner
- Add `ceh-workflow-builder/docs/ARCHITECTURE.md` and `docs/TEST_RESULTS.md`: how build and run fit together, and the empirical dynamic-workflow tests (F1-F14) the design rests on, with the full re-run procedure

### Changed

- `ceh-workflow-builder:build-agentic-workflow` emits a `flow.yaml` plus a thin trigger skill and an invocation guide instead of a pipeline-table flow skill, and its emitted `SKILL.md` templates move to the skill's `references/emitted-templates.md` to keep it under 500 lines
- Align the three `ceh-workflow-builder` skills with the component template: sentence-case titles, "Load this skill when" descriptions, and the runner's sections in template order

## 2026-10-02

First release of this repo. It completes the migration from agent-skills: 16 standalone plugins
restructured onto one `SKILL.md` and agent template, five scenario bundles as the install entry
point, the `validate.py` CI gate, and the maintainer docs. Plugins keep the version they migrated
at, so nothing is bumped. Releases are named by date from here on, and `docs/PLUGIN_VERSIONS.md`
maps each plugin version to the release that last changed it.

### Plugin versions

| Plugin                   | Version |
| ------------------------ | ------- |
| `ceh-ag-ui`              | 1.0.0   |
| `ceh-blog`               | 1.0.0   |
| `ceh-business-plan`      | 1.0.5   |
| `ceh-coding-agent`       | 1.0.0   |
| `ceh-core`               | 1.0.0   |
| `ceh-documentation`      | 1.0.0   |
| `ceh-git-datastore`      | 1.0.1   |
| `ceh-git-workflow`       | 1.0.0   |
| `ceh-plan-build-review`  | 1.0.0   |
| `ceh-python-library`     | 1.0.0   |
| `ceh-python-service`     | 1.0.0   |
| `ceh-seo`                | 1.0.0   |
| `ceh-testing`            | 1.0.0   |
| `ceh-usability-audit`    | 1.0.0   |
| `ceh-web-frontend`       | 1.0.0   |
| `ceh-workflow-builder`   | 1.1.2   |
| `ceh-scenario-editorial` | 1.0.0   |
| `ceh-scenario-ideation`  | 1.0.0   |
| `ceh-scenario-library`   | 1.0.0   |
| `ceh-scenario-service`   | 1.0.0   |
| `ceh-scenario-webapp`    | 1.0.0   |

### Added

- Add `docs/PLUGIN_VERSIONS.md`, the version of every plugin as of the latest release and the release that last changed it

- Add five scenario bundles as the install entry point, each a manifest and README with no skills, agents, or hooks: `ceh-scenario-service`, `ceh-scenario-library`, `ceh-scenario-webapp`, `ceh-scenario-ideation`, and `ceh-scenario-editorial`, all at `1.0.0`. They replace the agent-skills `-iterate` bundles under shorter names. `ceh-scenario-core`, the `-greenfield` bundles, and `ceh-scenario-agent-tooling` are not migrated: the stack bundles list the cross-cutting plugins directly, `ceh-scenario-ideation` covers the greenfield delta, and `ceh-evaluation` is archived
- Migrate `tools/skills-sync` from agent-skills unchanged apart from a stale decision-log pointer in its README: the py, sh, ps1 and html implementations that copy skills into a project's `.claude/skills/`. `tools/skill-evals` stays behind, since the Evaluation section of `CLAUDE.md` replaces it with Anthropic's own eval tools
- Add the `add-plugin-component` repo skill with `SKILL.md` and agent templates as the base for every new component
- Add `tools/validate-plugins/validate.py` and its CI workflow, ported from agent-skills, now also rejecting undocumented frontmatter keys, malformed names, and leftover template guidance
- Add the empty `ceh-claude-code-library` marketplace and skeleton `CLAUDE.md`, `docs/CROSS_REFERENCES.md`, and `docs/PLUGIN_DEPENDENCIES.md` for migrated plugins to land into
- Add a pre-commit config that formats Python with ruff, Markdown and JSON with the official npm prettier, and shell scripts with shfmt
- Migrate `ceh-git-workflow` from agent-skills at `1.0.0`: its 11 skills (branch, commit, open-pr, merge, hotfix, release, code-review, dependency-management, update-changelog, merge-flow, release-flow) restructured onto the repo `SKILL.md` template, plus `scripts/check-semver.py` and its cross-reference entries
- Migrate `ceh-coding-agent` from agent-skills at `1.0.0`: 8 skills, 2 agents, hooks, scripts, and the output style, reshaped to this repo's templates with content unchanged. The `delegate-bulk-reads` eval suite stays in agent-skills
- Add the cross-cutting `ceh-core` plugin for standards that hold however Claude Code is used, seeded with `usage-limit-handoff`, `delegate-bulk-reads`, the `bulk-reader` agent, and their hooks moved out of `ceh-coding-agent`
- Add a `ceh-git-workflow` PreToolUse branch guard that denies file edits on the default branch until a feature branch exists, disabled with `CEH_BRANCH_GUARD=off`
- Add `docs/ENVIRONMENT_VARIABLES.md`, the index of every environment variable any plugin reads
- Migrate `ceh-architecture` from agent-skills at `1.0.0` as a standalone use-case workflow plugin: `document-architecture` and `domain-modeling`, both invocable by name. The SessionStart invariants hook is not migrated: it injected layering rules into every session and pushed unrequested `ARCHITECTURE.md` upkeep, and the skill descriptions already carry the triggers. The README no longer points at plugins that have not migrated
- Migrate `ceh-seo` from agent-skills at `1.0.0` as a standalone use-case workflow plugin: `make-page-crawlable` (was `web-discoverability`), `pitch-project` (was `text-discoverability`), and `write-llms-txt`. The `write-llms-txt` eval suite stays in agent-skills, and references to plugins that have not migrated become prose
- Migrate `ceh-blog` from agent-skills at `1.0.0` as a standalone use-case workflow plugin: `draft-post`, `edit-post`, and `repurpose-post`. `blog-interviewer` and `blog-writer` merge into `draft-post`, which interviews when the material is thin and drafts directly when it is rich, so the shared Voice and post-type blocks exist once
- Add the shared blog voice, blog post-type structures, and GEO writing rules to `docs/CROSS_REFERENCES.md`
- Migrate `ceh-testing` from agent-skills at `1.0.0` as a cross-cutting plugin: `test-a-bug-fix`, `design-test-cases`, `audit-test-suite`, `verify-behavior-preserved`, and `close-test-risk-gaps`. The `test-suite-auditor` agent is not migrated: `audit-test-suite` gains a report-only mode for delegated runs, with the mutation-run cap. The routing doc `docs/TESTING_WORKFLOW.md` stays in agent-skills
- Migrate `ceh-python-service` from agent-skills at `1.0.0` as a stack plugin: seven skills renamed to say what they apply to (`write-fastapi-endpoints`, `write-postgresql-code`, `configure-python-service-env`, `write-pytest-service-tests`, `add-observability`, `secure-service-code`, `model-domain`). `write-postgresql-code` merges the asyncpg, PostgreSQL schema, and Alembic skills, which fire together, the unit, integration, and system tester agents, and the test-runner scripts
- Migrate `ceh-python-library` from agent-skills at `1.0.0` as a stack plugin: `publish-python-library` (packaging, public API, and semver in one skill), `configure-python-library-env`, and `write-pytest-library-tests`
- Migrate `ceh-web-frontend` from agent-skills at `1.0.0` as a stack plugin: `configure-bun-vite-env`, `write-sveltekit-code`, `write-react-vite-code`, `write-vitest-playwright-tests`, `make-ui-accessible`, `design-ui` with its Meridian and Tidewater themes, `visualize-graph-cytoscape` with its references, template, and converter script, the TypeScript tester agents, and the test-runner scripts
- Add the shared Python environment and testing foundations, the design-test-cases hand-off, the asyncpg pool call, the layer boundaries, and the audit findings report to `docs/CROSS_REFERENCES.md`, the three `ceh-testing` dependency edges to `docs/PLUGIN_DEPENDENCIES.md`, and the test-target variables to `docs/ENVIRONMENT_VARIABLES.md`
- Migrate `ceh-plan-build-review` from agent-skills at `1.0.0` as a use-case workflow plugin: `plan-fullstack-app-iteratively`, `plan-fullstack-app-to-mvp`, `implement-from-plan`, `review-against-plan`, and `patch-built-version`, restructured onto the repo `SKILL.md` template with every rule kept. `plan-schema.md`, `section-specs.md`, `audit-checklist.md`, and `implementation-gotchas.md` live once in the plugin-level `references/` folder and are read through `${CLAUDE_PLUGIN_ROOT}`. `plan-schema.md` is the single source for file naming, version families, and frontmatter, and the implement, patch, and review skills read the gotchas as well as the planners
- Migrate `ceh-documentation` from agent-skills at `1.0.0` as a use-case workflow plugin: `write-project-docs`, `write-guides-and-runbooks`, `write-api-reference`, `write-concept-docs`, and `write-examples`, restructured onto the repo `SKILL.md` template with every rule kept. `docs-standard.md` lives once in the plugin-level `references/` folder, read by the four writing skills, and references to plugins that have not migrated become prose
- Add the §02 Mermaid diagram requirement, the patch ITER frontmatter, and the planners' "Plan families and versions" prose to `docs/CROSS_REFERENCES.md`
- Migrate `ceh-ag-ui` from agent-skills at `1.0.0` as a stack plugin: `build-ag-ui`, `add-canvas-component`, `build-ag-ui-agent`, `add-live-state-panel`, and `add-human-approval`, restructured onto the repo `SKILL.md` template with every rule kept, plus the bundled canvas template and agent server unchanged. It depends on `ceh-web-frontend` for the `design-ui` theme, and its worked examples land in a new root `examples/ceh-ag-ui/`
- Migrate `ceh-usability-audit` from agent-skills at `1.0.0` as a use-case workflow plugin: `walk-first-run` (was `first-run-walkthrough`), `audit-interface`, `audit-error-messages`, `write-plain-language` (was `plain-language-pass`), and the `novice-walker` agent, restructured onto the repo templates with every rule kept. Hand-offs point at this repo's skill names. The persona table and severity scale that `walk-first-run` and `audit-interface` each carried now live once in the plugin-level `references/personas-and-severity.md`, both skills run at `high` effort instead of `xhigh`, and `audit-interface` gains a `compatibility` field
- Migrate `ceh-business-plan` (`develop-business-plan`), `ceh-git-datastore` (`build-git-datastore`, `migrate-git-datastore`), and `ceh-workflow-builder` (`build-agentic-workflow`, `interview-workflow-task`) from agent-skills as use-case workflow plugins, each moved as is at its agent-skills version with the content unchanged. Their `repository` URL now points at this repo, and references to `ceh-evaluation` and `ceh-orchestration`, which stay archived, are dropped. `ceh-git-datastore` points at `ceh-python-service:write-postgresql-code` and `ceh-coding-agent:document-architecture`, where the skills it named now live
- Document in `CLAUDE.md` that evals use Anthropic's tools: `skill-creator` for one skill and `claude plugin eval` for a whole plugin, and that the archived `ceh-evaluation` plugin is not to be run. `plugins/*/evals/results/` is git-ignored
- Migrate `ceh-readme` from agent-skills into `ceh-git-workflow` as the `update-readme` skill instead of a one-skill plugin: it fires at the same moment as `update-changelog`, reads the same git diff, and the `pull-request` and `release` sequences already carry a README step, which now names it. Every "the ceh-readme plugin" pointer in `ceh-documentation`, `ceh-seo`, and `ceh-usability-audit` becomes `ceh-git-workflow:update-readme`
- Add the usability persona set and severity scale and the AG-UI styling lock to `docs/CROSS_REFERENCES.md`, and the `ceh-ag-ui` → `ceh-web-frontend` edge to `docs/PLUGIN_DEPENDENCIES.md`
- Add six model-only specialist skills to `ceh-business-plan`, for use once the PMF gate passes: `review-business-plan` (report-only board review on seven lenses), `sharpen-strategy`, `stress-test-unit-economics`, `plan-go-to-market`, `run-premortem`, and `set-operating-plan`. Each writes one subsection into the existing 13-section schema, and `develop-business-plan` stays the only slash command and names the specialist to run next. `business-plan-schema.md` moves to the plugin `references/` because seven skills now share it. No version bump, since no release tag exists yet
- Add a `SubagentStart` hook to `ceh-coding-agent` that gives subagents the contract directive and the less-code digest, which `SessionStart` and `UserPromptSubmit` never deliver inside a subagent. Agents without the Skill tool are pointed at the contract file, and the read-only `Explore`, `Plan` and `bulk-reader` agents are skipped
- Migrate the documentation that still applies from agent-skills: `docs/TESTING_WORKFLOW.md` rewritten for this repo's skill and agent names, five `docs/CROSS_REFERENCES.md` entries (auto-merge probe, blog location and destination, blog repurpose handoff, git datastore hard stops, the workflow spec's nine questions) and its update protocol, the dependency behavior, edge rules, non-edge references, and bundle membership in `docs/PLUGIN_DEPENDENCIES.md`, and the README prerequisites, plugin-agent limitations, and verify step

### Changed

- Split `plugins/` into `plugins/scenarios/` for the five `ceh-scenario-*` bundles and `plugins/standalone/` for every other plugin. Plugin names and versions are unchanged. `validate.py` now globs `plugins/*/ceh-*`, and `marketplace.json`, the README install paths, the docs, and the `add-plugin-component` skill point at the new locations. Local `--plugin-dir` or settings paths that use `plugins/ceh-*` need updating
- Merge `ceh-python-service` from seven skills to four: `add-observability`, `secure-service-code` and `model-domain` fire once per project, so their rules now ride on skills that load on most service work. `write-fastapi-endpoints` absorbs logging, metrics, `/health`, correlation IDs, CORS, rate limiting, input validation and layer boundaries, `write-postgresql-code` absorbs entity IDs, status enums and immutability rules, and `configure-python-service-env` absorbs secrets management. The unused `argon2-cffi` and `pyjwt` requirement, the TypeScript enum snippet and the `ceh-scaffolding` pointer are dropped, and the HTTP status table is cut to the service's own choices
- Clean up `ceh-web-frontend` without merging any skill: `write-sveltekit-code` standardizes on Svelte 5 runes (shared state in `.svelte.ts` modules instead of `writable` / `derived` stores), `make-ui-accessible` and `write-vitest-playwright-tests` serve React as well as Svelte, source-application names (challenges, reasoning panel) become generic items, and `configure-bun-vite-env` drops the naming table, import-order block and Prettier config that the tooling already enforces. The API client and `ApiRequestError` duplication between the React and SvelteKit skills is registered in `docs/CROSS_REFERENCES.md`
- Retire `ceh-architecture` before its first release: `document-architecture` moves into `ceh-coding-agent` beside `explain-codebase`, and `domain-modeling` moves into `ceh-python-service` as `model-domain`. The stack plugins ship no SessionStart invariants hooks, matching the `ceh-architecture` decision, so their skills load from descriptions alone
- Route component authoring through `skill-creator` (no eval loop unless asked) and the plugin-dev agent, hook, and MCP skills; configure plugins through environment variables only
- Point the `ceh-coding-agent` less-code hook at the full `write-less-code` skill so it loads before implementing, and gate the skill's runnable-check rule on tests being in scope
- Consolidate `ceh-git-workflow` from 11 skills to 6: `open-pr`, `merge` and `merge-flow` become `pull-request`, and `release-flow` and `hotfix` fold into `release`, so a compound request loads two skills instead of one per step
- Make `ceh-git-workflow` stack-agnostic: Python and TypeScript checks, the coverage table, and `ARCHITECTURE.md` references are replaced by stack-neutral rules
- State `disable-model-invocation`, `user-invocable`, and `license` in every skill's frontmatter and in the `SKILL.md` template; `agent-coding-contract`, `write-less-code`, `usage-limit-handoff`, `delegate-bulk-reads` and `branch` become model-only, so they no longer appear as slash commands
- Trim the descriptions of the hook-loaded skills `agent-coding-contract`, `usage-limit-handoff` and `delegate-bulk-reads` to one line each, since their hooks name them explicitly and no trigger phrases are needed
- Make `ceh-business-plan:develop-business-plan` a thin entry point that finds the plan, routes to the specialist that owns the moment, and resets `status: draft` when the gate drops below 8/8. The product-market-fit loop moves whole into a new model-only skill, `find-product-market-fit`, and every specialist description shrinks to one sentence because only the entry point triggers. The duplicated `plan-schema.md` is deleted in favour of three inlined rules
- Tighten the `ceh-business-plan` schema and specialists: `business-plan-schema.md` fixes the heading form (`## §NN Title`) and the file location, lists every section each skill writes, and gains a worked example. Each specialist now writes one named subsection before it asks anything, asks at most three questions (five for `sharpen-strategy`), and tags any line it writes outside its subsection. `sharpen-strategy` confirms before removing refused items, `plan-go-to-market` stops on a missing acquisition ceiling, and `review-business-plan` derives its verdict from the scores
- Name repo releases by release date (`vYYYY.MM.DD`) instead of a semantic version. Plugin versions stay semantic
- Require `model` in every agent's frontmatter, enforced by `validate.py`

- Name skills with a verb phrase and agents with a noun, with two exemptions (model-only standards, established terms of art). The rule lives in `CLAUDE.md` and the `SKILL.md` template guidance

- Make four `ceh-testing` skills (`test-a-bug-fix`, `verify-behavior-preserved`, `close-test-risk-gaps`, `audit-test-suite`) write no tests and run no suite unless the user asked for them: each names the test or check it would run and what stays unverified. This follows the agent coding contract without depending on it. The shared section is registered in `docs/CROSS_REFERENCES.md`
- Reword the coverage percentages in `write-pytest-service-tests`, `write-pytest-library-tests`, `write-vitest-playwright-tests` and the `ceh-web-frontend` README as a floor for finding blind spots, not a goal, so they no longer contradict `design-test-cases` and `audit-test-suite`. The `vitest-unit-tester` agent reports the regions still untested instead of a coverage delta
- Warn in `write-sveltekit-code` that shared-state modules are browser-only, because module-level state is shared across every user's request during server rendering, and guard `setSession` with `browser`
- Align the skills and agents of `ceh-testing`, `ceh-python-service`, `ceh-python-library` and `ceh-web-frontend` with the `SKILL.md` and agent templates: every skill gets an intro, `## Procedure`, and `## Rules` (existing topic sections nested under it), with `## Output`, `## Stop conditions`, and `## Hands off to` where the content already existed. The three `design-test-cases` hand-offs move to `## Hands off to`, and every tester agent gains a `Report` step, an output example, and the "not run" rule
- Align `build-agentic-workflow`, `interview-workflow-task`, `build-git-datastore` and `migrate-git-datastore` with the `SKILL.md` template: they gain the always-present `disable-model-invocation`, `user-invocable` and `license` keys, and their sections move under `## Procedure`, `## Rules`, `## Output`, `## Stop conditions` and `## Hands off to` with the existing topic sections nested as H3. `bulk-reader` gains the "cannot ask questions" rule. Body text is otherwise unchanged
- Make the 11 stack-standards skills of `ceh-python-service`, `ceh-python-library` and `ceh-web-frontend` model-only (all but `publish-python-library`, `design-ui` and `visualize-graph-cytoscape`), since they are rule sets applied while writing code, and give the three `ceh-seo` skills their slash commands back, since each is a task asked for by name
- Drop the proactive triggers from `walk-first-run` ("before shipping a README or sign-up flow") and `explain-codebase` ("before making the first change to an unfamiliar codebase"), so neither starts a costly walk nobody asked for
- Merge `plan-fullstack-app-iteratively` and `plan-fullstack-app-to-mvp` into `plan-fullstack-app`, with a mode table (next release, whole build to MVP) in place of two skills that pointed at each other. The complexity gate's STOP now offers next-release mode instead of naming another skill, and the rules that conflict between the modes are scoped to their own mode. The shared plan-file locate step moves into `plan-schema.md` under "Locating plan files", and `implement-from-plan`, `review-against-plan` and `patch-built-version` cite it. The slash commands `/ceh-plan-build-review:plan-fullstack-app-iteratively` and `...-to-mvp` no longer exist

### Fixed

- Fix a renumbered Sequencing line in `verify-behavior-preserved` that read "3. ... 2. refactor → 5."
- Fix the `ceh-python-service` description in `CLAUDE.md`, `README.md`, `plugin.json` and `marketplace.json`, which still advertised observability, security and domain modeling after those skills were removed
- Fix `CLAUDE.md` statements that had drifted from the repo: the bundled-files exemption now covers `ceh-ag-ui` and `ceh-git-datastore`, the version-bump rule says CI only checks that `plugin.json` and `marketplace.json` match, the pre-commit note names the install step and all three formatters, and the always-present frontmatter keys are stated
- Add `CEH_WORKFLOW_BUILD_DIR` and `CEH_WORKFLOW_RUN_DIR` to `docs/ENVIRONMENT_VARIABLES.md`

### Removed

- Archive the `repo-tree-mapper` agent and its `walk-repo.sh` script to `archive/ceh-coding-agent/`
- Archive `ceh-git-workflow:dependency-management` to `archive/ceh-git-workflow/` until a stack plugin can own it
- Archive the eight agent-skills plugins that have not migrated, whole and unchanged, under `archive/`: `ceh-advisor`, `ceh-evaluation`, `ceh-fabled`, `ceh-lessons-learned`, `ceh-ops`, `ceh-orchestration`, `ceh-scaffolding`, and `ceh-summarize-chat`. They are unpublished and not validated
