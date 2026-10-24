# Retro Workflow

How the three retro skills fit together: which one to start, what each reads, where its issues go
next, and where its report is saved.

Per-skill detail lives in each skill's `SKILL.md` and its plugin's README. This guide covers only
what no single skill can document: the routing _between_ them and the files they share.

## The split

| Skill                                      | Looks back over                     | Reads                                         | Report kind           |
| ------------------------------------------ | ----------------------------------- | --------------------------------------------- | --------------------- |
| `ceh-git-workflow:review-recent-work`      | A period of work in a repo          | `git log`, and merged PRs when `gh` is set up | `period`              |
| `ceh-session-diagnosis:diagnose-session`   | One Claude Code session             | The session transcript and its subagents'     | `session-<id-prefix>` |
| `ceh-every-session:prevent-repeat-mistake` | One mistake that must not come back | The quoted evidence of that mistake           | `repeat-mistake`      |

The first two find issues and route them. The third fixes one kind of issue, an agent mistake, and
is also a route the first two hand work to. Each retro names the issue and its evidence, not the
fix, because the routed skill finds the cause and designs the fix.

## Routing: what you say to what runs

| Moment                                                                     | Loads                                                          |
| -------------------------------------------------------------------------- | -------------------------------------------------------------- |
| "write a retro", "what did we ship this week", "how did the last month go" | `review-recent-work`, over the period since the last retro     |
| "diagnose this session", "why did that session go wrong"                   | `diagnose-session`, which dispatches four `transcript-analyst` |
| "the agent kept doing X", with a session to read                           | `diagnose-session`                                             |
| "you did X again", "make sure this never happens again"                    | `prevent-repeat-mistake`                                       |

`review-recent-work` starts the day after the newest `product/retros/*-period.md` when no dates are
given, otherwise the last 14 days. `diagnose-session` reads `~/.claude/projects/<project>/`: "this
session" is the current one, "the last session" the newest other transcript.

## Where each issue goes

`review-recent-work` and `diagnose-session` share one route table (registered in
`docs/CROSS_REFERENCES.md`, "Retro routing and report location"):

| Issue is                                                              | Route                                                     |
| --------------------------------------------------------------------- | --------------------------------------------------------- |
| A bug in this repo's code or config                                   | `ceh-coding-conduct:find-root-cause`, writes a fix record |
| A feature or design change in this repo                               | `ceh-build-planning:write-build-plan`                     |
| An agent mistake a check or guidance in this repo should have stopped | `ceh-every-session:prevent-repeat-mistake`                |
| A rule for how work is done in this repo                              | `ceh-every-session:record-project-decisions`              |
| Anything else in this repo                                            | Fixed directly, with the check that proves it             |
| Outside this repo: user settings, an installed plugin, Claude Code    | Left in the report for the user                           |

The agent acts on every in-repo route in the same session. A route whose plugin is not installed
stays open in the report, with the route named. A Claude Code root cause from `diagnose-session` is
always left for the user, because filing its bug report is outward-facing.

`prevent-repeat-mistake` has no route table. It climbs its own ladder, strongest rung first: remove
the cause, a Claude Code setting, a check at write time, a check before landing, written guidance.
It builds a check that lives in the current repo, and drafts anything that changes how later
sessions behave (`CLAUDE.md`, memory, a skill, a hook) for the user to approve.

## Where reports are saved

Every retro splits its report by where each fix lands:

| Fix lands         | File                                                      | Committed |
| ----------------- | --------------------------------------------------------- | --------- |
| In this repo      | `product/retros/<YYYY-MM-DD>-<kind>.md`                   | Yes       |
| Outside this repo | `.agents_workspace/product/retros/<YYYY-MM-DD>-<kind>.md` | No        |

The committed file lands with the first fix it routes, because the routed work and the next retro
read it. The local file is for the user alone. When both exist, each names the other in its
`other_file` frontmatter field. Each skill fills its own template, `period-retro`, `session-retro`,
or `repeat-mistake`, because the three reports differ.

A committed report leaves the machine on the next push, so it is cleaned before commit:
`diagnose-session` scrubs and audits its file (secrets, home paths, hostnames, personal data), and
`prevent-repeat-mistake` masks secrets as `<secret>`. The `hygiene` check in
`tools/validate-plugins/validate.py` rejects a home path anywhere in `product/`.

## Scenario A: a period retro

1. Say "write a retro for the last two weeks". `review-recent-work` collects the history, groups
   what shipped, reads the flow, and names at most three issues, each with the PRs that show it.
2. Each in-repo issue goes to its route in the same session: a fix-of-a-fix to `find-root-cause`, a
   churn hotspot to `write-build-plan`, slow or unreviewed merges to `record-project-decisions`.
3. The retro is saved to `product/retros/<date>-period.md` and committed with the first fix.

## Scenario B: a session that went wrong

1. Say "diagnose the last session, it wrote code before a plan". `diagnose-session` sends four
   `transcript-analyst` agents, one per lens, then re-reads every cited line before concluding.
2. Each root cause is classed (request, guidance, environment, model, Claude Code) and routed. A
   guidance or model cause usually goes to `prevent-repeat-mistake`.
3. `prevent-repeat-mistake` picks the rung, builds or drafts the fix, and saves
   `product/retros/<date>-repeat-mistake.md`. Its next run lists every draft still
   `awaiting approval` before taking a new mistake, so a draft is not lost between sessions.

`product/retros/2026-10-22-session-de93dc4b.md` and `product/retros/2026-10-22-repeat-mistake.md`
are a real pair from this repo: the session diagnosis found a skill description that did not fire,
and the repeat-mistake report rewrote it at rung 5.
