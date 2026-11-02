---
schema: plan/v1
title: A skill that writes a repo's vision and strategy docs
status: built
created: 2026-11-02
---

## Goal

An agent asked to write a repo's vision and strategy gets two files, for its caller to commit, that
settle later decisions, instead of a mission statement nobody reads. The flow that matters most: the owner of a
repo says "write the vision and strategy docs", the agent drafts both from what the repo shows,
interviews the owner only on what the repo cannot show, proves each doc settles real decisions, and
points the repo's `CLAUDE.md` at them so later sessions read them.

## Scope

**In:**

- A new plugin `ceh-vision-and-strategy` holding one skill, `write-vision-and-strategy`, which writes
  or revises `VISION.md` and `STRATEGY.md`, in any repo, code or not.
- A versioned template and schema for each doc.
- An adopted vision or strategy is revised in place, keeping the owner's wording, never regenerated.
- A run with no human ends with `status: draft` docs, every gap marked, and the questions listed.
- `ceh-build-planning:write-build-plan` and `review-build-plan` read an existing vision and strategy,
  so the docs are a handoff file and not an island.
- Registration: catalog, plugin README, manifests, root README, `CLAUDE.md` tier table,
  `docs/GETTING_STARTED.md`, `docs/STRATEGY.md` Shape row and spine, changelog, plugin versions.
- `docs/VISION.md` Shape row, in its own PR as that file requires.

**Out:**

- A place in `ceh-business-plan`: that plugin's material is confidential and stays local, and a repo
  that is a library or a knowledge base has a direction but no business plan to enter through.
- A place in `ceh-build-planning`: a build plan decides how and recurs per feature, and a vision
  decides what and why once per repo. Vision principle 6 keeps one stage per plugin, and the docs
  belong to Shape while build planning belongs to Build, per `docs/STRATEGY.md`.
- A place in `ceh-documentation`: that plugin writes `docs/` for users of the product, and these docs
  are for the people and agents building it.
- A review skill for the docs: `ceh-every-session:stress-test-plan` already questions a strategy.
- A hook or validator that enforces the docs: no failure has been measured (vision principle 7).
- An HTML version or diagrams: nothing reads them, add when asked.
- Rewriting this repo's own `docs/VISION.md` and `docs/STRATEGY.md` to the new schemas: they work,
  and the skill handles an existing file without its `schema:` line.
- Paid evals: `decision-evaluation.md` runs them only when asked.
- A stage marker in `ceh-every-session:whats-next`: it adds a third plugin bump with nothing measured.
  Add when a run shows `whats-next` missing the docs.

## Design

**Scope test.** The skill passes the vision's test because it helps an agent ship a product: goal 2
("agents act as intended") needs written intent an agent can read, and an agent without it improvises
direction or stops to ask. Under `docs/STRATEGY.md` How work is chosen, the break on the spine is
"a moment where the agent improvised because no skill covered it": this repo's own vision and
strategy were written in agent sessions with no skill to follow, and no skill covers the moment in
another repo. This work is ahead of that section's listed order because the owner asked for it.

**Skill name.** `write-vision-and-strategy`, a verb phrase naming both docs. Plugin
`ceh-vision-and-strategy`, tier use-case workflow, stage Shape. `disable-model-invocation: false`,
`user-invocable: true`, `license: Apache-2.0`, no `argument-hint` because it takes no argument. No
`dependencies`. One skill covers both docs because a strategy holds up against its vision, so writing
them apart means reading the same repo twice.

**Description.** "Load this skill when a repo's direction must be written down to settle later
decisions: VISION.md and STRATEGY.md, drafted from the repo, then confirmed with its owner. Trigger
on "write the vision doc", "create a strategy doc". Not for a business plan (use
ceh-business-plan:develop-business-plan)."

**`plugin.json`.** Description "CEH vision and strategy: write a repo's VISION.md and STRATEGY.md, so
agents and people can settle later decisions from them, drafted from what the repo shows and confirmed
with its owner." Keywords `agent`, `vision`, `strategy`, `product-direction`.

**README signal.** It's working if the first run writes both files with `status: draft` and `[assumed]`
marks before it asks anything.

**Skill Output and Hands off.** `## Output` cites both templates and schemas. `## Hands off to` names
`ceh-every-session:stress-test-plan` to question the docs, and `ceh-build-planning:write-build-plan`
for the first plan, both bare names as conditional handoffs. The skill writes files only, and its
caller commits them, like `write-build-plan`.

**Location.** `product/VISION.md` and `product/STRATEGY.md`, committed, per
`decision-artifact-locations.md`: other stages and sessions read them and they are not for users of
the product. An existing file at `VISION.md`, `docs/VISION.md`, or a path the repo's `CLAUDE.md`
names stays where it is, and the same holds for `STRATEGY.md`.

**Files, all under `plugins/standalone/ceh-vision-and-strategy/skills/write-vision-and-strategy/`,**
per `decision-output-templates.md`:

- `SKILL.md`
- `assets/vision.template.md`, opening with `schema: vision/v1`
- `assets/strategy.template.md`, opening with `schema: strategy/v1`
- `references/vision-schema.md`, `references/strategy-schema.md`

