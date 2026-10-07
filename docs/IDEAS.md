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

## Dropped

- **Artifact handoff between skills (gstack 4.3).** Already shipped. `ceh-plan-build-review` chains
  `SKELETON.md` and `ITER_NN.md` through `plan-schema.md` and `depends_on`. `ceh-business-plan`
  shares one `BUSINESS_PLAN.md` schema that every skill reads and writes by section.
- **Rules-only AGENTS.md digest (gstack 4.7).** Only useful for users on agents that read rules but
  not skills. Dropped until there is demand.
- **`triggers:` frontmatter field (gstack 4.8).** No harness reads it. Claude Code supports
  `when_to_use` and `paths`, and the Agent Skills spec has neither `triggers` nor keywords.
