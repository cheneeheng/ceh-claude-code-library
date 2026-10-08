# Ideas Backlog

Ideas taken from the gstack, pstack, superpowers, ECC, and mattpocock/skills competitor analyses of
2026-10-07 ("What we take": Adopt now and Build). Together they cover every competitor skill,
agent, and workflow that our work covers only partly or not at all, except what each analysis put
under Skip. Nothing here is committed work, and an entry marked **Status: rejected** stays listed
so it is not proposed again. Where several competitors do the same job, the ideas are merged into
one entry.

Every entry was checked against [`VISION.md`](VISION.md) on 2026-10-08, and a **Note** records
where the vision changes one. Check each new entry the same way. Hook and guard entries need a
failure that guidance alone did not prevent before they are built (principle 7).

Effort: S is under a day, M is a few days, L is longer.

## Adopt now

### Description size cap

- **Source:** gstack `test/catalog-budget.test.ts`
- **Where:** `tools/validate-plugins/validate.py`
- **Effort:** S
- **Idea:** A per-description byte cap plus a ratcheted total keeps skill-catalog cost bounded.
  gstack caps each description at 260 bytes. Ours run from 63 to 1,058 bytes, median 693.
- **Status:** half built on 2026-10-08: `validate.py` caps each description at 600 characters. The
  ratcheted total is still open.

### Lead-judgment buckets

- **Source:** pstack `interrogate`
- **Where:** `ceh-git-workflow:code-review`
- **Effort:** S
- **Idea:** Sort findings into Act On, Consider, Noted, and Dismissed, with at most 5 Act On items,
  and keep Dismissed with reasons so the user can override it.
- **Status:** built on 2026-10-08 in reduced form: the `[blocking]` / `[advisory]` / `[question]`
  prefixes already sort findings, so `code-review` caps `[blocking]` at five and adds a Dismissed
  list rather than a second set of buckets.

### Quote or suppress

- **Source:** gstack confidence resolver
- **Where:** `ceh-git-workflow:code-review`, `ceh-plan-build-review:review-against-plan`,
  `ceh-testing:audit-test-suite`
- **Effort:** S
- **Idea:** A review finding with no quoted code drops below the line that shows it.
- **Note:** Three plugins means a `docs/CROSS_REFERENCES.md` entry.

### Scope drift first

- **Source:** gstack review-scope resolver
- **Where:** `ceh-git-workflow:code-review` and `pull-request` self-review
- **Effort:** S
- **Idea:** Compare the stated intent with the actual diff before judging code quality.
- **Status:** built on 2026-10-08: step 1 of `code-review`, and a self-review bullet in
  `pull-request`.

### No prejudging the reviewer

- **Source:** superpowers `requesting-code-review`, `code-reviewer.md`, `task-reviewer-prompt`,
  `re-review-prompt`
- **Where:** `ceh-git-workflow:code-review`, `ceh-plan-build-review:review-against-plan`
- **Effort:** S
- **Idea:** A review brief never says "do not flag" or "at most Minor", and a third verdict, "cannot
  verify from diff", exists.
- **Note:** Two plugins means a `docs/CROSS_REFERENCES.md` entry.

### Receive review with rigor

- **Source:** superpowers `receiving-code-review`
- **Where:** new skill in `ceh-git-workflow`
- **Effort:** S
- **Idea:** Fires on "address these review comments": verify each comment against the code before
  acting, push back with evidence, no performative agreement.

### Extra review lenses

- **Source:** ECC `silent-failure-hunter`, `comment-analyzer`, `type-design-analyzer`
- **Where:** `ceh-git-workflow:code-review`
- **Effort:** S
- **Idea:** Swallowed errors, stale comments, and weak types as named review lenses.
- **Status:** built on 2026-10-08 as checks inside `code-review`'s Correctness and Design steps.

### Patch-id re-check

- **Source:** pstack `shipping` playbook
- **Where:** `ceh-git-workflow:pull-request` (land step)
- **Effort:** S
- **Idea:** Record the `git patch-id` a review or test run saw, and compare it again before landing.
  A rebase can invalidate a review without touching a check.
- **Status:** built on 2026-10-08 in `pull-request`'s pre-merge gate.

### PR babysit loop

- **Source:** pstack `babysit` playbook
- **Where:** `ceh-git-workflow:pull-request`
- **Effort:** S
- **Idea:** A loop that clears conflicts, review threads, and red CI one PR at a time, stopping where
  a human call begins.

### PR body shape

- **Source:** mattpocock `pr`
- **Where:** `ceh-git-workflow:pull-request`
- **Effort:** S
- **Idea:** Lead with the smallest visual, show before and after, and name the door (one-way or
  two-way) and the blast radius.
- **Status:** built on 2026-10-08 in `pull-request`'s body template: a before/after line under What
  and a `## Risk` section.

### Finish-branch menu

- **Source:** superpowers `finishing-a-development-branch`
- **Where:** `ceh-git-workflow:pull-request`
- **Effort:** S
- **Idea:** Offer merge, PR, keep, or discard when work ends, and clean up the worktree. Ours
  assumes the branch always heads into a PR.
- **Note:** Agents first: the agent picks, and only merge and discard, being outward-facing or
  irreversible, wait for a human or advance authorization.
- **Status:** built, confirmed on 2026-10-08 with no edit: `pull-request` already has the Open
  path, the local no-PR merge (Land the branch), and worktree cleanup after merge. "Keep" needs no
  step, and "discard" deletes an unmerged branch, a one-way door the contract already holds for a
  human.

### Worktree cleanup