**Doc frontmatter.** `schema`, `status` (`draft` while any `[assumed]` remains or the owner has not
confirmed, `adopted` once confirmed), `updated` (date).

**Vision sections, in order:** Identity (it is, it is not), Vision (the end state), Scope (with a
one-sentence test question), Goals (each checkable), Non-goals (each something tempting, with its
reason), Principles (each with its reason and a closing **Ask:** question), When principles conflict
(an order, with one worked example), Where the repo does not match yet, Changing this file.

**Strategy sections, in order:** The concept (the one idea that joins the parts), The parts (what
each part does and what passes between them), How work is chosen (the rule that accepts or refuses
work, then the likely order next), Measuring progress, What not to do (rejected approaches with
reasons), Where the repo does not match yet, Open questions, Changing this file.

**Procedure, as the skill states it:**

1. Find what exists: both docs at the Location paths. An existing doc is revised: change only what
   the request or a finding needs, and keep the owner's wording. A request for one doc when the other
   is missing drafts both, because the two hold up against each other. An existing doc with no
   `schema:` line gets the template's frontmatter, `adopted` when the repo's `CLAUDE.md` or the owner
   already treats it as binding, otherwise `draft`. Keep its extra sections and its order, and add a
   missing section only when a later step writes to it.
2. Read what the repo shows: README, `CLAUDE.md`, `.claude/rules/`, plans, `ARCHITECTURE.md`, ideas
   or roadmap files, the changelog, recent `git log`, and
   `.agents_workspace/product/business/BUSINESS_PLAN.md` when present. A repo of plain documents is
   read the same way. Do what the repo does, not what it claims, count as evidence when they differ.
3. Draft each doc that does not exist now, with `status: draft`, because a draft on disk survives an
   interrupted session. Mark every statement of intent no source backs with `[assumed]`. An adopted
   doc stays `adopted` and never gets an `[assumed]`: a change the owner has not confirmed goes to
   step 4 as a question, and is written only once they confirm it.
4. Interview the owner, one question per turn, each offering the draft's hypothesis to correct, in
   this order of worth: who it is for, the end state, what it refuses, which principle wins a
   conflict. Fold each answer in and remove its `[assumed]`. Stop when none remain or after eight
   questions. Intent nobody wrote down is a fact only the owner has, which is why this skill
   interviews. Nothing else is asked except the confirmation in step 7.
5. Run the tests below on both docs, and rewrite or cut what fails. In a repo too new to supply
   decisions, candidates, or parts, take them from the owner's upcoming decisions, or from the docs'
   own Goals.
6. Record each difference between the docs and the repo under Where the repo does not match yet.
   Fix nothing in the repo.
7. Ask the owner to confirm the docs, listing each remaining `[assumed]` to confirm or correct. On
   their yes, set `status: adopted`, and add one pointer to the repo's `CLAUDE.md`, creating it if
   missing and unless one already points at these docs: read these docs before changing direction,
   and every change holds up against them. Otherwise the doc stays `draft` with no pointer, because
   an assumption must not bind later sessions.

**Tests the skill runs, each stated with what failing looks like:**

| Test           | Ask                                                                                  | Fails when                                                       |
| -------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Opposite       | Would a sane project choose the opposite of each principle or non-goal?              | Nobody would: "high quality" and "user-focused" are not choices  |
| Past decision  | Take two real decisions from the plans, ideas, or history. Does the doc settle them? | It settles neither, so the doc only decorates the repo           |
| Rejected item  | Name one tempting thing the scope test refuses.                                      | The test refuses nothing                                         |
| Checkable goal | How would someone tell each goal is met or not?                                      | Nobody could tell                                                |
| Reason         | Could a reader apply each principle to a case the text does not cover?               | The principle has no reason                                      |
| Strategy adds  | Which strategy lines say how, not what the vision already says?                      | The strategy restates the vision                                 |
| Chooses work   | Give the work rule two real candidates. Does it pick one?                            | It accepts both or neither with no reason                        |
| Fits the repo  | Does each major part of the repo appear in The parts?                                | A part appears nowhere, or the doc names one that does not exist |

**Confidentiality.** Both docs are committed, so neither carries pricing, unit economics, kill
criteria, contacts, or a home path, and neither quotes `.agents_workspace/`. Business material stays
where `decision-artifact-locations.md` puts it. The vision may state the direction the business plan
supports, in its own words.

**No human.** The skill asks nothing, writes new docs with `status: draft`, adds no pointer, changes
nothing in an adopted doc and reports its proposed edits instead, marks any test with nothing to run
against "not run: nothing to test against", and ends with the questions it would have asked in order,
each with the assumption it used. This follows the vision's interview exception, which the skill
states as behavior without citing, because in another repo "the vision" means that repo's doc.

**Handoff.** `write-build-plan` step 2 gains: "When a `VISION.md` and `STRATEGY.md` exist (in
`product/`, `docs/`, the root, or where the repo's `CLAUDE.md` says), read them, and put anything the
plan would contradict under Open." `review-build-plan` step 3 gains: "A plan claim that contradicts
the repo's `VISION.md` or `STRATEGY.md`, in the same places, is a finding too." Reading a file adds no
dependency, per `docs/STRATEGY.md`. Neither sentence sits in a block `docs/CROSS_REFERENCES.md`
registers as duplicated, since its `write-build-plan` entries cover the shared plan format and retro
routing. Phase 2's Check confirms it with a grep.

