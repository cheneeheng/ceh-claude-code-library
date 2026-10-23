1. **Scope and target** · _assumed_
   Scope is the whole `ceh-build-planning` plugin (9 files), audited against Sonnet 5.5, the model running this audit.
2. **Stale README claim** · _verified_
   `README.md:16` says the review reply opens with `Plan review:` and names skipped lenses. The skill does not say that.
3. **Prompt text and other groups** · _inferred_
   Groups 1, 3 and 4 have no findings. The plugin's prompt text is clean.
4. **Proposed diff** · _not applied_
   One hunk, README only.

---

**Scope and target**

- Inventory: two `SKILL.md` files, `references/plan-schema.md`, `references/plan-review-schema.md`, two templates, `README.md`, `plugin.json`, and `tuning.json`. I read `tuning.json` and found no secrets. The plugin has no agents, hooks, commands, or request-building code.
- Target is Sonnet 5.5 because the request named none and `tuning.json` says `targets: general`. I took the model running this audit instead. Skipped files: none. The plugin has no `CLAUDE.md`, and I did not read the user-level or repo `CLAUDE.md` for this audit.
- I did not run `git blame`, so provenance (Step 2) rests on idioms alone. That is enough here because I found nothing that needs dating.

**Stale README claim**

- **Location:** `plugins/standalone/ceh-build-planning/README.md:16`.
- **Evidence:** "It's working if the reply opens with `Plan review:` and a verdict, and names any lens it skipped."
- **Pattern:** Group 2, file contradicting another file. **Confidence:** high. I grepped the plugin: `Plan review:` appears only as the heading inside the saved file (`plan-review.template.md:8`). `review-build-plan/SKILL.md:81` says "Reply with the verdict, the blocking findings, and the path." Skipped lenses go in the saved review, not the reply.
- **Direction:** I rewrote the README to match the skill, since the skill defines the behavior. Reading it the other way would add reply text the skill never asked for.

**Prompt text and other groups**

- Counts: Group 1 has 0 findings, Group 2 has 1, Groups 3 and 4 are not applicable. Group 3 has no tool definitions. Group 4 has no request code and no agent roster.
- I checked the cross-plugin claims against the repo. `plan-schema.md` and `plan.template.md` are byte-identical across the three plugins by md5. `write-evidence-report` resolves to `ceh-testing`, and `product/plans/` exists. `.agents_workspace/business/BUSINESS_PLAN.md` is absent here, but it is git-ignored and written by another plugin, so that is not a contradiction.
- Low-confidence flag, no edit: `write-build-plan/SKILL.md:68` has "More than six phases is a sign to re-run step 4". It is a numeric heuristic. I left it because it ties to step 4's reasoning and I have no evidence it misfires.
- Kept on purpose, per the keep list: the "Rules" bullets restating step 3 and step 5 (working redundancy), "Judge from the plan, not the brief" (a reasoned prohibition), and the Design checklist (context only the author knows). The `Load this skill when…` descriptions are trigger text, so the urgency there is allowed.

**Proposed diff**

```diff
--- a/plugins/standalone/ceh-build-planning/README.md
+++ b/plugins/standalone/ceh-build-planning/README.md
-... Report-only unless asked to fix. It's working if the reply opens with `Plan review:` and a verdict, and names any lens it skipped. |
+... Report-only unless asked to fix. It's working if it saves `.agents_workspace/plan-reviews/<slug>-<date>.md` and the reply gives the verdict, the blocking findings, and that path. |
```

- Applying this in this repo needs a PATCH bump in both `plugin.json` and `marketplace.json`, a `CHANGELOG.md` entry, a `docs/PLUGIN_VERSIONS.md` row, and a green `validate.py`. Prettier may also reflow the table row, so keep the edit to that one cell.

---

I read the files and ran two greps and an md5 comparison. I ran no behavioral probe and did not run `validate.py`.