- **Source:** pstack `worktree-cleanup` playbook
- **Where:** `ceh-git-workflow:pull-request` (post-merge cleanup)
- **Effort:** S
- **Idea:** Prune merged or abandoned git worktrees, asking before any deletion.
- **Status:** built on 2026-10-08 in `pull-request`'s Merge cleanup step. It removes a worktree the
  session created without asking, and asks before removing any other.

### Docs drift check

- **Source:** gstack `document-release`; ECC `living-docs-governance`, `doc-updater`, `docs-lookup`
- **Where:** `ceh-git-workflow:update-readme`
- **Effort:** S
- **Idea:** After a change lands, compare what the docs claim with what the diff shipped, not only
  whether the README mentions the feature.
- **Status:** built on 2026-10-08 as step 4 of `update-readme`, scoped to the README.

### Certainty ladder

- **Source:** pstack `blast-radius`, `principle-prove-it-works`
- **Where:** `ceh-testing:verify-behavior-preserved`
- **Effort:** S
- **Idea:** Name the one fact a change's safety rests on and prove it at the highest rung that is
  cheap: said so, pointed at a line, walked the failure, ran code, reproduced in the app.
- **Status:** built on 2026-10-08 as step 0 of `verify-behavior-preserved`.

### Test value line

- **Source:** gstack `docs/test-value-bar.md`
- **Where:** `ceh-testing:design-test-cases`, `test-a-bug-fix`, `audit-test-suite`
- **Effort:** S
- **Idea:** Each new test states `protects`, `fails_when`, and `why_new`.
- **Status:** built on 2026-10-08 as a hand-over line in `design-test-cases` and `test-a-bug-fix`,
  not a comment in the test file, and as a deletion check in `audit-test-suite` step 1.

### Test-first rules

- **Source:** pstack `tdd`, `principle-test-behavior-not-implementation`
- **Where:** `ceh-testing:design-test-cases`, `test-a-bug-fix`
- **Effort:** S
- **Idea:** Write the failing test first, call the code the way users do, and assert literal
  expected values. The same rules feed Test-first by default.
- **Status:** built on 2026-10-08 in `design-test-cases` ("Before the first test") and
  `test-a-bug-fix` step 1. Test-first applies to new behavior and bug fixes only: making it the
  default for every task stays with Test-first by default.

### Test seams agreed first

- **Source:** mattpocock `tdd`
- **Where:** `ceh-testing:design-test-cases`
- **Effort:** S
- **Idea:** Agree the seams a test will hit before writing it, and name the tautological test as an
  anti-pattern. The red-green half joins Test-first by default.
- **Status:** built on 2026-10-08 in `design-test-cases` ("Before the first test").

### Test-polluter bisect

- **Source:** superpowers `find-polluter.sh`
- **Where:** `ceh-testing:audit-test-suite`
- **Effort:** S
- **Idea:** Find which test leaves stray files or state by bisecting the suite.
- **Status:** built on 2026-10-08 in step 4 of `audit-test-suite`, as prose and one command, with
  no script.

### One-way-door list

- **Source:** gstack one-way-door registry
- **Where:** `ceh-coding-conduct:agent-coding-contract`, Stop conditions
- **Effort:** S
- **Idea:** A concrete list of questions that are never auto-decided, giving our "stop on
  irreversible impact" rule teeth.
- **Status:** built on 2026-10-08 as the contract's One-way doors list.

### Claim needs fresh evidence

- **Source:** superpowers `verification-before-completion`
- **Where:** `ceh-coding-conduct:agent-coding-contract`, No implicit actions
- **Effort:** S
- **Idea:** A success claim cites output from the full verification command, run this turn.
- **Note:** "Full" means the change's own checks. The full suite is a slow run and still waits for a
  request, per the contract's Validation policy.
- **Status:** built on 2026-10-08 in the contract's "No implicit actions" rule.

### Parallel dispatch brief

- **Source:** superpowers `dispatching-parallel-agents`
- **Where:** `ceh-coding-conduct:agent-coding-contract`, Task decomposition
- **Effort:** S
- **Idea:** Our contract already says to fan out independent subtasks. Add what each subagent prompt
  must carry: scope, inputs as paths, expected return.
- **Status:** built on 2026-10-08 in the contract's Task decomposition, which also requires the
  decisions that bind the subagent.

### Infer house style first

- **Source:** ECC `inherit-legacy-style`, `coding-standards`
- **Where:** `ceh-coding-conduct:agent-coding-contract`
- **Effort:** S
- **Idea:** Before editing legacy code, name the conventions it actually uses. Our contract says
  "follow repo patterns" without saying how to find them.

### Build the lever

- **Source:** pstack `principle-build-the-lever`
- **Where:** `ceh-coding-conduct:agent-coding-contract`
- **Effort:** S
- **Idea:** For bulk or repeated work, write the script or codemod that does or checks it instead
  of editing by hand.
- **Status:** built on 2026-10-08 as the contract's "Build the lever" rule. The check is always a
  command, and a script makes the change only when it is mechanical, matching the rule that edits
  go through Edit.

### Search before building

- **Source:** ECC `search-first`
- **Where:** `ceh-coding-conduct:write-less-code`
- **Effort:** S
- **Idea:** Before custom code, search package registries and installed skills. Extends rungs 2
  to 4.
- **Status:** built on 2026-10-08 in `write-less-code`'s Procedure, as one search of the repo, the
  dependency manifest, and the skill list. A registry search waits for permission to add a
  dependency, which the contract's non-goals forbid by default.

### Structural rules

- **Source:** pstack principles boundary-discipline, minimize-reader-load,
  migrate-callers-then-delete-legacy-apis, redesign-from-first-principles
