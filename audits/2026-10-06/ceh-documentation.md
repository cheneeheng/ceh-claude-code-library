# Model audit: ceh-documentation

- Date: 2026-10-06
- claude-code 2.1.291
- Edits applied: yes

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-documentation.doctor.md](ceh-documentation.doctor.md).

## Kept changes

### plugins/standalone/ceh-documentation/skills/write-project-docs/SKILL.md:36

- **Rule:** 3, a model-independent defect. This is also the report's one High finding.
- **Backing:** No guide quote applies. The plugin has exactly one `references/docs-standard.md`, and the README says it "lives once at the plugin root". The skills read it through `${CLAUDE_PLUGIN_ROOT}`. "Ships the same file" implies a copy inside each delegated skill, which does not exist.
- **Change:**
  - Before: `Each delegated skill ships the same file.`
  - After: `Each delegated skill reads the same file.`

### plugins/standalone/ceh-documentation/skills/write-guides-and-runbooks/SKILL.md:130

- **Rule:** 3, two instructions that contradict each other. The report left this as a low-confidence flag. I kept it because the contradiction is concrete.
- **Backing:** No guide quote applies. `docs-standard.md:72-74` says "`NN` is two digits from `01`, contiguous… inserting or removing renumbers the rest of that folder… Never leave a gap." The skeleton hardcodes `OP-02-install` and `OP-04` to `OP-07`. Under `write-project-docs` the skill drops `OP-01` and `OP-03`, so following the skeleton literally leaves gaps.
- **Change:**
  - Before: `…and the runbook links to both instead of repeating them.`
  - After: `…and the runbook links to both instead of repeating them. Renumber the remaining pages from OP-01 (standard §3), so install becomes OP-01-install.`

## Left out

- **Page-mode count in `README.md:43`.** The README is not loaded by any skill, so it affects no model behavior and fits none of the three rules.
- **Basic CommonMark rules in `docs-standard.md:145-148`.** No page backs removing them. The report found no failure they prevent.
- **Self-review checklists, `Never invent` rules, and page budgets.** The Opus 5 guide says explicit verification instructions cause over-verification. The Fable 5 and Sonnet 5.5 guides say explicit verification helps. Those guides conflict, so rule 2 excludes the change.
- **Parallel-call nudge and other model-specific additions.** The Fable 5.1 batching nudge is written as a per-turn harness message, not static skill text. I judged the need too weak for rule 1 or 2 in these skills.
