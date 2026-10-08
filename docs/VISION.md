# Vision

What this library is, what it is for, and the principles that settle a decision when the rules
elsewhere do not. Read it before adding a plugin, accepting an idea from [`IDEAS.md`](IDEAS.md),
or changing a rule in `CLAUDE.md`.

`CLAUDE.md` says how the repo works, and this file says why. If the two disagree, one of them is
wrong. Fix it on purpose, as described in Changing this file, never by quietly ignoring one.

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
  `claude -p`, subagents, and agent teams. It adds only what Claude Code lacks.
- **Granular.** You install the plugin for the situation you are in, or a scenario bundle that
  names several, and nothing else.

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
  authorize a class of these actions ahead of time, and then the agent no longer asks for that
  class.

How it asks:

- **Once, up front.** Batch every question into one round, each with a recommended answer, then run
  without stopping again.
- **Never for what it can find out.** The repo, the docs, and its tools come first. A question the
  agent could have answered itself costs the human's time and breaks the run.
- **With no human present** (a headless run), the agent takes the conservative option for a fact,
  records it, and leaves an irreversible action undone and reported instead of doing it.
- **Interviews are the exception.** A skill whose job is drawing knowledge out of a person, such as
  a product-market-fit loop or a blog interview, asks adaptively: each answer picks the next
  question. It still asks only what it cannot infer, and it still has a path for a run with no
  human: draft from what exists, mark every gap, and end with the questions a person must answer.

## Who overrides

- **An explicit human instruction overrides any standard** for the task it was given in. Silence, a
  hint, or the agent's own preference does not.
- **A calling agent can assign and narrow scope.** It cannot switch a standard off or widen what the
  agent is authorized to do. In a team of agents, only a human loosens the rules.
- **An override that keeps recurring is a defect in the plugin.** Fix the standard rather than
  overriding it every time.

## Scope: the product lifecycle

A plugin belongs here when it helps shape, build, prove, or tell people about a product. The
cross-cutting plugins hold the disciplines that apply at every stage.

| Stage      | What happens                                                             | Plugins today                                                                                                                                                                               |
| ---------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Shape      | Decide what to build and whether it is worth it                          | `ceh-business-plan`, `ceh-competitor-analysis`, `ceh-plan-build-review` (planning)                                                                                                          |
| Build      | Write the code, the UI, and the docs                                     | `ceh-python-service`, `ceh-python-library`, `ceh-web-frontend`, `ceh-ui-design`, `ceh-ag-ui`, `ceh-git-datastore`, `ceh-documentation`, `ceh-codebase-explanation`, `ceh-plan-build-review` |
| Prove      | Show it works and that a person can use it                               | `ceh-testing`, `ceh-usability-audit`, `ceh-plan-build-review` (review)                                                                                                                      |
| Tell       | Get it in front of the people who should find it                         | `ceh-blog`, `ceh-seo`                                                                                                                                                                       |
| Every step | How the agent behaves, commits, spends context, and runs repeatable work | `ceh-every-session`, `ceh-coding-conduct`, `ceh-git-workflow`, `ceh-workflow-builder`, `ceh-workflow-runner`                                                                                |

The test for a new plugin or skill: **does it help an agent ship a product, or get one in front of
people?** If not, it does not belong here, however useful it is. General productivity, chat
helpers, and anything bound to one application are out.

Teaching a person passes the test when that person must give the agent something it cannot get
alone: a yes before an irreversible action, or a fact only they hold. A yes to a system nobody
understood is not consent, so `ceh-codebase-explanation:explain-until-understood` stays.

## Goals

1. **Agents finish tasks without a human.** Every question an agent asks falls under Autonomy and
   its limits. Any other question is a gap in the guidance.
2. **Agents act as intended.** An agent following the guidance makes the choice the author would
   have made, so no one has to restate a standard in a session.