- **Where:** `ceh-coding-conduct:refactor-repo`, `write-less-code`
- **Effort:** S
- **Idea:** Add these as rules inside our existing skills rather than as skills of their own.

### Design red-flag screen

- **Source:** pstack `architect`
- **Where:** `ceh-coding-conduct:refactor-repo` or `document-architecture`
- **Effort:** S
- **Idea:** Screen a design for Ousterhout's red flags: shallow module, information leakage,
  pass-through method.
- **Status:** built on 2026-10-08 in `refactor-repo`'s Phase 1 inventory. Shallow modules and
  pass-through methods were already there under over-abstraction, so only information leakage was
  added.

### Rationale from history

- **Source:** pstack `why`, `investigation` playbook
- **Where:** `ceh-codebase-explanation:explain-codebase`, `explain-until-understood`
- **Effort:** S
- **Idea:** Answer "why is it like this" from git log, blame, and PRs, with every claim cited.
- **Note:** Decided on 2026-10-08: a new skill in `ceh-codebase-explanation`, not an addition to
  `explain-codebase`, because it reads history rather than the current code.

### Mine the implied spec

- **Source:** ECC `spec-miner`
- **Where:** `ceh-codebase-explanation:explain-codebase`
- **Effort:** S
- **Idea:** Extract the behavior the code actually promises, as a spec, before changing it.
- **Status:** not built, covered on 2026-10-08: `ceh-testing:verify-behavior-preserved` pins
  current behavior with characterization tests before a change, which a prose spec would only
  restate more weakly.

### Plain-English re-pitch

- **Source:** mattpocock `wait-what`
- **Where:** `ceh-codebase-explanation:explain-until-understood`
- **Effort:** S
- **Idea:** Add the moment "wait, what?": re-pitch the last message in plain words before escalating
  the explanation.
- **Status:** built on 2026-10-08 in `explain-until-understood`'s "When it did not land". The
  description has no room under the 600-character cap, so the moment lives in the body only.

### Evidence label per claim

- **Source:** pstack `poteto-mode`
- **Where:** `ceh-coding-conduct` output style
- **Effort:** S
- **Idea:** Every claim carries measured, inferred, or guess in the same sentence.

### Comment audit

- **Source:** pstack `no-comments`, `comment-sicko` agent
- **Where:** new read-only agent in `ceh-coding-conduct`
- **Effort:** S
- **Idea:** Flag comments that restate the code or excuse a workaround, and offer to encode real
  constraints in types or checks instead.

### Protect lint configs

- **Source:** ECC `config-protection`
- **Where:** new `PreToolUse` hook in `ceh-coding-conduct`
- **Effort:** S
- **Idea:** Block edits to an existing linter or formatter config so the agent fixes the code
  instead. Stack-agnostic.
- **Status:** waiting on evidence. A new guard is built only after an observed failure that prose
  did not prevent (principle 7), so this stays unbuilt until one is recorded here.

### Block hook bypass

- **Source:** ECC `pre:bash:dispatcher`, `block-no-verify`
- **Where:** `ceh-git-workflow` `PreToolUse` hook
- **Effort:** S
- **Idea:** Deny `--no-verify`, `-n`, and `-c core.hooksPath=` on commit, which our pre-commit
  discipline assumes never happen.
- **Status:** waiting on evidence. A new guard is built only after an observed failure that prose
  did not prevent (principle 7), so this stays unbuilt until one is recorded here.

### Denial dampening

- **Source:** ECC `gateguard-fact-force`
- **Where:** `ceh-every-session` bulk-read guards, `ceh-git-workflow` branch-guard
- **Effort:** S
- **Idea:** Full deny text for the first three denials, then one line with an ordinal, and every
  deny names the env var that disables it. Identical deny blocks push the model into repetition
  loops.

### Hook kill switch

- **Source:** ECC hook profiles in `run-with-flags.js`
- **Where:** each hooked plugin's `scripts/`, `docs/ENVIRONMENT_VARIABLES.md`
- **Effort:** S
- **Idea:** A `CEH_DISABLED_HOOKS` list lets a user switch off one hook without uninstalling.
- **Note:** Copied per plugin, so a `docs/CROSS_REFERENCES.md` entry.

### Save and restore on demand

- **Source:** gstack `context-save`, `context-restore`; pstack `recall`, `session-pickup` and
  `pause-safely` playbooks; ECC session commands, `session:start`, `stop:session-end`,
  `pre:compact`, `suggest-compact`, `strategic-compact`, `token-budget-advisor`
- **Where:** `ceh-every-session:usage-limit-handoff`
- **Effort:** S
- **Idea:** The handoff writes a resume point only near the usage limit. Let it also fire on "save
  where we are" and "pick this up".
- **Status:** built on 2026-10-08 as `ceh-every-session:hand-off-session` (save and load), which
  `usage-limit-handoff` now calls.

### Phase-boundary tree

- **Source:** mattpocock `handoff`
- **Where:** `ceh-every-session:usage-limit-handoff`
- **Effort:** S
- **Idea:** At a phase change, pick continue, clear, handoff, subagent, or compact, first yes wins.
  Our handoff fires only near the usage limit.

### Questionnaire for others

- **Source:** mattpocock `to-questionnaire`
- **Where:** new skill in `ceh-every-session`
- **Effort:** S
- **Idea:** Turn open questions into an async questionnaire someone else answers. Holds for any
  Claude Code use, so it passes the `ceh-every-session` test.

### `skip: <reason>` rows

