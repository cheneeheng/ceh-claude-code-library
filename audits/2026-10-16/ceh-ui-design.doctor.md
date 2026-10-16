| # | Topic | Outcome | Status |
|---|-------|---------|--------|
| 1 | Motion rules contradict each other | `design-ui` says to animate only `transform` and `opacity`, then tells you to transition color, lift with a shadow, and use `--dur-fast` for color changes. | inferred, high confidence |
| 2 | Token-compliance check vs the examples | The review pass bans hardcoded px sizes, but `examples.md` hardcodes several. | inferred, high confidence |
| 3 | "No markup changes" when swapping themes | Two tokens exist only in Meridian, so the claim is not fully true. | verified, medium confidence |
| 4 | Recipes carry one app's vocabulary | The dock, table, and anti-pattern lines use "round", "End turn", and "queued orders". | inferred, low confidence, flag only |
| 5 | "Ask the user" vs the autonomous coding contract | The theme-choice and variants-board steps ask the user, while the contract says to decide, log, and continue. | your call |
| 6 | Everything else in the plugin | Class names, tokens, and the cross-skill reference all resolve, and the Group 1 and Group 3 patterns are absent. | verified |

**Assumptions**

- **Scope:** `plugins/standalone/ceh-ui-design`, which is `SKILL.md`, `references/examples.md`, `README.md`, and `plugin.json`. I read the two themes' `brand.css` and `brand-guide.html` only through greps. I did not read `.claude/settings*.json`, `.mcp.json`, or anything outside the plugin.
- **Target model:** Sonnet 5.5, the model running this audit, since these files are read by the coding agent.
- **Not run:** `git blame` (so I could not order conflicting passages by age), `validate.py`, and any before/after behavioral probe.

**Motion rules contradict each other**

- **Location and pattern:** `SKILL.md:321-323` and `:327-329` (Group 2, internal conflict). `:321` assigns `--dur-fast` to "hover, press, and color changes", and `:327` says "Animate `transform` and `opacity` only". The Micro-interactions section does the same at `:312-313`: "lift with a deeper shadow" and "state changes transition color".
- **Why it matters:** the model gets two rules for one situation and cannot satisfy both. The reflow reason given for the rule does not cover color or shadow, so the fix is to scope the rule to what moves or resizes.
- **Action:** `rewrite` (hunk 1 below).

**Token-compliance check vs the examples**

- **Location and pattern:** `SKILL.md:374` says "no hardcoded hex, px sizes, or shadows", and `:103` says "No off-scale values". `examples.md` has `2px var(--space-2)` (line 32), `10px` nodes (149, 156), `0 0 0 4px` (156), `28px` (176), `38px` (197), and `1200px` (17). This is Group 2: two passages in the same plugin that disagree.
- **Action:** `rewrite` the rule to allow fixed component dimensions no token covers (hunk 2). Change the one off-scale padding to `var(--space-1)` (hunk 3), which is 4px on the 4px grid.

**"No markup changes" when swapping themes**

- **Location and pattern:** `SKILL.md:394-395` and `:443-444` (Group 2, volatile specifics). `--shadow-lg` and `--weight-heavy` are defined only in `meridian/brand.css`. Tidewater defines neither, and `SKILL.md:420` already says so.
- **Action:** `rewrite` (hunk 4). I checked where the tokens are defined, not where Meridian's component classes use them.

**Recipes carry one app's vocabulary (flag only)**

- **Evidence:** `SKILL.md:232-242` ("CURRENT ROUND", "runs the 2 queued orders"), `:249`, and `:361` ("two 'End turn' buttons"). The repo's root `CLAUDE.md` says app-specific patterns are not standards.
- **Why only a flag:** I could not tell whether the vocabulary is deliberate illustration or a leftover from the app the recipes came from. That is the "one session's stumble encoded as a rule" pattern. No hunk is proposed.

**"Ask the user" vs the autonomous coding contract**

- **Evidence:** `SKILL.md:392` tells the model to ask via `AskUserQuestion` unless the user named a theme. `:59` says to show the board and ask which variant to keep. The contract loaded this session says to decide, document, and continue, and to stop only on its listed stop conditions.
- **Why no hunk:** the contract lives in another plugin, so an edit there is out of scope, and without blame I cannot say which passage is newer. `SKILL.md:393` already falls back to Meridian when no human answers, so the practical conflict is small. The choice below is yours.

