# Ideas Backlog

Ideas taken from the gstack and pstack competitor analyses of 2026-10-07 ("What we take": Adopt
now and Build). Together they cover every competitor skill, agent, and workflow that our work
covers only partly or not at all, except what each analysis put under Skip. Nothing here is
committed work, and an entry marked **Status: rejected** stays listed so it is not proposed again.
Where both competitors do the same job, the ideas are merged into one entry.

Effort: S is under a day, M is a few days, L is longer.

## Adopt now

### Description size cap

- **Source:** gstack `test/catalog-budget.test.ts`
- **Where:** `tools/validate-plugins/validate.py`
- **Effort:** S
- **Idea:** A per-description byte cap plus a ratcheted total keeps skill-catalog cost bounded.
  gstack caps each description at 260 bytes. Ours run from 63 to 1,058 bytes, median 693.

### Lead-judgment buckets

- **Source:** pstack `interrogate`
- **Where:** `ceh-git-workflow:code-review`
- **Effort:** S
- **Idea:** Sort findings into Act On, Consider, Noted, and Dismissed, with at most 5 Act On items,
  and keep Dismissed with reasons so the user can override it.

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

### Patch-id re-check

- **Source:** pstack `shipping` playbook
- **Where:** `ceh-git-workflow:pull-request` (land step)
- **Effort:** S
- **Idea:** Record the `git patch-id` a review or test run saw, and compare it again before landing.
  A rebase can invalidate a review without touching a check.

### PR babysit loop

- **Source:** pstack `babysit` playbook
- **Where:** `ceh-git-workflow:pull-request`
- **Effort:** S
- **Idea:** A loop that clears conflicts, review threads, and red CI one PR at a time, stopping where
  a human call begins.

### Worktree cleanup

- **Source:** pstack `worktree-cleanup` playbook
- **Where:** `ceh-git-workflow:pull-request` (post-merge cleanup)
- **Effort:** S
- **Idea:** Prune merged or abandoned git worktrees, asking before any deletion.

### Docs drift check

- **Source:** gstack `document-release`
- **Where:** `ceh-git-workflow:update-readme`
- **Effort:** S
- **Idea:** After a change lands, compare what the docs claim with what the diff shipped, not only
  whether the README mentions the feature.

### Certainty ladder

- **Source:** pstack `blast-radius`, `principle-prove-it-works`
- **Where:** `ceh-testing:verify-behavior-preserved`
- **Effort:** S
- **Idea:** Name the one fact a change's safety rests on and prove it at the highest rung that is
  cheap: said so, pointed at a line, walked the failure, ran code, reproduced in the app.

### Test value line

- **Source:** gstack `docs/test-value-bar.md`
- **Where:** `ceh-testing:design-test-cases`, `test-a-bug-fix`, `audit-test-suite`
- **Effort:** S
- **Idea:** Each new test states `protects`, `fails_when`, and `why_new`.

### Test-first on request

- **Source:** pstack `tdd`, `principle-test-behavior-not-implementation`
- **Where:** `ceh-testing:design-test-cases`, `test-a-bug-fix`
- **Effort:** S
- **Idea:** When the user asks for test-first, write the failing test first, call the code the way
  users do, and assert literal expected values.

### One-way-door list

- **Source:** gstack one-way-door registry
- **Where:** `ceh-coding-agent:agent-coding-contract`, Stop conditions
- **Effort:** S
- **Idea:** A concrete list of questions that are never auto-decided, giving our "stop on
  irreversible impact" rule teeth.

### Build the lever

- **Source:** pstack `principle-build-the-lever`
- **Where:** `ceh-coding-agent:agent-coding-contract`
- **Effort:** S
- **Idea:** For bulk or repeated work, write the script or codemod that does or checks it instead
  of editing by hand.

### Structural rules

- **Source:** pstack principles boundary-discipline, minimize-reader-load,
  migrate-callers-then-delete-legacy-apis, redesign-from-first-principles
- **Where:** `ceh-coding-agent:refactor-repo`, `write-less-code`
- **Effort:** S
- **Idea:** Add these as rules inside our existing skills rather than as skills of their own.