- **Source:** pstack `poteto-mode`
- **Where:** `ceh-workflow-runner:run-agentic-workflow`, `ceh-plan-build-review:implement-from-plan`
- **Effort:** S
- **Idea:** Copy the steps into the task list verbatim and keep a skipped step visible as
  `skip: <reason>`.

### Triage before planning

- **Source:** superpowers `brainstorming`
- **Where:** `ceh-plan-build-review:plan-fullstack-app`, `ceh-workflow-builder:interview-workflow-task`
- **Effort:** S
- **Idea:** Announce spike, bounded, or architectural before planning, and only architectural work
  gets a written spec. The path may upgrade, never downgrade.

### Skill from this session

- **Source:** gstack `skillify`
- **Where:** `ceh-workflow-builder:build-agentic-workflow`
- **Effort:** S
- **Idea:** Add the moment "turn what we just did into a skill", building from the steps that
  worked in this session instead of an interview.
- **Note:** Decided on 2026-10-08: a separate plugin rather than a moment inside
  `build-agentic-workflow`, so it needs the `VISION.md` scope test and its own PR.

### Loop failure review

- **Source:** ECC `loop-design-check`, autonomous-loop skills
- **Where:** `ceh-workflow-builder:build-agentic-workflow`
- **Effort:** S
- **Idea:** Check a designed loop for spinning without progress and for gaming its own metric.
- **Note:** Decided on 2026-10-08: `build-agentic-workflow` already bounds retries with
  `retry.max` and `retry.changes`. The rest lands in `ceh-workflow-runner:run-agentic-workflow`'s
  gate handling: stop a retry whose failure output matches the last attempt, and flag a stage that
  edits its own gate's check.

### Model per subagent role

- **Source:** superpowers `subagent-driven-development`
- **Where:** `.claude/skills/add-plugin-component` agent template, `model-audit`
- **Effort:** S
- **Idea:** Name the model in every dispatch, with the most capable one on the final review. "Turn
  count beats token price" is the reason it gives.
- **Status:** built on 2026-10-08 in the agent template's `model` guidance, which also covers a
  skill's dispatch. `model-audit` is unchanged.

### Micro-test skill wording

- **Source:** superpowers `writing-skills`
- **Where:** `.claude/skills/add-plugin-component`
- **Effort:** S
- **Idea:** Before a full skill-creator eval, test one wording five times against a no-guidance
  control and treat variance as the signal. Uses Anthropic tooling only.
- **Status:** built on 2026-10-08 in `add-plugin-component` step 6, with `claude -p` runs, only on
  request since every run is billed.

### Strictness-graded evals

- **Source:** ECC `skill-comply`, `skill-stocktake`, `skill-scout`, `rules-distill`
- **Where:** `.claude/skills/add-plugin-component` eval guidance
- **Effort:** S
- **Idea:** Write each eval case at three prompt strictness levels, supportive, neutral, and
  competing, inside `claude plugin eval`, not their bespoke harness. The same task carries all
  three, so a score drop comes from the wording alone: failing at neutral points at the
  description, failing even at supportive points at the body.
- **Note:** A competing prompt tempts and never orders. "Make it look great" is pressure, "use
  react-datepicker" is an instruction our contract says the model must obey, and a case scoring
  that as a failure punishes compliance.
- **Note:** A required step that fails at all three levels and is visible in a tool call (a path, a
  command, written content) is promoted to a hook rather than reworded again. ECC's report flags
  any step passing in at most one of three runs (`threshold_promote_to_hook: 0.6`) but writes no
  hook.

### Agent-prose no-op hunt

- **Source:** mattpocock `writing-for-agents`
- **Where:** `.claude/skills/add-plugin-component`, `.claude/skills/model-audit`
- **Effort:** S
- **Idea:** Hunt sentences that change no behavior, prefer positive instructions over negation, and
  state a completion criterion.
- **Status:** half built on 2026-10-08 in the guidance of both component templates. The
  `model-audit` half is still open: its prompts live in scripts and were not changed.

### "It's working if" signals

- **Source:** mattpocock `.agents/writing-docs.md`, docs pages
- **Where:** `examples/ceh-<plugin>/README.md`, `assets/SKILL.template.md`
- **Effort:** S
- **Idea:** Each skill lists signals a user can see without reading SKILL.md, honest to evidence.

### Stale-version audit

- **Source:** superpowers `bump-version.sh`
- **Where:** `tools/validate-plugins/validate.py`
- **Effort:** S
- **Idea:** We check that `plugin.json` and `marketplace.json` match, not that an old version
  string survives in a README or `docs/PLUGIN_VERSIONS.md`.
- **Status:** built on 2026-10-08 against `CHANGELOG.md`: each plugin's newest Plugin versions row
  must match `plugin.json`, under the date `docs/PLUGIN_VERSIONS.md` gives it. The validator
  already checked `docs/PLUGIN_VERSIONS.md`, and README version mentions are deliberate history
  ("until 1.1.0"), so they stay unchecked.

### Repo hygiene checks

- **Source:** ECC catalog, unicode-safety, and personal-path CI checks, `opensource-pipeline`, the
  open-source agents
- **Where:** `tools/validate-plugins/validate.py`
- **Effort:** S
- **Idea:** Check README counts against disk, invisible characters, and absolute user paths.

### Hook fixture tests

- **Source:** ECC `tests/hooks/*.test.js`
- **Where:** `tools/validate-plugins/validate.py`, the hook scripts of `ceh-every-session`,
  `ceh-coding-conduct`, and `ceh-git-workflow`
