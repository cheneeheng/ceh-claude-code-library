| Topic                      | Outcome                                                                                                                                                                                                                                                                               | Status   |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| Scope and target           | Scope is `plugins/standalone/ceh-documentation` (5 `SKILL.md`, `references/docs-standard.md`, `README.md`, `plugin.json`). The target model is Sonnet 5.5, the model running this audit, because no skill pins its own model. I read `plugins/CLAUDE.md` only to check for conflicts. | assumed  |
| Stale fact                 | `write-project-docs/SKILL.md:36` says each delegated skill "ships the same file", but the plugin has exactly one copy of `docs-standard.md`.                                                                                                                                          | verified |
| Low-confidence flags       | Three items are flagged and left out of the diff.                                                                                                                                                                                                                                     | inferred |
| Considered and kept        | Every other match was context or a working constraint, so I left it alone.                                                                                                                                                                                                            | inferred |
| Groups 3 and 4, provenance | Both groups are not applicable, and `git blame` gave no usable provenance.                                                                                                                                                                                                            | verified |

**Stale fact**

- Location `write-project-docs/SKILL.md:36`, pattern Group 2 "Volatile specifics", confidence **High**, action `rewrite`. The evidence is "Each delegated skill ships the same file."
  - A glob of the plugin shows one copy at `references/docs-standard.md`.
  - The skills read it through `${CLAUDE_PLUGIN_ROOT}`, and the README says it "lives once at the plugin root".
  - A grep for the old phrase finds nothing else to update.
- The proposed diff is below. It is a proposal only, since you did not ask me to apply edits.

```diff
--- a/plugins/standalone/ceh-documentation/skills/write-project-docs/SKILL.md
+++ b/plugins/standalone/ceh-documentation/skills/write-project-docs/SKILL.md
@@ -35,2 +35,2 @@
 follows `${CLAUDE_PLUGIN_ROOT}/references/docs-standard.md` ("the standard" below). Read it before
-step 3. Each delegated skill ships the same file.
+step 3. Each delegated skill reads the same file.
```

- Landing this edit needs a PATCH bump in `plugin.json` and `marketplace.json`, a `CHANGELOG.md` entry, and a `docs/PLUGIN_VERSIONS.md` row. I did not check `docs/CROSS_REFERENCES.md` for this line.

**Low-confidence flags**

- `write-guides-and-runbooks/SKILL.md:117-130` hardcodes OP-01 to OP-07, then says to drop OP-01 and OP-03 under `write-project-docs`. Standard §3 requires contiguous numbers, and the standard wins on conflict. So install becomes OP-01 after the drop, but the skeleton does not say so. The user decides whether one clause is worth adding.
- `README.md:43` lists five page modes, while standard §2 says its seven names are the only valid values (it adds Hub and Front page). The README is not loaded by the model, so this is cosmetic.
- `docs-standard.md:145-148` restates basic CommonMark (blank line between paragraphs, no hard-wrap). The model likely knows this already. The file is loaded by four skills, so the cost is real, but I found no failure it prevents.

**Considered and kept**

- Page budgets (at most 7 steps, two screens, 20 to 40 lines) are the deliverable's format spec, each with a stated reason, so they are not the output-length clamps of Group 1f.
- The `Never invent` rule recurs across the standard and four skills, and the Self-review checklists repeat the Rules sections. The copies agree with each other, and the rule guards a failure that still occurs (fabricated commands and flags). That is working redundancy under keep-list item 8.
- The "no 'simply' or 'just'" and "no marketing adjectives" rules are house style for the docs the plugin writes. They are not patches for an older model's habits.
- Prohibitions in `write-examples` (no production runs, no manifest edits) protect state outside the example files, so they stay.

**Coverage**

- Group 1 has zero findings. Group 2 has 1 high-confidence finding and 3 low-confidence flags. Groups 3 and 4 are not applicable, because the plugin has no tool definitions and no request-building code.
- The plugin has one git commit, the 2026-10-01 directory split, so `git blame` cannot date any line. Provenance came from the text alone. No eval or behavioral probe was run, because the one proposed change is a factual correction.

Architecture: no flags.
