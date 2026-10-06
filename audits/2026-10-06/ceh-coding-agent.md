# Model audit: ceh-coding-agent

- Date: 2026-10-06
- claude-code 2.1.291
- Edits applied: yes

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-coding-agent.doctor.md](ceh-coding-agent.doctor.md).

## Kept changes

### plugins/standalone/ceh-coding-agent/README.md:20

- **Rule:** 3. The README describes a contract section that does not exist.
- **Backing:** No page backs this one. The defect is in the repo. `agent-coding-contract/SKILL.md` has no role section. Its sections are Procedure, Rules, Output, and Stop conditions.
- **Before:** `The full behavioral contract — role, core rules, five-step workflow, stop conditions, decision logging.`
- **After:** `The full behavioral contract — core rules, five-step workflow, stop conditions, decision logging.`

### plugins/standalone/ceh-coding-agent/README.md:25

- **Rule:** 3. Two instructions contradict each other.
- **Backing:** No page backs this one. `explain-codebase/SKILL.md:13` sets `disable-model-invocation: false` and lists trigger phrases. `README.md:35` tells users to say "explain this codebase". Line 25 says "never auto-fires".
- **Before:** `Manual only (`/explain-codebase`) — never auto-fires`
- **After:** `On demand — when the ask is to understand a whole repo and leave the understanding in a file`

### plugins/standalone/ceh-coding-agent/skills/explain-until-understood/SKILL.md:244

- **Rule:** 3. The line points to a section that is not there.
- **Backing:** No page backs this one. The contract has no honesty section. The honesty rules are in the `# Honesty` section of `output-styles/ceh-coding-agent.md:56`.
- **Before:** `The contract's honesty rules apply unchanged.`
- **After:** `The output style's honesty rules apply unchanged.`

### plugins/standalone/ceh-coding-agent/skills/explain-codebase/SKILL.md:210

- **Rule:** 3. The line refers to a skill that does not exist.
- **Backing:** No page backs this one. "Running the mapper first is cheap…" names a mapper skill. No such skill exists in the plugin, and the report's grep found no other mention.
- **Before:** `Running the mapper first is cheap and gives a good inventory to explain against — but never required.` (a trailing line after the Hands-off table)
- **After:** The line and its preceding blank line are removed.

### plugins/standalone/ceh-coding-agent/skills/shrink-diff/SKILL.md:35

- **Rule:** 3. The frontmatter and the body contradict each other.
- **Backing:** No page backs this one. The frontmatter declares `argument-hint: "[base-branch]"`, but lines 35-39 hard-code `main...HEAD` and never use the argument.
- **Before:**
  ```
  The seed set is everything the branch changed relative to main:
  git diff --stat main...HEAD          # size baseline (three dots: merge-base, not main's tip)
  git diff --name-only main...HEAD     # seed files
  ```
- **After:**
  ```
  The seed set is everything the branch changed relative to the base branch (the argument, default
  `main`):
  git diff --stat <base>...HEAD        # size baseline (three dots: merge-base, not the base tip)
  git diff --name-only <base>...HEAD   # seed files
  ```

### plugins/standalone/ceh-coding-agent/skills/shrink-diff/SKILL.md:109

- **Rule:** 3. This applies the same fix to the `Output` line, so it matches the scope block.
- **Backing:** Same as above. The report's note says the final `Output` line takes the same `<base>` substitution.
- **Before:** `End with the before/after `git diff --stat main...HEAD` totals`
- **After:** `End with the before/after `git diff --stat <base>...HEAD` totals`

**Considered and left out**

- **`shrink-diff` and `refactor-repo` test and commit conflict:** the report flags it and proposes no edit, and I followed the report.
- **Verification and scope-limiting instructions:** none of the model guides call for changing the plugin's existing instructions, so nothing was added.
- **Pressure wording in `load-contract.sh`:** the report left it alone, and I did too.
- **Output style "max 3" bullets and README migration notes:** the report left both alone, and no guide contradicts either.
- **Other page patterns:** no file shows the need these sections describe. Examples are parallel-call batching, progress updates, and the send-to-user tool.