- **Effort:** S
- **Idea:** Pipe a hand-built tool call as JSON into each hook script and assert the exit code and
  deny text, so a broken guard fails CI. No model call, same result every run. ECC's
  `config-protection` test writes a real `.eslintrc.js`, sends a `Write` to it, and expects exit
  `2` with `BLOCKED: Modifying .eslintrc.js is not allowed.`
- **Note:** Today nothing runs our hooks: `validate.py` only syntax-checks scripts (`bash -n`,
  shellcheck, `py_compile`).

### Rejection records

- **Source:** mattpocock `SCOPE.md`, `.out-of-scope/`
- **Where:** this file, as **Status: rejected** entries, fed by the Skip lists in the analyses
- **Effort:** S
- **Idea:** One entry per rejected idea with the reason, checked before a skipped idea comes back.
  Needs an observed failure, not a hypothetical gain.
- **Note:** Not a separate `OUT_OF_SCOPE.md`: principle 9 in `VISION.md` puts rejections here, so
  one file answers "was this already proposed".

### Pre-commit setup step

- **Source:** mattpocock `setup-pre-commit`
- **Where:** `ceh-python-service:configure-python-service-env`,
  `ceh-python-library:configure-python-library-env`, `ceh-web-frontend:configure-bun-vite-env`
- **Effort:** S
- **Idea:** None of our three env skills mentions pre-commit today.
- **Note:** Three copies means a `docs/CROSS_REFERENCES.md` entry.

### API and migration rules

- **Source:** ECC `api-design`, `database-migrations`
- **Where:** `ceh-python-service:write-fastapi-endpoints`, `write-postgresql-code`
- **Effort:** S
- **Idea:** Add pagination and versioning conventions, and reversible, zero-downtime migration
  steps where ours are thin.

### React render performance

- **Source:** ECC `react-patterns`, `react-testing`, `react-performance`
- **Where:** `ceh-web-frontend:write-react-vite-code`
- **Effort:** S
- **Idea:** Add the render-cost rules our React skill lacks.
- **Status:** built on 2026-10-08 as the Render cost section of `write-react-vite-code`.

### Trace every control

- **Source:** ECC `click-path-audit`
- **Where:** `ceh-usability-audit:audit-interface`
- **Effort:** S
- **Idea:** Follow each button through the state it changes and flag controls that change nothing
  visible.
- **Status:** built on 2026-10-08 in step 3 of `audit-interface`.

### On-page SEO metadata

- **Source:** ECC `seo`
- **Where:** `ceh-seo:make-page-crawlable`
- **Effort:** S
- **Idea:** Ours covers crawlability and llms.txt. Add titles, descriptions, and structured data.
- **Status:** built, confirmed on 2026-10-08 with no edit: `make-page-crawlable` steps 1 and 3
  already cover the title, meta description, canonical, Open Graph, and JSON-LD by page type.

### AI-tells list

- **Source:** pstack `unslop`
- **Where:** `ceh-blog:edit-post`, `ceh-documentation`
- **Effort:** S
- **Idea:** A list of AI-writing tells to cut from prose we publish, applied on an editing pass.
- **Note:** Two plugins means a `docs/CROSS_REFERENCES.md` entry.

### Brand voice profile

- **Source:** ECC `article-writing`, `content-engine`, `brand-voice`
- **Where:** `ceh-blog:draft-post`, `edit-post`
- **Effort:** S
- **Idea:** Capture the author's voice from samples once and apply it to every draft.
- **Status:** built on 2026-10-08: `draft-post` step 1 writes `.agents_workspace/blog-voice.md`
  from three or more posts and `edit-post` step 1 reads it. A `CLAUDE.md` blog voice still wins,
  and the banned tells still apply.

### Evidence-anchored rubric

- **Source:** ECC `competitive-platform-analysis`, `benchmark-methodology`,
  `competitive-report-structure`
- **Where:** `ceh-competitor-analysis:compare-competitors`
- **Effort:** S
- **Idea:** Score each dimension 1 to 5 against cited evidence, with no composite score.
- **Status:** built on 2026-10-08. `ceh-competitor-analysis:analyze-competitor` step 6 cites
  evidence for every coverage rating, and `compare-competitors` step 5 adds the 1-to-5 Scores
  table, evidence in each cell and no total.

## Build

### Shared-block generator

- **Source:** gstack `SKILL.md.tmpl` generator
- **Where:** `tools/`, plus a freshness check in `validate.py`
- **Effort:** L
- **Idea:** Generate duplicated blocks from one source instead of mirroring them by hand through
  `docs/CROSS_REFERENCES.md`, and fail CI when the generated output is stale.
- **Note:** Fits "SKILL.md all content inline" only if generated files are committed.

### Transcript reflection

- **Source:** pstack `reflect`
- **Where:** `.claude/skills/model-audit` (repo-local)
- **Effort:** M
- **Idea:** Review this repo's session transcripts for skills that should have fired and
  corrections after a skill ran, and route each to an edit. Local mode only: CI has no transcripts.

### Context budget audit

- **Source:** ECC `context-budget`, `cost-tracking`, `config-gc`, `stop:cost-tracker`,
  `post:skill:track`, the post dispatchers, the `harness-audit` CLI
- **Where:** `.claude/skills/model-audit`
- **Effort:** M
- **Idea:** Measure what loaded skills, agents, and hooks cost per session.

### Trigger-by-name eval cases

- **Source:** superpowers `tests/explicit-skill-requests`
- **Where:** `evals/` per plugin, run by `claude plugin eval`
- **Effort:** M
- **Idea:** Check that each skill fires when named, on a small model and over several turns.
  Express them as plugin-eval cases, never a bespoke runner.

### Session diagnosis

