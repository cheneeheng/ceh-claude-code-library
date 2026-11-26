# Vision

What this library is, what it is for, and the principles that settle a decision when the rules
elsewhere do not. `CLAUDE.md` and the decision rules in `.claude/rules/` say how the repo works,
and this file says why, so every change must hold up against it. If the two disagree, fix one on
purpose, as described in Changing this file, never by quietly ignoring one.

## Identity

`ceh-claude-code-library` is guidance for autonomous agents, delivered as Claude Code plugins.
Every skill, subagent, hook, and output style is written first for an agent running a task with
no human watching, and second for a person using Claude Code. It is personal and opinionated
today, and written so it can open to other people later without a rewrite.

It is:

- **Agents first, humans second.** Each component tells an agent what to do at one moment in a
  product's life, so it acts the intended way instead of improvising.
- **Guidance, not a cage.** The agent still decides. The plugins give it what it needs to decide
  well, and constrain it only where guidance has been shown to fail.
- **Claude Code native.** It runs on any Claude Code runtime: interactive sessions, headless
  `claude -p`, subagents, and agent teams.
- **Granular.** You install a small core, then the plugin for the stage you are in, and nothing
  else. [`GETTING_STARTED.md`](GETTING_STARTED.md) is the route.

It is not:

- A toolkit a person drives step by step.
- A neutral catalogue of best practice for every language and framework.
- A multi-host toolkit. Agents and editors outside Claude Code are out of scope.

## Vision

A team of agents takes a product from a rough idea to working software to the people who should
find it, as autonomously as possible, guided at every step by standards that tell them how. A human
supplies only what an agent cannot: facts only a person has, and a yes before anything that cannot
be undone.

## Autonomy and its limits

The agent decides by default. It asks a human only in these cases:

- **Facts only a human has:** secrets and credentials, intent nobody wrote down, and taste where no
  standard decides.