### Design red-flag screen

- **Source:** pstack `architect`
- **Where:** `ceh-coding-agent:refactor-repo` or `document-architecture`
- **Effort:** S
- **Idea:** Screen a design for Ousterhout's red flags: shallow module, information leakage,
  pass-through method.

### Rationale from history

- **Source:** pstack `why`, `investigation` playbook
- **Where:** `ceh-coding-agent:explain-codebase`, `explain-until-understood`
- **Effort:** S
- **Idea:** Answer "why is it like this" from git log, blame, and PRs, with every claim cited.

### Evidence label per claim

- **Source:** pstack `poteto-mode`
- **Where:** `ceh-coding-agent` output style
- **Effort:** S
- **Idea:** Every claim carries measured, inferred, or guess in the same sentence.

### Comment audit

- **Source:** pstack `no-comments`, `comment-sicko` agent
- **Where:** new read-only agent in `ceh-coding-agent`
- **Effort:** S
- **Idea:** Flag comments that restate the code or excuse a workaround, and offer to encode real
  constraints in types or checks instead.

### Save and restore on demand

- **Source:** gstack `context-save`, `context-restore`; pstack `recall`, `session-pickup` and
  `pause-safely` playbooks
- **Where:** `ceh-core:usage-limit-handoff`
- **Effort:** S
- **Idea:** The handoff writes a resume point only near the usage limit. Let it also fire on "save
  where we are" and "pick this up".

### `skip: <reason>` rows

- **Source:** pstack `poteto-mode`
- **Where:** `ceh-workflow-runner:run-agentic-workflow`, `ceh-plan-build-review:implement-from-plan`
- **Effort:** S
- **Idea:** Copy the steps into the task list verbatim and keep a skipped step visible as
  `skip: <reason>`.

### Skill from this session

- **Source:** gstack `skillify`
- **Where:** `ceh-workflow-builder:build-agentic-workflow`
- **Effort:** S
- **Idea:** Add the moment "turn what we just did into a skill", building from the steps that
  worked in this session instead of an interview.

### AI-tells list

- **Source:** pstack `unslop`
- **Where:** `ceh-blog:edit-post`, `ceh-documentation`
- **Effort:** S
- **Idea:** A list of AI-writing tells to cut from prose we publish, applied on an editing pass.
- **Note:** Two plugins means a `docs/CROSS_REFERENCES.md` entry.

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

### Parallel reviewers

- **Source:** gstack Review Army
- **Where:** new agents for `ceh-git-workflow:code-review`
- **Effort:** M
- **Idea:** Specialist reviewers run in parallel, and their findings are merged and deduped.
- **Note:** Pairs with Model-diverse review panel: one splits by specialty, the other by model.

### Model-diverse review panel

- **Source:** pstack `interrogate`
- **Where:** opt-in mode of `ceh-git-workflow:code-review`
- **Effort:** M
- **Idea:** The same prompt and rubric to subagents on different models, with findings ranked by
  agreement. Opt-in, since it costs several times a single review.

### Engineering retro

- **Source:** gstack `retro`
- **Where:** new skill in `ceh-git-workflow`
- **Effort:** M
- **Idea:** Summarise what shipped, how work flowed, and what to change, from git history over a
  period.

### Opt-in verify gate

- **Source:** gstack `bin/gstack-verify-gate`
- **Where:** `ceh-coding-agent` hooks
- **Effort:** M
- **Idea:** A Stop hook that runs a trusted, sha256-pinned check before the turn ends.
- **Note:** Conflicts with "don't run tests unless asked" unless it stays opt-in per repo.

### Scope-lock guard

- **Source:** gstack `freeze`, `unfreeze`, `guard`
- **Where:** new skill and hook in `ceh-coding-agent`
- **Effort:** M
- **Idea:** Deny edits outside one folder while the skill is active, failing closed.
- **Status:** rejected. Claude Code's built-in auto mode is good enough.

### Destructive-command guard

- **Source:** gstack `careful`, `guard`
- **Where:** `ceh-git-workflow` hooks
- **Effort:** M
- **Idea:** Ask or deny on destructive commands such as force-push and `reset --hard`.
- **Status:** rejected. Claude Code's built-in auto mode is good enough.