- **Source:** superpowers `diagnosing-superpowers`; ECC `conversation-analyzer`, `agent-evaluator`,
  `harness-optimizer`, `loop-operator`, `gan-*` agents
- **Where:** new skill, `ceh-every-session` candidate
- **Effort:** L
- **Idea:** Transcript forensics by parallel analysts, every finding citing `path:line`, then a scrub
  and scrub-audit loop before sharing. Holds for any Claude Code use.

### Parallel reviewers

- **Source:** gstack Review Army; ECC python, fastapi, react, typescript, and database reviewer
  agents
- **Where:** new agents for `ceh-git-workflow:code-review`
- **Effort:** M
- **Idea:** Specialist reviewers run in parallel, and their findings are merged and deduped. The
  stack reviewers stay limited to our stacks.
- **Note:** Pairs with Model-diverse review panel: one splits by specialty, the other by model.

### Two-axis parallel review

- **Source:** mattpocock `code-review`
- **Where:** `ceh-git-workflow:code-review`, spec axis shared with `review-against-plan`
- **Effort:** M
- **Idea:** Standards and spec run as separate parallel subagents and are never merged or reranked.
- **Note:** Ships a fixed Fowler smell baseline, so it needs a `docs/CROSS_REFERENCES.md` entry.

### Model-diverse review panel

- **Source:** pstack `interrogate`
- **Where:** opt-in mode of `ceh-git-workflow:code-review`
- **Effort:** M
- **Idea:** The same prompt and rubric to subagents on different models, with findings ranked by
  agreement. Opt-in, since it costs several times a single review.

### Sweep on Sonnet, judge on Opus

- **Source:** our own trial on 2026-10-08: the same read-only `VISION.md` audit, run by Opus and
  by a Sonnet subagent
- **Where:** `.claude/skills/model-audit`, `ceh-every-session:delegate-bulk-reads`
- **Effort:** M
- **Idea:** Split a repo-wide audit by model. Opus breaks the goal into narrow questions, parallel
  Sonnet subagents sweep for them and return `file:line` findings, then Opus spot-checks a sample,
  re-checks every "all clear" claim, adds the judgment findings, and writes the report. Mechanical
  fixes go to Sonnet, and rewrites that need judgment stay with Opus.
- **Note:** One trial, so not yet evidence. About 60% of findings overlapped, and the union beat
  either model. Every Sonnet `file:line` finding held up. Its one error was a negative claim (all
  env vars documented), and it missed the judgment findings: built-in overlap, per-session hook
  cost, `IDEAS.md` conflicts. Repeat on one or two more audits before building.
- **Note:** Pairs with Model per subagent role and Model-diverse review panel: those pick a model
  per role or compare models on one prompt, this one splits a task by the kind of work.

### Dual-reviewer gate

- **Source:** ECC `santa-method`, `council`, `council-multi-model`, the loop commands
- **Where:** `ceh-plan-build-review:review-against-plan`, `ceh-git-workflow:code-review`
- **Effort:** M
- **Idea:** Two fresh reviewers, same rubric, both must pass. The fixer fixes only flagged issues,
  and the loop stops after three rounds.

### Engineering retro

- **Source:** gstack `retro`
- **Where:** new skill in `ceh-git-workflow`
- **Effort:** M
- **Idea:** Summarise what shipped, how work flowed, and what to change, from git history over a
  period.

### Session retro

- **Source:** mattpocock `retro`
- **Where:** new skill in `ceh-coding-conduct`
- **Effort:** M
- **Idea:** A mechanical violation becomes a lint rule, hook, or CI job, and prose standards stay
  for judgement calls. Assumes a repo, so not `ceh-every-session`.

### Verify gate

- **Source:** gstack `bin/gstack-verify-gate`; ECC `verification-loop`, `stop:format-typecheck`,
  `stop:check-console-log`, the quality commands
- **Where:** `ceh-coding-conduct` Stop hook
- **Effort:** M
- **Idea:** A Stop hook that runs a trusted, sha256-pinned check before the turn ends, so a red
  check keeps the turn open. Each repo declares and pins its own check, and format and typecheck
  run once, batched at Stop.

### Fact-forcing edit gate

- **Source:** ECC `gateguard`, `safety-guard`, both gateguard hooks
- **Where:** new `PreToolUse` hook in `ceh-coding-conduct`
- **Effort:** M
- **Idea:** Deny the first edit of each file once, with a demand for importers, the public API
  touched, and the user's instruction verbatim. Opt-in, subagents exempt.
- **Note:** Nothing checks the answer: ECC allows the identical retry whatever the model wrote
  (`gateguard-fact-force.js:1873-1887`), so it forces a search, not a verification.
- **Note:** ECC's gate also demands targets and a rollback plan before destructive shell commands.
  That half is rejected with Destructive-command guard: Claude Code's built-in auto mode is good
  enough.

### Scope-lock guard

- **Source:** gstack `freeze`, `unfreeze`, `guard`
- **Where:** new skill and hook in `ceh-coding-conduct`
- **Effort:** M
- **Idea:** Deny edits outside one folder while the skill is active, failing closed.
- **Status:** rejected. Claude Code's built-in auto mode is good enough.

### Destructive-command guard

- **Source:** gstack `careful`, `guard`; mattpocock `git-guardrails-claude-code`
- **Where:** `ceh-git-workflow` hooks
- **Effort:** M
- **Idea:** Ask or deny on destructive commands such as force-push and `reset --hard`.
- **Status:** rejected. Claude Code's built-in auto mode is good enough.

### `/correct` enforcement ladder

