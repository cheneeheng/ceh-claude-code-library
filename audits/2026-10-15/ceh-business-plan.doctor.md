| # | Topic | Outcome | Status |
|---|---|---|---|
| 1 | Scope and target | 11 files in `ceh-business-plan`, audited against Sonnet 5.5, the model running this audit. | assumed |
| 2 | `status` contradiction | `develop-business-plan` says no specialist touches `status`, but `find-product-market-fit` sets `status: validated`. | verified, diff proposed |
| 3 | Word cap on the cold email | `write-investor-materials` caps the email at 120 words in two places, a numeric output ceiling. | inferred, diff proposed |
| 4 | Remaining flags | Two low-confidence items, no edit proposed. | flag only |
| 5 | Edits | None applied. Your request did not ask for edits. | done |

**Scope and target**

- The scope is `plugins/standalone/ceh-business-plan`: 9 `SKILL.md` files, `references/business-plan-schema.md`, `README.md` and `plugin.json`. I skipped `~/.claude/` and the repo-level `CLAUDE.md`.
- The target is Sonnet 5.5 because the request names no model and no migration is documented. Re-run with a different target if these skills are meant for another model.
- Groups 3 and 4 are not applicable. The plugin has no tool definitions and no request-building code. Group 1 has one finding and Group 2 has one. Nothing turned up for pressure language, think-step-by-step scaffolds, prefill, or the thinking-disabled and anti-formatting patterns.
- `git blame` was not run. Provenance comes from reading the files only.

**`status` contradiction**

- **Location:** `skills/develop-business-plan/SKILL.md:57-58`. **Pattern:** Group 2, instruction files that contradict each other. **Confidence:** high.
- **Evidence:** the text says "several of them re-score `pmf_gate` and none of them touches `status`". `skills/find-product-market-fit/SKILL.md:166` says "Flip frontmatter `status: validated`". I grepped both lines.
- **Why it matters:** the router relies on this rule to decide when to reset `status` to `draft`. A model that believes no specialist sets `status` may skip re-reading it after `find-product-market-fit`.
- **Action:** rewrite. The proposed diff is below.

```diff
--- a/skills/develop-business-plan/SKILL.md
+++ b/skills/develop-business-plan/SKILL.md
@@ -57,2 +57,3 @@
 - The status rule in step 4 runs after every specialist, because several of them re-score
-  `pmf_gate` and none of them touches `status`.
+  `pmf_gate` and only `find-product-market-fit` sets `status`, to `validated` when the gate
+  passes.
```

**Word cap on the cold email**

- **Location:** `skills/write-investor-materials/SKILL.md:32` ("a cold email of at most 120 words") and `:91` ("**Email** (≤ 120 words)"). **Pattern:** Group 1f, numeric output ceilings. **Confidence:** medium.
- **Why obsolete:** per 1f, the guidance is to state the audience and goal and drop the count, because numeric caps were tuned against older models that rambled. This one is a real format preference, so you may reasonably keep it. Both locations have to change together if you take it.
- **Action:** rewrite.

```diff
--- a/skills/write-investor-materials/SKILL.md
+++ b/skills/write-investor-materials/SKILL.md
@@ -31,3 +31,3 @@
-5. Write the outreach notes: the investor profile that fits (stage, cheque size, sector, a thesis
-   this plan matches), a cold email of at most 120 words, and one follow-up line for two weeks
-   later.
+5. Write the outreach notes: the investor profile that fits (stage, cheque size, sector, a thesis
+   this plan matches), a cold email an investor can read in one glance on a phone, and one
+   follow-up line for two weeks later.
@@ -91 +91 @@
-**Email** (≤ 120 words)
+**Email** (short enough to read in one glance)
```

**Remaining flags**

- **Anecdotes:** `run-premortem` (Branson's leased aircraft), `plan-go-to-market` (Estée Lauder samples, Sam Walton) and `stress-test-unit-economics` (Musk, Kamprad, Dell) attach a story to many steps. This could be example over-indexing or history narrative. The README says they are deliberate traceable tests, and they carry the reason behind each check, so I left them. Confidence is low.
- **README wording:** `README.md:45-47` says the eight specialists "do not trigger on their own". Their frontmatter has `disable-model-invocation: false`, so the model can load them. The descriptions carry no trigger phrases, so the claim is roughly true but not exact. Confidence is low.
- **Left alone on purpose:** the "No human to answer" block repeats across six skills. It agrees everywhere and works, so the keep list protects it.

---

I checked the `ceh-build-planning` claims these skills rely on (`product/plans/` and `status: built`) against its `references/plan-format.md`, and they hold. I did not run `validate.py`, because no edits were made. If you apply either hunk, bump the plugin version in both manifests and add the CHANGELOG and `docs/PLUGIN_VERSIONS.md` entries.