**Everything else in the plugin**

- **Group 3 (tool descriptions):** zero findings. The skill `description` is 4 trigger phrases, so it is not enumerated.
- **Group 4 (request config):** not applicable, because the plugin has no request code.
- **Checked:** I grepped both `brand.css` files. Every class and token the skill names is defined in both themes, except `--shadow-lg` and `--weight-heavy`, which only Meridian has (as `SKILL.md:420` states). `ceh-web-frontend:make-ui-accessible` exists.
- **Left alone:** the four-step procedure (order matters), the numeric design limits (type sizes, nav items, placeholder length, which are design constraints and not output caps), the anti-pattern list (it repeats the rules, but the repeats are consistent), and the Motion section's restatement of common knowledge (low confidence, no hunk).
- **Out of scope but noticed:** `README.md:7-8` and `:28` narrate the move from `ceh-web-frontend`. I did not propose a hunk because the README is documentation for people, not prompt text.

**Proposed diff**

Proposed only, nothing applied.

```diff
--- a/plugins/standalone/ceh-ui-design/skills/design-ui/SKILL.md
+++ b/plugins/standalone/ceh-ui-design/skills/design-ui/SKILL.md
@@ hunk 1: Motion
-- **Animate `transform` and `opacity` only.** Animating `width`, `height`, `top`, or `margin`
-  reflows the page on every frame and jank shows first on slow hardware. Expand a panel with a
-  `transform` or a `grid-template-rows` transition, not `height: auto` hacks.
+- **Move and resize with `transform` and `opacity`.** Animating `width`, `height`, `top`, or
+  `margin` reflows the page on every frame and jank shows first on slow hardware. Expand a panel
+  with a `transform` or a `grid-template-rows` transition, not `height: auto` hacks. Color,
+  background, and shadow transitions at `--dur-fast` do not reflow and are fine.
@@ hunk 2: Review pass
-6. **Token compliance:** no hardcoded hex, px sizes, or shadows — `var(--token)` everywhere.
+6. **Token compliance:** no hardcoded hex, shadows, or font sizes, and spacing only from
+   `--space-*`. A px value is allowed for a fixed component dimension no token covers (a stepper
+   node, a monogram tile, a content-column cap).
@@ hunk 4: Choose and install (and the matching sentence under the Theme layer, ~line 443)
-  the same token names and component classes, so the choice is purely look-and-feel — swap later
-  by replacing one CSS file, with no markup changes. To preview, open
+  the same token names and component classes except Meridian's `--shadow-lg` and `--weight-heavy`,
+  so the choice is look-and-feel — swap later by replacing one CSS file, and keep markup off those
+  two tokens so it survives the swap. To preview, open
--- a/plugins/standalone/ceh-ui-design/skills/design-ui/references/examples.md
+++ b/plugins/standalone/ceh-ui-design/skills/design-ui/references/examples.md
@@ hunk 3: Command dock, line 32
-        style="font-size: var(--fs-50); border: 1px solid var(--border); border-radius: var(--radius-full); padding: 2px var(--space-2); text-decoration: none;"
+        style="font-size: var(--fs-50); border: 1px solid var(--border); border-radius: var(--radius-full); padding: var(--space-1) var(--space-2); text-decoration: none;"
```

If you apply these, bump `plugin.json` and the matching `marketplace.json` entry (PATCH, 1.0.5 to 1.0.6). Also add the `CHANGELOG.md` entry, the `docs/PLUGIN_VERSIONS.md` row, and run `python tools/validate-plugins/validate.py`. I have not done any of that.

---

I ran the greps on the two `brand.css` files and read all four plugin files in full. I did not run the validator.

**Decision: How should the theme-choice and variants-board steps behave when the contract says to decide without asking?**

1. Keep the skill as written and treat the contract as the override in autonomous sessions (recommended)
2. Rewrite `SKILL.md:392` and `:59` to decide, log the choice, and continue
3. Leave it and flag it for the contract's owner