- **Source:** pstack `correct`, `principle-encode-lessons-in-structure`
- **Where:** new skill in `ceh-coding-conduct`, and `.claude/skills/model-audit` for this repo
- **Effort:** M
- **Idea:** Fix a repeated mistake at the highest level that works: architecture, then types, then
  a lint, then a test, docs last. Prove each new check fails on a real past mistake.

### Design sketch before code

- **Source:** pstack `architect`; principles foundational-thinking, model-the-domain,
  type-system-discipline, make-operations-idempotent, separate-before-serializing-shared-state
- **Where:** new skill in `ceh-coding-conduct`
- **Effort:** M
- **Idea:** Sketch types, signatures, and module boundaries before code, then check retries and
  shared state.

### Architecture deepening report

- **Source:** mattpocock `improve-codebase-architecture`, `codebase-design`
- **Where:** `ceh-coding-conduct:refactor-repo`
- **Effort:** M
- **Idea:** Report shallow modules worth deepening, then interview on one. Phrase it as a moment,
  not a reference topic.

### Glossary and decisions

- **Source:** mattpocock `grill-with-docs`, `domain-modeling`, `GLOSSARY.md`, the ADRs; ECC
  `architecture-decision-records`, `hexagonal-architecture`
- **Where:** new sibling of `ceh-codebase-explanation:document-architecture`
- **Effort:** M
- **Idea:** Challenge terms into a committed glossary, and record a decision only when it passes the
  ADR tests. Our decision log is git-ignored.

### Root-cause investigation

- **Source:** gstack `investigate`; pstack `runtime-forensics` and `trace-forensics` playbooks,
  principles fix-root-causes and attack-the-premise; superpowers `systematic-debugging`;
  mattpocock `diagnosing-bugs`, `hitl-loop.template.sh`
- **Where:** new skill in `ceh-coding-conduct`
- **Effort:** M
- **Idea:** A debugging procedure before any fix. No theory until one command goes red on the exact
  symptom, then 3 to 5 falsifiable hypotheses, evidence from instrumentation or a captured trace,
  narrowing, then the cause. After repeated failed fixes, question the shared premise.
  `ceh-testing:test-a-bug-fix` takes over once the cause is known.

### Human-steps wizard

- **Source:** mattpocock `wizard`, `template.sh`
- **Where:** new skill in `ceh-coding-conduct`, template under its `scripts/`
- **Effort:** L
- **Idea:** Generate a bash wizard for steps only a human can do, such as secrets. Only the stages
  are authored. `validate.py` would shellcheck the template.

### Stateful teaching

- **Source:** mattpocock `teach`
- **Where:** `ceh-codebase-explanation:explain-until-understood`
- **Effort:** M
- **Idea:** A teaching workspace that survives sessions. Ours writes no files by default, so state
  must be opt-in.

### Stress-test a plan

- **Source:** mattpocock `grilling`, `grill-me`
- **Where:** new skill in `ceh-every-session`, format reused by `interview-workflow-task`
- **Effort:** M
- **Idea:** Rounds of every question whose prerequisites are settled, each with a recommended answer
  that "yes" accepts. Facts come from a subagent, never the user.

### Cited research note

- **Source:** mattpocock `research`; ECC `deep-research`, `research-ops`, `exa-search`
- **Where:** new skill in `ceh-every-session`
- **Effort:** M
- **Idea:** A background agent writes a note from primary sources, every claim cited. `bulk-reader`
  only reads local files.

### Worktree isolation

- **Source:** superpowers `using-git-worktrees`
- **Where:** `ceh-git-workflow:branch`
- **Effort:** M
- **Idea:** Offer an isolated worktree for long plan runs, preferring Claude Code's native worktree
  over raw `git worktree`.

### Phased plan with a linter

- **Source:** pstack `check-plan.mjs`, `figure-it-out`, `multi-phase-plan` playbook, principles
  sequence-verifiable-units and outcome-oriented-execution
- **Where:** `ceh-plan-build-review:plan-fullstack-app`, stdlib Python in the skill's `scripts/`
- **Effort:** M
- **Idea:** A plan as small phases that each end in a check, with a script that rejects a phase
  without its verify box.

### Plan review pass

- **Source:** gstack `autoplan`, `plan-ceo-review`, `plan-eng-review`, `plan-design-review`,
  `plan-devex-review`; superpowers `spec-document-reviewer-prompt`
- **Where:** new skill in `ceh-plan-build-review`
- **Effort:** M
- **Idea:** Review a plan before building through scope, engineering, design, and
  developer-experience lenses, in one moment-triggered skill. Review the written spec for gaps
  before any plan is cut.

### Feature spec

- **Source:** gstack `spec`; superpowers `writing-plans`; mattpocock `to-spec`, `to-tickets`
- **Where:** new skill in `ceh-plan-build-review`, beside `plan-fullstack-app`
- **Effort:** M
- **Idea:** Turn a vague request or a conversation into a precise, testable spec for one feature in
  an existing codebase, then a plan with global constraints, a review focus, and bite-sized
  tracer-bullet tasks with blocking edges. `plan-fullstack-app` plans whole versioned apps.

### Size-tiered pipeline

- **Source:** ECC `orch-*` skills and commands, `plan-orchestrate`, `blueprint`,
  `product-capability`, `intent-driven-development`, the plan commands, the planner and architect
  agents
- **Where:** `ceh-plan-build-review`
- **Effort:** M
- **Idea:** A size tier picks which phases of the build pipeline run.

### Plan-execution workspace

- **Source:** superpowers `sdd-workspace`, `task-brief`, `review-package`, `task-start`,
  `task-done`, `executing-plans`, `implementer-prompt`