**`docs/STRATEGY.md`.** The Shape row names the plugin. The spine's Shape row writes
`product/VISION.md` and `product/STRATEGY.md`, its Build row reads them, and the Shape-to-Build prose
says so. The kept-files list gains: "**Vision and strategy are revised in place.** One of each per
repo, committed and kept, because every later stage reads them." Where the repo does not match yet
gains one line for the missing `docs/VISION.md` row, and Phase 3 removes it. The disagreement lasts
one PR, because that file wants its own.

**Versions.** New plugin at `1.0.0`. `ceh-build-planning` PATCH, `1.1.16` to `1.1.17`.

## Phases

### Phase 1: The plugin and its skill

- **Builds:** the plugin directory with `plugin.json`, `README.md`, and the five files under Files.
  `SKILL.md` starts from `.claude/skills/add-plugin-component/assets/SKILL.template.md` and states the
  Procedure, tests, Confidentiality, and No human above. It shares one commit with Phase 2, because
  `CLAUDE.md` wants a component and its registration together and a pushed Phase 1 alone fails CI.
- **Check:** `claude plugin validate plugins/standalone/ceh-vision-and-strategy` passes, and
  `python tools/validate-plugins/checks/templates.py` and `checks/skills.py` pass. Manual, because no
  free command can judge prose: apply the eight tests by reading this repo's `docs/VISION.md` and
  `docs/STRATEGY.md`, record the results in this phase's Status, and confirm the no-`schema:` path of
  step 1 covers them.
- **Status:** done. `validate.py` passes. Manual check by reading, with no live run: Opposite passes
  ("agents first" has a real opposite in human-driven toolkits). Past decision passes (principle 6
  settles retiring the bundles, principle 7 settles waiting on hooks). Rejected item passes ("general
  productivity" is refused). Checkable goal partly fails: goals 3 and 5 can be checked, while goals 2
  and 4 state no way to tell, a real gap the skill would raise. Reason passes. Strategy adds passes.
  Chooses work passes ("a competitor has it" is refused). Fits the repo passes for plugins, and `tools/`
  has no row, which the skill would raise. Step 1 covers both files: `decision-vision-governs.md`
  treats the vision as binding, so it gets `adopted`, and extra sections such as Who overrides stay.

### Phase 2: Registration and the handoff

- **Builds:** `.claude-plugin/marketplace.json`, `docs/CATALOG.md`, root `README.md` Plugins and
  lifecycle tables, `CLAUDE.md` tier table, `docs/GETTING_STARTED.md` Shape entry, the
  `docs/STRATEGY.md` changes under Design, the two `ceh-build-planning` clauses with its version bump,
  `CHANGELOG.md`, and `docs/PLUGIN_VERSIONS.md`.
- **Check:** `python tools/validate-plugins/validate.py` passes, and
  `grep -l ceh-vision-and-strategy README.md CLAUDE.md docs/CATALOG.md docs/GETTING_STARTED.md docs/STRATEGY.md`
  lists all five, `grep -l "VISION.md" plugins/standalone/ceh-build-planning/skills/*/SKILL.md` lists
  both skills, and `grep -n "VISION\|Shape-to-Build" docs/CROSS_REFERENCES.md` shows no registered block
  holds the edited sentences.
- **Status:** done. `validate.py`: "OK: all plugin checks passed". Both greps list every file, and
  the one `CROSS_REFERENCES.md` hit cites vision principle 3, not an edited sentence.

### Phase 3: The vision row

- **Builds:** the plugin in the `docs/VISION.md` Shape row with a `CHANGELOG.md` entry, and removal
  of the gap line from `docs/STRATEGY.md`, in a second PR right after the first merges, because that
  file's Changing this file section wants its own PR.
- **Check:** `python tools/validate-plugins/validate.py` passes, and
  `grep ceh-vision-and-strategy docs/VISION.md` finds the row.
- **Status:** done. `validate.py`: "OK: all plugin checks passed", and the grep finds the Shape row.

## Open

- Live trigger check: a fresh `claude --plugin-dir` session is a real model call, so it waits for a
  request. Assumption: the validator and Phase 1's manual check are the proof for this PR, and the
  summary says so.

## Record

- 2026-11-02 Planned: status ready
- 2026-11-02 Reviewed: Revise first, 4 blocking (step 3 overwrites an adopted doc; no path for a file without a schema line; step 4 forbids the step 7 confirmation; tests assume a repo with history)
- 2026-11-02 PR: #193 https://github.com/cheneeheng/ceh-claude-code-library/pull/193
- 2026-11-02 Built Phase 3: python tools/validate-plugins/validate.py, OK: all plugin checks passed
- 2026-11-02 Checked: every item Built, 0 Gap, 0 Deviation, 0 Extra, 0 Failing, 1 Cannot verify (live triggering, a paid run)