### `/correct` enforcement ladder

- **Source:** pstack `correct`, `principle-encode-lessons-in-structure`
- **Where:** new skill in `ceh-coding-agent`, and `.claude/skills/model-audit` for this repo
- **Effort:** M
- **Idea:** Fix a repeated mistake at the highest level that works: architecture, then types, then
  a lint, then a test, docs last. Prove each new check fails on a real past mistake.

### Design sketch before code

- **Source:** pstack `architect`; principles foundational-thinking, model-the-domain,
  type-system-discipline, make-operations-idempotent, separate-before-serializing-shared-state
- **Where:** new skill in `ceh-coding-agent`
- **Effort:** M
- **Idea:** Sketch types, signatures, and module boundaries before code, then check retries and
  shared state.

### Root-cause investigation

- **Source:** gstack `investigate`; pstack `runtime-forensics` and `trace-forensics` playbooks,
  principles fix-root-causes and attack-the-premise
- **Where:** new skill in `ceh-coding-agent`
- **Effort:** M
- **Idea:** A debugging procedure before any fix: hypotheses, evidence from instrumentation or a
  captured trace, narrowing, then the cause. After repeated failed fixes, question the shared
  premise. `ceh-testing:test-a-bug-fix` takes over once the cause is known.

### Phased plan with a linter

- **Source:** pstack `check-plan.mjs`, `figure-it-out`, `multi-phase-plan` playbook, principles
  sequence-verifiable-units and outcome-oriented-execution
- **Where:** `ceh-plan-build-review:plan-fullstack-app`, stdlib Python in the skill's `scripts/`
- **Effort:** M
- **Idea:** A plan as small phases that each end in a check, with a script that rejects a phase
  without its verify box.

### Plan review pass

- **Source:** gstack `autoplan`, `plan-ceo-review`, `plan-eng-review`, `plan-design-review`,
  `plan-devex-review`
- **Where:** new skill in `ceh-plan-build-review`
- **Effort:** M
- **Idea:** Review a plan before building through scope, engineering, design, and
  developer-experience lenses, in one moment-triggered skill.

### Feature spec

- **Source:** gstack `spec`
- **Where:** new skill in `ceh-plan-build-review`
- **Effort:** M
- **Idea:** Turn a vague request into a precise, testable spec for one feature in an existing
  codebase.

### Generated verify skill

- **Source:** pstack `create-verification-skill`, `maintain-verification-skill`
- **Where:** new skill pair in `ceh-testing`, reusing `ceh-web-frontend:playwright-system-tester`
- **Effort:** L
- **Idea:** Generate a repo-local skill and feature map that drive the real app, prove it once
  before handover, and keep it honest with a maintenance pass.
- **Note:** It writes into the user's repo, so it fires only on an explicit request.

### QA pass

- **Source:** gstack `qa`, `qa-only`
- **Where:** new skill in `ceh-testing`
- **Effort:** M
- **Idea:** Explore the running app for bugs, with a report-only mode and a fix mode.
- **Note:** Generated verify skill would supply the launch and drive steps.

### Performance discipline

- **Source:** gstack `benchmark`; pstack `benchmark-checklist`, `principle-explain-the-number`,
  `perf-issue` and `hillclimb` playbooks
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

- **Source:** gstack `design-shotgun`
- **Where:** `ceh-ui-design:design-ui`
- **Effort:** M
- **Idea:** Generate several design variants side by side and iterate on feedback.

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

### Security audit

- **Source:** gstack `cso`
- **Where:** new skill, likely a new `ceh-security` plugin
- **Effort:** L
- **Idea:** A whole-codebase audit with findings and fixes. Claude Code's built-in
  `/security-review` covers only pending changes.

### Deploy and canary

- **Source:** gstack `setup-deploy`, `land-and-deploy`, `canary`
- **Where:** new use-case plugin, `ceh-deploy`
- **Effort:** L
- **Idea:** Configure a deploy, ship it, then watch it and roll back on failure.
- **Note:** Host-specific steps stay out, per "app-specific patterns are not standards".