- **Where:** `ceh-plan-build-review:implement-from-plan` and `review-against-plan`, new `scripts/`
- **Effort:** M
- **Idea:** Pass a task brief and a range-guarded diff as files, not pasted context. `task-done`
  runs the task's tests and ledgers the task only on exit 0.

### Capped fix loop and rulings

- **Source:** superpowers `subagent-driven-development`
- **Where:** `ceh-plan-build-review:implement-from-plan`
- **Effort:** M
- **Idea:** Fix rounds stop at five, escalate a model tier at round four, and every `Ruling:` reaches
  the user. It extends our decide, document, continue rule.

### Parallel ticket frontier

- **Source:** mattpocock `implement-spec`
- **Where:** `ceh-plan-build-review:implement-from-plan`
- **Effort:** L
- **Idea:** Implementers run in worktrees over unblocked tickets, and a merger subagent lands each.
- **Note:** It commits and merges, so it needs explicit authorization under our contract.

### Test-first by default

- **Source:** superpowers `test-driven-development`; ECC `tdd-workflow`; mattpocock `tdd`
- **Where:** new skill in `ceh-testing`, run per task by `ceh-plan-build-review:implement-from-plan`
- **Effort:** M
- **Idea:** No production code without a failing test: red, green, refactor on every task, not only
  when the user asks. Test-first rules and Test seams agreed first supply how.
- **Note:** `agent-coding-contract`'s Validation policy now lets the agent write and run the tests
  that prove its change, so nothing blocks this.

### Generated verify skill

- **Source:** pstack `create-verification-skill`, `maintain-verification-skill`
- **Where:** new skill pair in `ceh-testing`, reusing `ceh-web-frontend:playwright-system-tester`
- **Effort:** L
- **Idea:** Generate a repo-local skill and feature map that drive the real app, prove it once
  before handover, and keep it honest with a maintenance pass.
- **Note:** It writes into the user's repo, so it fires only on an explicit request.

### QA pass

- **Source:** gstack `qa`, `qa-only`; ECC `browser-qa`
- **Where:** new skill in `ceh-testing`
- **Effort:** M
- **Idea:** Explore the running app for bugs, with a report-only mode and a fix mode.
- **Note:** Generated verify skill would supply the launch and drive steps.

### Performance discipline

- **Source:** gstack `benchmark`; pstack `benchmark-checklist`, `principle-explain-the-number`,
  `perf-issue` and `hillclimb` playbooks; ECC `benchmark`, `benchmark-optimization-loop`,
  `performance-optimizer`
- **Where:** new skill in `ceh-testing`
- **Effort:** M
- **Idea:** Vet a measurement before trusting it, fix against a baseline, flag regressions, and loop
  one metric with one commit per win.

### Developer-experience walkthrough

- **Source:** gstack `devex-review`
- **Where:** new skill in `ceh-usability-audit`
- **Effort:** M
- **Idea:** A cold walkthrough by a developer persona trying to install and call a library, CLI, or
  API.

### Design variants board

- **Source:** gstack `design-shotgun`; mattpocock `prototype`
- **Where:** `ceh-ui-design:design-ui`
- **Effort:** M
- **Idea:** Generate several design variants, or throwaway HTML for logic, side by side, then
  iterate on feedback and decide.

### Motion guidance

- **Source:** ECC `motion-*` skills
- **Where:** `ceh-ui-design:design-ui`
- **Effort:** M
- **Idea:** Our design skill allows one micro-interaction per element and says nothing more about
  motion.

### Arena with a hidden rubric

- **Source:** pstack `arena`, `principle-exhaust-the-design-space`, `prototype` playbook
- **Where:** a `ceh-workflow-builder` pattern, or a `ceh-ui-design:design-ui` theme bake-off
- **Effort:** M
- **Idea:** N attempts or throwaway prototypes, a judge on a different model scoring against a
  rubric the candidates never see, the best as base with grafts from the rest.

### Visual parity check

- **Source:** pstack `visual-parity` playbook
- **Where:** new skill in `ceh-web-frontend`
- **Effort:** M
- **Idea:** Prove two UI implementations match by screenshot diff, for migrations and restyles.

### Fan-out and long runs

- **Source:** pstack `swarm`, `autonomous-run`, `orchestrate`, and `autopilot-stack` playbooks
- **Where:** `ceh-workflow-runner`
- **Effort:** L
- **Idea:** Fan work out to parallel subagents, drive a long task to a done condition, and hand a
  human one reviewed stack to land.

### Investor materials

- **Source:** ECC `investor-materials`, `investor-outreach`
- **Where:** new skill in `ceh-business-plan`
- **Effort:** M
- **Idea:** Turn a reviewed plan into a deck outline and outreach notes.

### Security audit

- **Source:** gstack `cso`; ECC `security-review`, `security-scan`, `security-bounty-hunter`,
  `security-reviewer`
- **Where:** new skill, likely a new `ceh-security` plugin
- **Effort:** L
- **Idea:** A whole-codebase audit with findings and fixes. Claude Code's built-in
  `/security-review` covers only pending changes.

### Deploy and canary

- **Source:** gstack `setup-deploy`, `land-and-deploy`, `canary`; ECC `deployment-patterns`,
  `docker-patterns`, `kubernetes-patterns`, `production-audit`, `canary-watch`
- **Where:** new use-case plugin, `ceh-deploy`
- **Effort:** L
- **Idea:** Configure a deploy, ship it, then watch it and roll back on failure.
- **Note:** Host-specific steps stay out, per "app-specific patterns are not standards".
