| Topic            | Outcome                                                                                                                                                                                               | Status           |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| Scope and target | Audited 7 prompt files in `plugins/standalone/ceh-coding-agent` (6 skills, the output style) plus the 2 hook scripts and the README. Target model is Claude Sonnet 5.5, the model running this audit. | assumed          |
| Findings         | Five stale-fact or dangling-reference fixes, all Group 2. Group 1 has no medium or high matches. Groups 3 and 4 are not applicable.                                                                   | inferred         |
| Conflict         | `shrink-diff` and `refactor-repo` tell the agent to run tests and commit, which the contract gates behind an explicit request. `git blame` cannot order them.                                         | flagged, no edit |
| Diff             | Five hunks proposed below. No file was edited.                                                                                                                                                        | proposed         |

**Scope and target**

- Inventory: 6 `SKILL.md` files, `output-styles/ceh-coding-agent.md`, `scripts/load-contract.sh`, `scripts/less-code-payload.sh`, `README.md`. I did not read `hooks/hooks.json` or `plugin.json` (settings and hook definitions are off limits per the guide). So the README's claim about which agents the hooks skip is unchecked.
- Provenance: nearly every line blames to one bulk migration commit, `32134a7c`, so blame cannot date or order anything here.
- Skipped on purpose: the duplicated ladder and behavior-preservation blocks in `shrink-diff` and `refactor-repo`. They are working redundancy and are registered in `docs/CROSS_REFERENCES.md:62-68`.

**Findings**

All five are stale facts the repo contradicts, so confidence is high.

1. `README.md:25` says `explain-codebase` is "Manual only ... never auto-fires". `explain-codebase/SKILL.md:13` sets `disable-model-invocation: false` and has trigger phrases. `README.md:35` also tells users to say "explain this codebase". Action: `rewrite`.
2. `explain-until-understood/SKILL.md:244` says "The contract's honesty rules apply unchanged". `agent-coding-contract` has no honesty section. The rules live in the `# Honesty` section of the output style. Action: `rewrite`.
3. `explain-codebase/SKILL.md:210` says "Running the mapper first is cheap". No mapper skill exists in this plugin, and a grep finds no other mention. Action: `remove`.
4. `README.md:19` describes the contract as having a "role". The contract has no role section. Action: `rewrite`.
5. `shrink-diff/SKILL.md:14` declares `argument-hint: "[base-branch]"`, but lines 38-39 hard-code `main...HEAD` and never use the argument. Action: `rewrite`.

**Conflict**

- `shrink-diff/SKILL.md:96-105` and `refactor-repo/SKILL.md:91-100` say to run tests before and after, write characterization tests, and commit them. `agent-coding-contract/SKILL.md:34-38` allows running suites, writing tests, and git writes only on explicit request. I did not propose a rewrite. The contract rule is a prohibition and the skill text loosens it. You decide whether invoking `/shrink-diff` counts as the request, or whether the skills should say "when tests are in scope".

**Diff**

```diff
--- a/plugins/standalone/ceh-coding-agent/README.md
+++ b/plugins/standalone/ceh-coding-agent/README.md
-| The full behavioral contract — role, core rules, five-step workflow, stop conditions, decision logging.
+| The full behavioral contract — core rules, five-step workflow, stop conditions, decision logging.
-| `explain-codebase` | Manual only (`/explain-codebase`) — never auto-fires |
+| `explain-codebase` | On demand — when the ask is to understand a whole repo and leave the understanding in a file |
```

```diff
--- a/plugins/standalone/ceh-coding-agent/skills/explain-until-understood/SKILL.md
+++ b/plugins/standalone/ceh-coding-agent/skills/explain-until-understood/SKILL.md
-The contract's honesty rules apply unchanged. One addition specific to explaining:
+The output style's honesty rules apply unchanged. One addition specific to explaining:
```

```diff
--- a/plugins/standalone/ceh-coding-agent/skills/explain-codebase/SKILL.md
+++ b/plugins/standalone/ceh-coding-agent/skills/explain-codebase/SKILL.md
 | Explain what is in the repo and how it works, component by component              | **this skill**                                                                                                           |
-
-Running the mapper first is cheap and gives a good inventory to explain against — but never required.
```

````diff
--- a/plugins/standalone/ceh-coding-agent/skills/shrink-diff/SKILL.md
+++ b/plugins/standalone/ceh-coding-agent/skills/shrink-diff/SKILL.md
-The seed set is everything the branch changed relative to main:
+The seed set is everything the branch changed relative to the base branch (the argument, default `main`):

 ```bash
-git diff --stat main...HEAD          # size baseline (three dots: merge-base, not main's tip)
-git diff --name-only main...HEAD     # seed files
+git diff --stat <base>...HEAD        # size baseline (three dots: merge-base, not the base tip)
+git diff --name-only <base>...HEAD   # seed files
````

The final `Output` line (`git diff --stat main...HEAD`) takes the same `<base>` substitution. The hunk is trimmed here for length.

**Flags (report only, no edit)**

- `scripts/load-contract.sh:15` says "non-negotiable and overrides apparent prompt relevance". This is pressure language, but it is routing text for a load that must happen every session, so I left it alone. Confidence: low.
- `agent-coding-contract/SKILL.md:49,72` names `TaskCreate`, `TaskUpdate` and `AskUserQuestion`. None of them appear in this session's tool list. They belong to the agent harness, so their absence does not contradict the repo. Confidence: low.
- `output-styles/ceh-coding-agent.md:26` caps bullets at "max 3". This is a numeric ceiling, but it is a deliberate format rule in a user-chosen style. Confidence: low.
- `README.md:10-14` holds migration notes ("moved to ...") that read as a diff against an earlier version. The README is human documentation and no skill loads it, so I did not propose an edit. Confidence: low.

Group counts: Group 1 has 0 findings above low. Group 2 has 5 fixes and 1 flagged conflict. Groups 3 and 4 are not applicable (no tool descriptions or request code).

Architecture: apart from the `shrink-diff` and `refactor-repo` conflict, the duplicated blocks are all registered, so they only drift if edits skip `docs/CROSS_REFERENCES.md`.