3. **Proven, not claimed.** No human checks the work, so evidence is the only signal that it is
   done. Work reported as done arrives with the evidence that it works.
4. **Load only what the moment needs.** Context is the agent's working memory. Installing a plugin
   costs one use case, and a loaded skill costs only what its moment needs.
5. **A repo that checks itself.** Every invariant a machine can check lives in `validate.py`, and
   CI is the gate.
6. **Ready to open up.** Nothing ties a plugin to one machine, account, or private context, and
   every opinion carries its reason.

## Non-goals

- **Human in the loop by default.** A workflow that waits on a person at every step has failed its
  design, however careful it looks.
- **Other hosts.** Claude Code runtimes only, whatever competitors ship for Cursor, Codex, or
  others.
- **Every stack.** A stack plugin exists because the author ships with that stack. A new one
  arrives with a real project, not for coverage.
- **Rebuilding Claude Code.** Where Claude Code already does the job (auto-mode permission checks,
  `/security-review` on a diff, native worktrees, `claude plugin eval`), we use it and add only
  the delta.
- **Switchable opinions.** Environment variables, listed in `docs/ENVIRONMENT_VARIABLES.md`, tune
  thresholds and paths, and may turn a guard off, because setting one is an explicit human act. None
  swaps one standard for another.
- **Releases.** Per-plugin versions and dated changelog sections are how changes reach users.
- **App-specific patterns.** A pattern bound to one application's schema or design is not a
  standard.

## Principles

Each principle ends with the question it answers in a review.

### 1. Agents first, humans second

Write for an agent that has only the text, the repo, and its tools. Name the trigger, the steps,
and the done condition. Never write "use your judgment" without the criteria the judgment needs. A
person reading the same text should still be able to follow it.
**Ask:** could an agent with no one to ask follow this to the end?

### 2. Decide by default, ask by exception

On ambiguity the agent picks the conservative option, records it, and keeps going. It asks only
under Autonomy and its limits, all at once, with a recommended answer for each question. A decision
that shapes the repo for others belongs in a committed file, not only in the git-ignored decision
log.
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
either never matches or restates what the model already knows.
**Ask:** what is the agent doing when this loads?

### 5. Only the delta

Write down what this repo believes that the model would not do on its own, and nothing it already
does. Every description, hook payload, and reference file takes space in the agent's context on
every session that loads it.
**Ask:** would the agent do this anyway without the text?

### 6. One use case, one install

Each plugin stands alone. A standard needed by two plugins is copied into both and registered in
`docs/CROSS_REFERENCES.md`, rather than pulled into a shared base that must also be installed.
Duplication costs the author effort, and a forced extra install costs every run.
**Ask:** can this situation be equipped with exactly this and nothing more?

### 7. Guide first, enforce on evidence

Reach for a Claude Code feature first, skill prose second, and a hook, validator, or test only
when there is evidence the prose fails. Enforcement narrows what the agent can do, so it has to be
earned. A hook is never added because a competitor has one.
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
the name alone, without opening it. The name is the only part an agent always sees in full:
descriptions get truncated in the skill listing, and only the name appears in file trees and in
`Invoke the Skill tool with skill="..."` calls. Choose clear over short and the plain word over the
clever one. A term of art stays only when the people who use it already know it (`ag-ui`,
`pull-request`). The `ceh-` prefix is a namespace that keeps these plugins apart from everyone
else's, not part of the name this principle judges.
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

This list shrinks as the gaps close. Remove a line in the PR that closes it. Add one when a change
here, or a new finding, opens a gap the same PR cannot close.

No known gaps as of 2026-10-08.

## Changing this file

Change it on purpose: in its own PR, with a `CHANGELOG.md` entry, and with any rule it now
contradicts in `CLAUDE.md`, `plugins/CLAUDE.md`, or a skill updated in the same PR. A proposal that
needs this file changed is a bigger decision than one that fits inside it, so treat it that way.
