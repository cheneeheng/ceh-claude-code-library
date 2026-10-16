| # | Topic | Outcome | Status |
|---|-------|---------|--------|
| 1 | Scope and target | Audited all 10 files in `plugins/standalone/ceh-testing`. Target model is Sonnet 5.5, the model running this audit. | assumed |
| 2 | Group 1 (dated prompt text) | One medium finding: a numeric cap on report length. No pressure language, no scaffolds replaced by API features, no model-version fossils. | done |
| 3 | Group 2 (skill files) | Every in-project cross-reference I checked resolves. Versions match. One low-confidence flag on a command flag. | partly verified |
| 4 | Groups 3 and 4 | Not applicable. There are no tool definitions and no request-building code. | done |
| 5 | Proposed diff | One hunk. The cap is the only medium or high finding. | done, not applied |

**Scope and target**

- I read the README, `plugin.json`, all 9 `SKILL.md` files, and `references/fix-record-format.md`. I made no edits, because the request did not ask for any.
- I skipped `~/.claude/` and other user-level files.

**Group 1 (dated prompt text)**

I grepped for `MUST|NEVER|ALWAYS|CRITICAL|IMPORTANT|think step|try to|if possible`. The only hits were:
- the literal `CRITICAL` severity label in `audit-test-suite` output;
- a `# MUST fail` code comment in `test-a-bug-fix`;
- the trigger phrase "try to break it" in `explore-app-for-bugs`.

None is pressure language.

| # | Location | Evidence | Pattern | Why obsolete | Confidence | Action |
|---|----------|----------|---------|--------------|------------|--------|
| F1 | `audit-test-suite/SKILL.md:225` | "Cap the list at about 15 findings and cut the tail rather than listing everything" | 1f, numeric output ceiling | The skill gives an operational reason, but 1f says a stated reason does not make a numeric clamp a keeper. Re-express it as outcome framing. | Medium | rewrite |

Proposed diff for F1:

```diff
-- Cap the list at about 15 findings and cut the tail rather than listing everything, because a
-  long tail buries the few fixes that matter.
+- Keep the list to the findings that change a decision, ranked worst-first, because a long tail
+  buries the few fixes that matter.
```

- You may reasonably decline F1: the number gives a subagent a concrete stopping point. I kept the reason and dropped only the number.
- `explore-app-for-bugs` uses "about 20 actions" per charter, and `measure-performance` uses "about 5%" for a flat profile. I left both. They are working budgets and decision thresholds, not output ceilings, and the report records how many actions each charter used.

**Group 2 (skill files)**

- The skill and agent names the plugin cites all exist: `ceh-coding-conduct:find-root-cause`, `ceh-coding-conduct:refactor-repo`, `ceh-coding-conduct:shrink-diff`, `ceh-security-audit:audit-codebase-security`, `ceh-usability-audit:simulate-newcomer-first-run`. `plugin.json` and `marketplace.json` both say 1.4.4. I checked these by listing the directories, and I read no other plugin's skill bodies.
- The "What waits for a request" block appears in 5 skills and overlaps `agent-coding-contract`'s Validation policy. I did not flag it: it is registered in `docs/CROSS_REFERENCES.md:242` and keeps each plugin self-contained (keep-list item 8).
- **F2, low, flag only:** `audit-test-suite/SKILL.md:105` uses `mutmut run --paths-to-mutate`. From memory, mutmut 3.x moved that setting into project config, so the flag may no longer exist. I did not verify this. Check it against the mutmut version you target before changing anything.
- **F3, low, flag only:** `verify-behavior-preserved/SKILL.md:111` creates the pre-change worktree at `/tmp/before`. This is a style note, not a defect.

---

I read all the files, ran the signal grep, checked skill names by listing directories, and compared the two version strings. I did not run any of the commands the skills describe. I did not run Step 7's behavioral probes either, so F1 is untested.
