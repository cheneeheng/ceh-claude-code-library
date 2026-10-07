# Ideas Backlog

Ideas taken from the gstack and pstack competitor analyses of 2026-10-07 ("What we take": Adopt
now and Build). Nothing here is committed work.

Effort: S is under a day, M is a few days, L is longer.

## Adopt now

### Lead-judgment buckets

- **Source:** pstack `/interrogate`
- **Where:** `ceh-git-workflow:code-review`
- **Effort:** S
- **Idea:** Sort findings into Act On, Consider, Noted, and Dismissed, with at most 5 Act On items,
  and keep Dismissed with reasons so the user can override it. It sits on top of our existing
  blocking/advisory split.

### Certainty ladder

- **Source:** pstack `/blast-radius`
- **Where:** `ceh-testing:verify-behavior-preserved`
- **Effort:** S
- **Idea:** Name the one fact a change's safety rests on and prove it at the highest rung reachable:
  said so, pointed at a line, walked the failure, ran code, reproduced in the app. It fires on a
  moment: "I don't trust this small diff".

### `skip: <reason>` rows

- **Source:** pstack `poteto-mode`
- **Where:** `ceh-workflow-runner:run-agentic-workflow`, `ceh-plan-build-review:implement-from-plan`
- **Effort:** S
- **Idea:** Copy the steps into the task list verbatim and keep a skipped step visible as
  `skip: <reason>`, so no step disappears silently.

### Patch-id re-check

- **Source:** pstack shipping playbook
- **Where:** `ceh-git-workflow:pull-request` (land step)
- **Effort:** S
- **Idea:** Record the `git patch-id` a review or test run saw, and compare it again before landing.
  A rebase can invalidate a review without touching a check.
- **Note:** Not a release mechanism, so no conflict with the no-releases rule.

### Design red-flag screen

- **Source:** pstack `architect`
- **Where:** `ceh-coding-agent:refactor-repo` or `document-architecture`
- **Effort:** S
- **Idea:** Screen a design for Ousterhout's red flags: shallow module, information leakage,
  pass-through method.
- **Note:** Register it in `docs/CROSS_REFERENCES.md` if it lands in both skills.

### Evidence label per claim

- **Source:** pstack `poteto-mode`
- **Where:** `ceh-coding-agent` output style
- **Effort:** S
- **Idea:** Every claim carries measured, inferred, or guess in the same sentence. Our Status column
  does this per topic, and this extends it to each claim.

### Description size cap

- **Source:** gstack `test/catalog-budget.test.ts`
- **Where:** `tools/validate-plugins/validate.py`
- **Effort:** S
- **Idea:** A per-description byte cap plus a ratcheted total keeps skill-catalog cost bounded.
  gstack caps each description at 260 bytes. Ours run from 63 to 1,058 bytes, median 693.
- **Note:** Stdlib-only, so it fits the validator.

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
- **Idea:** Compare the stated intent with the actual diff before judging code quality. Fits our
  minimal-diff rule and `ceh-coding-agent:shrink-diff`.

### Test value line

- **Source:** gstack `docs/test-value-bar.md`
- **Where:** `ceh-testing:design-test-cases`, `test-a-bug-fix`, `audit-test-suite`
- **Effort:** S
- **Idea:** Each new test states `protects`, `fails_when`, and `why_new`. Stack-agnostic, so it
  belongs in `ceh-testing`.

### One-way-door list

- **Source:** gstack one-way-door registry
- **Where:** `ceh-coding-agent:agent-coding-contract`, Stop conditions
- **Effort:** S
- **Idea:** A concrete list of questions that are never auto-decided. Our contract already stops on
  irreversible impact, and the list gives that rule teeth.

## Build

### Generated verify skill

- **Source:** pstack `/create-verification-skill`, `/maintain-verification-skill`
- **Where:** new skill pair in `ceh-testing`, reusing `ceh-web-frontend:playwright-system-tester`
- **Effort:** L
- **Idea:** Generate a repo-local skill and feature map that drive the real app, prove it once
  before handover, and keep it honest with a maintenance pass.
- **Note:** It writes into the user's repo, so it fires only on an explicit request.

### `/correct` enforcement ladder

- **Source:** pstack `/correct`
- **Where:** new skill in `ceh-coding-agent`, and `.claude/skills/model-audit` for this repo
- **Effort:** M
- **Idea:** Fix a repeated mistake at the highest level that works: architecture, then types, then a
  lint, then a test, docs last. Prove each new check fails on a real past mistake. Matches how we
  already push rules into `validate.py`.

### Plan linter

- **Source:** pstack `check-plan.mjs`
- **Where:** `ceh-plan-build-review:plan-fullstack-app`, as stdlib Python in the skill's `scripts/`
- **Effort:** M
- **Idea:** A script that makes a plan carry its verify boxes, called from the skill body.

### Arena with a hidden rubric

- **Source:** pstack `/arena`
- **Where:** a `ceh-workflow-builder` pattern, or a `ceh-ui-design:design-ui` theme bake-off
- **Effort:** M
- **Idea:** N attempts at the same task, a judge on a different model scoring against a rubric the
  candidates never see, the best as base with grafts from the rest.
- **Note:** Claude Code cannot mix vendors, so an Opus-vs-Sonnet judge is a weaker version.

### Opt-in verify gate

- **Source:** gstack `bin/gstack-verify-gate`
- **Where:** `ceh-coding-agent` hooks
- **Effort:** M
- **Idea:** A Stop hook that runs a trusted, sha256-pinned check before the turn ends. Editing the
  command revokes trust.
- **Note:** Conflicts with "don't run tests unless asked" unless it stays opt-in per repo.

### Parallel reviewers

- **Source:** gstack Review Army
- **Where:** new agents for `ceh-git-workflow:code-review`
- **Effort:** M, could grow to L
- **Idea:** Specialist reviewers run in parallel, and their findings are merged and deduped. Worth
  the cost only on large diffs.

### Shared-block generator

- **Source:** gstack `SKILL.md.tmpl` generator
- **Where:** `tools/`, plus a freshness check in `validate.py`
- **Effort:** L
- **Idea:** Generate duplicated blocks from one source instead of mirroring them by hand through
  `docs/CROSS_REFERENCES.md`, and fail CI when the generated output is stale.
- **Note:** Fits "SKILL.md all content inline" only if generated files are committed and CI diffs
  them.
