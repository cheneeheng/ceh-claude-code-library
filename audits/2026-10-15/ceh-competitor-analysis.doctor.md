The shell blocked `git blame`, so the audit has no provenance data. I read all five plugin files and checked the template, its block markers, and the Tidewater theme directly.

| # | Topic | Outcome | Status |
| --- | --- | --- | --- |
| 1 | Scope and target | All 5 files in the plugin, audited against Sonnet 5.5 (the model running this audit). Request code and prompt assembly don't exist here. | assumed |
| 2 | Agent output ceiling | `competitor-analyst.md:48` caps the reply at "about 150 lines". The cap is a numeric output ceiling, and the diff replaces it with the goal. | inferred, medium confidence |
| 3 | README trigger phrases | `README.md:21-22` and `:40-41` list auto-trigger phrases that the skill descriptions don't contain. | verified, medium confidence |
| 4 | Glance-first sizing rule | `analyze-competitor/SKILL.md:97-99` sets sentence counts. It also pins the HTML card layout, so I'm leaving it alone. | flag only, low confidence |
| 5 | Everything else | Group 3 (tool descriptions) and Group 4 (request config) don't apply. Group 1 has no other matches. The file paths and commands the skills name all resolve. | verified |

**Agent output ceiling**

- Location: `agents/competitor-analyst.md:48`. Evidence: "Stay under about 150 lines plus one coverage row per component."
- Pattern: Group 1f, numeric output ceiling. The stated reason (keep the caller's context small) doesn't make it a keeper. The cap tracks a size, not the point, and it can starve the mechanism table on a large competitor.
- Action: `rewrite`. The surrounding rules stay: "Never paste file contents back", and the coverage-row requirement from `analyze-competitor` step 6.

```diff
--- a/plugins/standalone/ceh-competitor-analysis/agents/competitor-analyst.md
+++ b/plugins/standalone/ceh-competitor-analysis/agents/competitor-analyst.md
-Lead with the identity table. Stay under about 150 lines plus one coverage row per component. Never
-paste file contents back. Point at them instead. This agent exists to keep a large competitor out of
-the caller's context, so a long reply defeats it.
+Lead with the identity table, then one coverage row per component. Never paste file contents back.
+Point at them instead. This agent exists to keep a large competitor out of the caller's context, so
+keep every other section to what the parent needs to rate and verify.
```

**README trigger phrases**

- Location: `README.md:21-22` and `README.md:40-41`. Evidence: the README lists "how does X compare to us", "study this competitor", "a pasted GitHub URL with 'investigate'", "comparison report" and "master report". The descriptions carry only "competitor analysis", "analyze this repo", "what can we learn from X", "compare them with us" and "how do we stack up".
- Pattern: Group 2, a stale claim the repository contradicts. Trigger phrases belong in the description, which the router reads, so the README overpromises.
- Action: `rewrite` the README to match the descriptions. This is a proposed edit only. The other direction (adding the phrases to the descriptions) would risk the 300-character limit.

```diff
--- a/plugins/standalone/ceh-competitor-analysis/README.md
+++ b/plugins/standalone/ceh-competitor-analysis/README.md
-**Auto-triggers on:** "competitor analysis", "analyze this repo", "what can we learn from X", "how
-does X compare to us", "study this competitor", or a pasted GitHub URL with "investigate".
+**Auto-triggers on:** "competitor analysis", "analyze this repo", "what can we learn from X".
@@
-**Auto-triggers on:** "compare them with us", "comparison report", "master report", "how do we
-stack up", "side by side with our work".
+**Auto-triggers on:** "compare them with us", "how do we stack up", or after several competitors
+were analysed.
```

**Glance-first sizing rule**

- The rule sets "a few words" per name, one line per one-liner, and one to three sentences per why or how. It reads like a numeric ceiling, but it feeds fixed HTML card slots in `references/report-page.html`. That makes it a format requirement, which the keep list protects.
- I'm flagging it only. If you want it loosened, re-express it as "names and one-liners must fit a card header".

---

If you accept the two hunks, repo rules need these in the same commit:

- the `CHANGELOG.md` entry
- version bumps in `plugin.json` and `marketplace.json` (PATCH, 1.1.7 to 1.1.8)
- the `docs/PLUGIN_VERSIONS.md` row
- a green `python tools/validate-plugins/validate.py`

I haven't applied any edits or run the validator.
