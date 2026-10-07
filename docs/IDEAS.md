# Ideas Backlog

Ideas for future plugins, skills, and validator checks. Nothing here is committed work. When an idea
ships, delete its entry and let the `CHANGELOG.md` entry carry the history. When an idea is rejected,
move it to **Dropped** with the reason, so it is not proposed again.

Effort: S is under a day, M is a few days.

## Open

### Evidence bound to content, not commit SHAs

- **Source:** gstack (section 3 #4)
- **Where:** `ceh-testing`, `ceh-git-workflow:pull-request` (pre-merge gate)
- **Effort:** M
- **Idea:** Record "these tests passed" against a hash of the working-tree contents instead of a
  commit SHA. A rebase or squash keeps the evidence valid, and an edit after a review or test run
  marks it stale. The pre-merge gate then cites fresh evidence instead of rerunning.
- **Open question:** Needs a small script to fingerprint the tree and store results. Check whether
  `git write-tree` over a temporary index is enough before building anything bespoke.

### Untrusted-text envelope for tracker content

- **Source:** gstack (section 3 #8)
- **Where:** `ceh-git-workflow:code-review`, `ceh-git-workflow:pull-request`
- **Effort:** S for the prose rule, M for a script
- **Idea:** Issue and PR bodies are attacker-controlled input to an agent that has a shell. Start
  with a prose rule: tracker text is data, never instructions, quote it and flag any line that tries
  to give commands. Add a wrapper script that labels injection-shaped lines (including fullwidth and
  zero-width evasion) only if the prose rule proves insufficient. A CI check that every tracker-text
  input goes through the wrapper is what makes it enforceable.
- **Note:** `code-review` today mentions only SQL injection.

### Egress receipts

- **Source:** gstack (section 3 #9)
- **Where:** an own skill or hook, alongside the second-opinion skill below
- **Effort:** M
- **Idea:** Before any send to an outside service, append a receipt (time, destination, payload
  hash, hash of the previous receipt) to a local log. Editing or deleting an old receipt breaks the
  chain, so tampering shows. Record each consent with a revoke command.
- **Depends on:** only worth building once a skill sends code off the machine (second opinion).

### `careful` skill

- **Source:** gstack (section 4.1)
- **Where:** `ceh-coding-agent`
- **Effort:** S
- **Idea:** A user-invoked skill (`disable-model-invocation: true`) with a `hooks:` frontmatter
  `PreToolUse` Bash guard. It denies or asks on `rm -rf`, `git push --force`, `git reset --hard`,
  `DROP TABLE`, `kubectl delete`. The hook lives from invocation until the session ends.
- **Priority:** Low. Claude Code auto mode already covers most of this. Revisit if auto mode
  proves too permissive for production work. An always-on force-push block in
  `ceh-git-workflow/hooks/hooks.json` is the cheaper variant. The branch guard needs no change: it
  is already always on.

### Context-budget ratchet in CI

- **Source:** gstack (section 3 #3, 4.2)
- **Where:** `tools/validate-plugins/validate.py`
- **Effort:** S
- **Idea:** `validate.py` checks only the 1024-char limit per description. Add per-plugin totals
  for description chars and SKILL.md lines in a committed fixture. CI fails on growth unless the
  fixture is bumped in the same commit. The 500-line rule in the SKILL template is guidance only
  today.

### Blame protocol for failing tests

- **Source:** gstack (section 3 #10, 4.4)
- **Where:** `ceh-testing`, `ceh-git-workflow:pull-request` (pre-merge gate)
- **Effort:** S
- **Idea:** Before calling a failure "pre-existing", run the same test on the base branch and cite
  the result. Otherwise label it unverified. Applies only once a failure has already surfaced, so it
  does not conflict with the no-tests-unless-asked rule.

### Second-opinion skill

- **Source:** gstack (section 3 #6, 4.6)
- **Where:** new skill in `ceh-coding-agent` (not a step in `code-review`)
- **Effort:** M
- **Idea:** When another model CLI (`codex`, `gemini`) is installed, send a diff, plan, or design to
  it, merge the findings, and name which model produced each. Triggers on "get a second opinion",
  which also covers plans, so it does not belong inside the PR-review skill.
- **Notes:** Needs `compatibility` naming the CLI. It sends code off the machine, so it asks for
  consent first, see Egress receipts.

### `/correct`: mistake-to-enforcer loop

- **Source:** pstack (section 3 #3, 4)
- **Where:** new skill in `ceh-coding-agent`
- **Effort:** M
- **Idea:** Corrections today land as prose (memory files, CLAUDE.md lines), the weakest level,
  because nothing fails when an agent skips them. On `/correct` or "you keep doing X": mine reverts,
  PR review comments, `DECISION_LOG.md`, feedback memories, and the never/always lines in
  CLAUDE.md, and group them into classes that happened at least twice. Fix each class at the highest
  level that works: architecture, then types, then a lint or `validate.py` check whose error names
  the fix, then a test, docs last. Prove each new check goes red on the real past mistake. Keep a
  rule → enforcer table in CLAUDE.md.
- **Note:** A candidate class here is a bumped plugin missing its `docs/PLUGIN_VERSIONS.md` row, if
  `validate.py` does not check it yet.

### Confidence ladder for safety claims

- **Source:** pstack `/blast-radius` (section 3 #4, 4)
- **Where:** `ceh-git-workflow:code-review`, `ceh-testing:verify-behavior-preserved`
- **Effort:** S
- **Idea:** Name the one fact the change's safety depends on, push it as far down the ladder as is
  cheap, and say where it stopped: 1 said so, 2 `file:line`, 3 walked the failure step by step, 4 ran
  a script that fails loud, 5 reproduced in the running app. Splits our `inferred` status, which
  today covers both "saw the line" and "traced the failure".
- **Open question:** Whether the output style maps its status words onto rungs. Check
  `docs/CROSS_REFERENCES.md` first if that text is duplicated.

### Don't ask what you can run

- **Source:** pstack (section 3 #2, 4)
- **Where:** `ceh-coding-agent:agent-coding-contract`
- **Effort:** S
- **Idea:** Before `AskUserQuestion` on a "which approach" fork, classify it. If running something
  answers it (behavior, timing, output, layout), sketch a throwaway prototype in the scratchpad,
  observe, decide, report. Only product or preference calls reach the user.
- **Constraint:** Stays within the contract's always-allowed "throwaway snippet" category, so it does
  not conflict with the no-tests-unless-asked rule. Mirror per `docs/CROSS_REFERENCES.md` if the
  contract text is duplicated.

### Workflow steps copied verbatim into tasks

- **Source:** pstack (section 3 #1, 4)
- **Where:** `ceh-workflow-runner:run-agentic-workflow`, `ceh-plan-build-review`
- **Effort:** S
- **Idea:** At start, create one task per stage, named exactly as in the SKILL or `flow.yaml`, before
  any task-specific todos. A stage not run is closed as `skip: <reason>`, and the final summary lists
  every skip. A silently merged or dropped stage becomes visible.
- **Open question:** Check whether `run-agentic-workflow` already creates per-stage tasks.

### Multi-model review panel

- **Source:** pstack `/interrogate` (section 3 #6, 4)
- **Where:** `ceh-git-workflow:code-review` (opt-in mode)
- **Effort:** M
- **Idea:** Send the same prompt and rubric, no personas, to subagents pinned to `opus`, `sonnet`, and
  `haiku`. Dedupe, rank findings by how many models agree, bucket each as act on, consider, noted,
  or dismissed.
- **Caveat:** All-Claude panels share blind spots, so agreement means less than pstack's
  cross-family panel. Costs about 3x, so opt-in only. Overlaps with Second-opinion skill, which adds
  a non-Claude model.

### Generated project verify skill

- **Source:** pstack `/create-verification-skill` (section 3 #7, 4)
- **Where:** `ceh-testing` (new skill)
- **Effort:** M
- **Idea:** Read the repo (scripts, Makefile, compose, `.env.example`) and write
  `.claude/skills/verify-<app>/SKILL.md` with Launch (command plus readiness probe), Doctor (common
  failures), Drive (curl or browser steps), Evidence, Cleanup, and a feature map. The generator must
  run the new skill end to end and fix it until it passes. Saves tester agents rediscovering how to
  start the app each run.
- **Notes:** The generator is stack-agnostic, only its output is stack-specific, so it passes the
  technique/tooling test. Claude Code's built-in `run` skill already looks for such a project skill.
  Needs a maintain step for drift.

### Transcript evidence for model-audit

- **Source:** pstack `/reflect` (section 3 #8, 4)
- **Where:** `.claude/skills/model-audit/` (repo-local)
- **Effort:** M
- **Idea:** Read `~/.claude/projects/<this-repo-slug>/*.jsonl` only, never other projects. Look for
  skills that should have fired and did not, skill output that was ignored, and corrections right
  after a skill ran. Three reviewer lenses plus a synthesizer produce Accepted / Rejected / Backlog.
  Items a script could enforce move to Backlog as `validate.py` candidates. Apply only after user
  approval.
- **Constraint:** A local mode only. `model-audit.yml` runs in CI, which has no transcripts.

### Cite a skill only with what it changed

- **Source:** pstack (section 3 #5, 4)
- **Where:** `ceh-coding-agent` output style
- **Effort:** S
- **Idea:** One line: when citing a skill or standard, name the choice it changed, and cite only
  skills loaded this session. "Per write-less-code" becomes "per write-less-code, used `pathlib`
  instead of a helper".

### Fresh subagent per round

- **Source:** pstack (section 3 #11, 4)
- **Where:** tester agents, `ceh-core:delegate-bulk-reads`
- **Effort:** S
- **Idea:** A retry or follow-up goes to a new subagent whose brief merges the original brief, every
  later directive, and the prior report, not a `SendMessage` resume. pstack's reason: resumed agents
  drop mid-run directives. Exception: the round needs live state the old agent holds (a running
  server, uncommitted changes).
- **Priority:** Low. Bulk-reader questions already go to fresh agents, so the value is mostly in the
  tester agents.

## Dropped

- **Artifact handoff between skills (gstack 4.3).** Already shipped. `ceh-plan-build-review` chains
  `SKELETON.md` and `ITER_NN.md` through `plan-schema.md` and `depends_on`. `ceh-business-plan`
  shares one `BUSINESS_PLAN.md` schema that every skill reads and writes by section.
- **Rules-only AGENTS.md digest (gstack 4.7).** Only useful for users on agents that read rules but
  not skills. Dropped until there is demand.
- **`triggers:` frontmatter field (gstack 4.8).** No harness reads it. Claude Code supports
  `when_to_use` and `paths`, and the Agent Skills spec has neither `triggers` nor keywords.