- **Before an irreversible or outward-facing action:** publishing, pushing or merging to a shared
  remote, spending money, deleting data, or sending content to an external service. A human can
  authorize a class of these actions ahead of time, recorded as a rule in `.claude/rules/` (as
  `decision-pr-review.md` does for merging this repo's own PRs), and then the agent no longer asks
  for that class.

How it asks:

- **Once, up front.** Batch every question into one round, each with a recommended answer, then run
  without stopping again.
- **Never for what it can find out.** The repo, the docs, and its tools come first. A question the
  agent could have answered itself costs the human's time and breaks the run.
- **With no human present** (a headless run), the agent takes the conservative option for a fact,
  records it, and leaves an irreversible action undone and reported instead of doing it.
- **Interviews are the exception.** A skill whose job is drawing knowledge out of a person, such as
  a product-market-fit loop, asks adaptively: each answer picks the next question. It still asks
  only what it cannot infer, and it still has a path for a run with no human: draft from what
  exists, mark every gap, and end with the questions a person must answer.

## Who overrides

- **An explicit human instruction overrides any standard** for the task it was given in. Silence, a
  hint, or the agent's own preference does not.
- **A calling agent can assign and narrow scope.** It cannot switch a standard off or widen what the
  agent is authorized to do. In a team of agents, only a human loosens the rules.
- **An override that keeps recurring is a defect in the plugin.** Fix the standard rather than
  overriding it every time.

## Scope: the product lifecycle

A plugin belongs here when it helps shape, build, prove, or tell people about a product. The Core
plugins hold the disciplines that apply at every stage and load in most sessions, and
`ceh-testing` also sits in Prove. The On demand plugins are installed for an activity that can come
at any stage.

| Stage     | What happens                                                           | Plugins today                                                                                                                                                   |
| --------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Shape     | Decide what to build and whether it is worth it                        | `ceh-product-direction`, `ceh-competitor-analysis`                                                                                                              |
| Build     | Decide how to build it, then write the code, the UI, and the docs      | `ceh-build-plan`, `ceh-python-service`, `ceh-python-library`, `ceh-web-frontend`, `ceh-ui-design`, `ceh-ag-ui`, `ceh-documentation`, `ceh-codebase-explanation` |
| Prove     | Show it works and that a person can use it                             | `ceh-testing`, `ceh-usability-audit`, `ceh-check-build-against-plan`, `ceh-security-audit`                                                                      |
| Tell      | Get it in front of the people who should find it                       | `ceh-blog-and-seo`                                                                                                                                              |
| Core      | How the agent behaves, commits, tests, and spends context              | `ceh-every-session`, `ceh-coding-conduct`, `ceh-git-workflow`, `ceh-testing`                                                                                    |
| On demand | Turn repeated work into a workflow and run it, or learn from a session | `ceh-workflow-builder`, `ceh-workflow-runner`, `ceh-session-learning`                                                                                           |

The stages are a route, not only a filing system: each one writes handoff files the next
one reads, so installed plugins chain without a router. How they chain, and how the next piece of
work is chosen, is in [`STRATEGY.md`](STRATEGY.md).

The test for a new plugin or skill: **does it help an agent ship a product, or get one in front of
people?** If not, it does not belong here, however useful it is. General productivity, chat
helpers, and anything bound to one application are out.

Three kinds of component made for a person pass the test:

- **Teaching a person** passes when that person must give the agent a yes or a fact only they
  hold. A yes to a system nobody understood is not consent, so
  `ceh-codebase-explanation:explain-until-understood` stays.
- **Advising a person** passes when it only points at the installed skill or agent that fits their
  situation and runs nothing. Which stage to enter next is the person's intent, and an advisor
  that ran what it suggested would be the router the strategy rules out.
- **Changing only what a person sees**, never what an agent reads, passes when it helps that
  person give a fact or a yes, or judge the evidence, because it costs the agent's context
  nothing. A mod that folds a reply to its summary table, or draws its closing questions as
  options, passes. One that only makes chatting more pleasant does not.

## How the library is cut

The library has three levels, and each has one name and one job. A stage holds plugins, and a
plugin holds skills:

| Level  | What it is                                                                                                                                                                                      | What decides it                                                       |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Stage  | Shape, Build, Prove or Tell, the four route rows of the table above: where a plugin sits on the route, and so when a user installs it. Core and On demand are rows beside the route, not stages | Where its moments come in a product's life                            |
| Plugin | One use case: the moments a user reaches together, in one row of the table, for one kind of work, so they install together                                                                      | Would a user who reaches one of its moments want the rest loaded too? |
| Skill  | One moment: something the agent is doing, such as opening a PR                                                                                                                                  | The moment test below                                                 |

Each plugin sits in one row. `ceh-testing` is the one exception, in Core and in Prove, because
the stack plugins that write tests (`ceh-python-service`, `ceh-python-library`,
`ceh-web-frontend`) depend on it. A stack plugin is a Build plugin picked by what is being built,
and is named for its stack. A standard a hook loads on every session, such as the coding contract,
has no moment of its own, so the moment test does not apply to it: it must hold in every session
its plugin loads in.

### The moment test

A new skill passes these in order, and stops at the first no:

1. **Name the moment.** Finish "The agent is \_\_\_", and give two or three phrases a real user
   would type. If the blank cannot be filled, it is not a skill yet.
2. **The moment is free.** No skill in `docs/CATALOG.md` already fires on it. If one does, extend
   that skill instead.
3. **There is a delta.** Name what the agent does at this moment without the skill: the step it
   gets wrong or improvises. If it already does the right thing, the skill restates the model
   (principle 5).
4. **It is in scope.** The moment comes while shaping, building, proving, or telling a product,
   per the scope test above.
5. **It has a home.** It goes in the plugin a user already has installed when the moment arrives.
   With none, it starts a new plugin in the moment's stage. When the moment can arrive unannounced
   in any session, such as "you did X again", this step outranks the plugin's kind of work: the
   skill goes in `ceh-every-session` if it passes `decision-every-session-admission.md`, and
   otherwise in the Core plugin whose kind of work it is, even when an On demand plugin does
   related work.

## Goals

1. **Agents finish tasks without a human.** Every question an agent asks falls under Autonomy and
   its limits.
2. **Agents act as intended.** No one has to restate a standard in a session.
3. **Proven, not claimed.** Work reported as done arrives with the evidence that it works.
4. **Load only what the moment needs.** Installing a plugin costs one use case, and a loaded skill
   costs only what its moment needs.
5. **A repo that checks itself.** A check that has earned its place under principle 7 lives in
   `validate.py`, or in the unit tests CI runs beside it, and CI is the gate. Principle 7 decides
   whether a check exists, and this goal decides where it goes.
6. **Ready to open up.** Nothing ties a plugin to one machine, account, or private context, and
   every opinion carries its reason.

## Non-goals

- **Every stack.** A stack plugin exists because the author ships with that stack. A new one
  arrives with a real project, not for coverage.
- **Rebuilding Claude Code.** Where Claude Code already does the job (auto-mode permission checks,
  `/security-review` on a diff, native worktrees, `claude plugin eval`), we use it and add only
  the delta.
- **Switchable opinions.** Environment variables, listed in `docs/ENVIRONMENT_VARIABLES.md`, tune
  thresholds and paths, and may turn a guard off, because setting one is an explicit human act. None
  swaps one standard for another.

## Principles

Each principle ends with the question it answers in a review.

### 1. Agents first, humans second

Write for an agent that has only the text, the repo, and its tools. Name the trigger, the steps,
and the done condition. Never write "use your judgment" without the criteria the judgment needs. A
person reading the same text should still be able to follow it.
**Ask:** could an agent with no one to ask follow this to the end?

### 2. Decide by default, ask by exception

On ambiguity the agent picks the conservative option, records it, and keeps going. It asks only as
Autonomy and its limits allows. A decision that shapes the repo for others belongs in a committed
file or the versioned workspace, not only in the git-ignored decision log. The versioned workspace
is `.agents_workspace/` when it is a git repository of its own, pushed to a private remote, so its
history versions the artifacts even though this repo ignores the folder.
**Ask:** does this make the agent stop for something it could have decided or found out?

### 3. Proof over permission

Proving its own work is part of the task, not extra scope. The agent writes and runs the tests and
checks that show its change works, without being asked. Scope stays minimal: proof is not a licence
for refactors, extra features, or drive-by fixes. Verification that costs money or long wall-clock
time beyond the change's own checks, such as paid evals or real model calls, still waits for a
request.
**Ask:** what evidence shows this works, and did the agent produce it?

### 4. Moments, not topics

A skill fires on something the agent is doing ("opening a PR"), not on a subject ("PostgreSQL").
The agent loads skills by matching what it is doing to a description, so a topic description
either never matches or restates what the model already knows. The moment test, in How the
library is cut, is the gate for a new skill.
**Ask:** what is the agent doing when this loads?

### 5. Only the delta

Write down what this repo believes that the model would not do on its own, and nothing it already
does. Every description, hook payload, and reference file takes space in the agent's context on
every session that loads it.
**Ask:** would the agent do this anyway without the text?

### 6. One use case, one install

Each plugin stands alone. A standard needed by two plugins is copied into both and registered in
`docs/CROSS_REFERENCES.md`, rather than pulled into a shared base that must also be installed.
Duplication costs the author effort, and a forced extra install costs every run. A plugin is one
use case, and a use case sits in one row of the stage table. One that spans several rows is
split, so a user who enters at one stage installs only that stage. A dependency is declared only
when a skill calls the other plugin on every run (`decision-plugin-dependencies.md`), and it stays
within the plugin's own stage or reaches a Core plugin, which the user has installed already. One
that reaches another stage is a gap, listed below. The edges are in `docs/PLUGIN_DEPENDENCIES.md`.
**Ask:** can this situation be equipped with exactly this and nothing more?

### 7. Guide first, enforce on evidence

Reach for a Claude Code feature first, skill prose second, and a hook, validator, or test only
when there is evidence the prose fails. Enforcement narrows what the agent can do, so it has to be
earned. A hook is never added because a competitor has one. A check that earns its place goes
where goal 5 says.
**Ask:** what failure did we see that guidance did not prevent?

### 8. Opinions with reasons

Every standard picks one answer and says why. The reason lets an agent apply the standard to a case
the text did not foresee, and lets a later reader judge whether it still holds. An opinion without
a reason is a habit, not a standard.
**Ask:** could an agent tell from the reason what to do in a case the text does not cover?

### 9. Small surface, sharp edges

Fewer, sharper skills beat broad coverage. Content that no longer earns its place moves to
`archive/`. An idea that does not fit is rejected with its reason recorded in `docs/IDEAS.md`, so
it is not proposed again.
**Ask:** what would we lose if this did not exist?

### 10. Names say what they do

A plugin, skill, agent, hook, or script is named so a person or an agent can tell what it does from
the name alone. The name is the only part an agent always sees in full: descriptions get truncated
in the skill listing, and only the name appears in file trees and in
`Invoke the Skill tool with skill="..."` calls. Choose the plain word over the short or clever one.
A term of art stays only when the people who use it already know it (`ag-ui`, `pull-request`), and
the `ceh-` prefix is a namespace, not part of the name this principle judges.
**Ask:** could someone who has seen only the name say what it does and when it is used?

## When principles conflict

An explicit human instruction sits above all of these, as described in Who overrides. Between the
principles, resolve in this order:

1. **Proof.** Never trade away the evidence that work is correct.
2. **Autonomy.** Fewer stops for a human come next.
3. **Context and install cost.** What every run pays comes before the author's convenience.
4. **Authoring convenience.** Easier maintenance wins only when the first three are equal.

For example, an agent that cannot run its integration tests without a database URL asks for it,
because proof outranks autonomy (1 beats 2). A shared base plugin would be easier to maintain, but
every run would pay for the extra install, so standards are duplicated (3 beats 4).

## Where the repo does not match yet

Remove a line in the PR that closes its gap, and add one when a change here, or a new finding,
opens a gap the same PR cannot close.

As of 2026-11-18:

- **Principle 5, Only the delta.** The `SessionStart` hook loads both coding skills in a session
  that writes no code. Kept until a session shows it doing harm.
- **Principle 5, Only the delta.** Six skills run past 300 lines, with a few trims left.
- **Principle 6, One use case, one install.** `ceh-competitor-analysis`, a Shape plugin, depends on
  `ceh-ui-design`, a Build plugin, to render its reports, kept as an exception until design is
  something every skill can reach.
- **Goal 2 and principle 4, Moments, not topics.** A full install overflows the default skill
  listing budget. `tools/setup/setup.py` raises it to 2%, but the user's other plugins share the
  budget, so some skills can still lose the description they trigger on. `/doctor` shows it.
- **Scope.** `ceh-workflow-builder` and `ceh-workflow-runner` are decided to move out of this repo
  and still sit in the On demand row.

## Changing this file

Change it on purpose: in its own PR, with a `CHANGELOG.md` entry, and with any rule it now
contradicts in `CLAUDE.md`, `plugins/CLAUDE.md`, `.claude/rules/decision-*.md`, or a skill updated
in that same PR. The PR lands before any other change that relies on the new text. A file found
disagreeing with the vision as it stands is fixed in the PR that finds it, with no vision change.
A proposal that needs this file changed is a bigger decision than one that fits inside it, so treat
it that way.
