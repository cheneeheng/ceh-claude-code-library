| Topic            | Outcome                                                                                                                 | Status      |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------- | ----------- |
| Scope and target | I audited the 3 `SKILL.md` files, the README and `plugin.json` in `ceh-blog` against Sonnet 5.5. No edits were applied. | assumed     |
| Findings         | There are 4 proposed changes: 1 high, 3 medium, plus 3 low-confidence flags. Group 3 and Group 4 do not apply.          | inferred    |
| Proposed diff    | Four hunks below, one per finding.                                                                                      | not applied |

**Scope and target**

- Scope is all five files under `plugins/standalone/ceh-blog`. I read nothing outside it except `plugins/CLAUDE.md` and `docs/CROSS_REFERENCES.md`.
- Target is Sonnet 5.5, the model running this audit, because the skills pin no model.
- `git log` shows one commit for this plugin (a directory move), so `git blame` cannot date any line to an older model. Provenance here rests on idiom and on the repo itself.

**Inventory**

- `skills/draft-post/SKILL.md` (304 lines)
- `skills/edit-post/SKILL.md` (186 lines)
- `skills/repurpose-post/SKILL.md` (131 lines)
- `README.md`
- `.claude-plugin/plugin.json`

## Audit report

By confidence, highest first. The groups for this audit are Group 1 prompt text, Group 2 skill files, Group 3 tool descriptions and Group 4 request config. Group 1 has 2 findings and Group 2 has 2 (F2 and F3 are padding, which this audit places in Group 2).

**F1 (High, `rewrite`): Launch template contradicts the opening rule**

- **Location:** `draft-post/SKILL.md:192`, against `:137` and `:245-246`. Mirror: `edit-post/SKILL.md:114`, against `:55`.
- **Evidence:** the template says `Hook: What it does and who it's for (one sentence)`. The Opening rule says "not background, not a product pitch" and Voice says "never a product pitch".
- **Pattern:** Group 2, instructions that contradict each other.
- **Why obsolete:** a Launch post is told both to open with a product line and never to open with one. Nothing says which wins, so the result varies by which passage the model weighs.
- **Action:** rewrite in both files, canonical `draft-post` first, per `docs/CROSS_REFERENCES.md:123-132`. That entry's "Diverges" note stays accurate.

**F2 (Medium, `remove`): restated rules in edit-post**

- **Location:** `edit-post/SKILL.md:151`, `:157` and `:158`.
- **Evidence:**
  - `:158` "Draft is already good: say so clearly and make only minor polish edits."
  - `:151` "Diagnose before editing"
  - `:157` "One question after"
- **Pattern:** Group 2, scattered repetition.
- **Why obsolete:** each rule is already stated in Step 2 (`:40-43`), Step 4 (`:143`) and Output (`:166`). `:158` repeats `:155` almost word for word. The model spends effort reconciling three wordings, and nothing disagrees.
- **Action:** remove the three bullets. This file's rules are not a registered copy, so removal creates no drift.

**F3 (Medium, `remove`): generic virtue in draft-post**

- **Location:** `draft-post/SKILL.md:278`.
- **Evidence:** "No fluff drafts: specific, well-structured, worth publishing — not a padded word count mirroring the input length."
- **Pattern:** Group 2, generic virtues.
- **Why obsolete:** current models do not pad by default, and the concrete rules already sit in Step 4 ("don't pad", the "Concrete over abstract" bullet at `:276` and "Length").
- **Action:** remove.

**F4 (Medium, `rewrite`): hard word ranges**

- **Location:** `draft-post/SKILL.md:141-143`.
- **Evidence:** "400–800 words. Tight is better.", "600–1,000 words", "800–1,800 words".
- **Pattern:** Group 1, numeric output ceilings.
- **Why obsolete:** ceilings tuned against an older model's verbosity clamp the draft. The How-To line already carries its own escape hatch ("no ceiling if genuinely required"), which shows the numbers are soft.
- **Action:** restate by outcome and keep the relative ordering.

**Low-confidence flags (no edit)**

- **Scripted dialogue.** Verbatim quoted scripts sit at `draft-post:61-66`, `:69-71` and `:282-283`, at `edit-post:43` and `:48`, and at `repurpose-post:28-33`. This is Group 1 example over-indexing. I left them because they pin conversational shape and this is not a documented harm.
- **Opening drift.** `edit-post:55` says "create tension, a surprising claim, or a concrete moment". `draft-post:137` says "inside a moment or a thought". The two differ, and "surprising claim" can push an edit toward influencer style. The two edit rules may differ on purpose, and history cannot say, so this is the author's decision.
- **Numeric format limits in repurpose-post.** The tweet limit of 280 characters is a platform constraint and stays. The LinkedIn 150–300 words, TL;DR 2–3 sentences and blurb 3–5 sentences are channel format requirements. I kept them as format-sensitive.

**Kept on purpose**

- **Banned tells, in all three Voice blocks.** They are an author-stated preference, registered in `CROSS_REFERENCES.md:109-118`.
- **Duplicated post-type templates.** Registered at `:123-132`, and the copies agree apart from the noted divergence.
- **"Never invent scenes, feelings, or chronology."** A real constraint that still matters for this model.
- **Trigger phrases in descriptions.** Routing text may carry them.
- **Skill cross-references.** Every `ceh-blog:*` reference resolves.

## Proposed diff

Hunks are in finding order.

```diff
--- a/plugins/standalone/ceh-blog/skills/draft-post/SKILL.md   # F1
@@ -192
-Hook: What it does and who it's for (one sentence)
+Hook: The moment that led to building it (a scene or a thought), with what it does and who it's for inside the first paragraph
```

```diff
--- a/plugins/standalone/ceh-blog/skills/edit-post/SKILL.md   # F1 mirror
@@ -114
-Hook: What it does and who it's for (one sentence)
+Hook: The moment that led to building it (a scene or a thought), with what it does and who it's for inside the first paragraph
```

```diff
--- a/plugins/standalone/ceh-blog/skills/edit-post/SKILL.md   # F2
@@ -151
-- **Diagnose before editing**: a brief diagnosis always precedes the revised draft. The author needs the reasoning, not just a new version.
@@ -157,158
-- **One question after**: after sharing the edit, ask one focused question. It is a dialogue, not a checklist.
-- **Draft is already good**: say so clearly and make only minor polish edits.
```

```diff
--- a/plugins/standalone/ceh-blog/skills/draft-post/SKILL.md   # F3
@@ -278
-- **No fluff drafts**: specific, well-structured, worth publishing — not a padded word count mirroring the input length.
```

```diff
--- a/plugins/standalone/ceh-blog/skills/draft-post/SKILL.md   # F4
@@ -141,143
-- **Length**: what the content needs — don't pad, don't cut substance.
-  - Opinion / Personal Story / Thought Leadership: 400–800 words. Tight is better.
-  - Lessons Learned / Launch: 600–1,000 words.
-  - How-To / Tutorial: 800–1,800 words, driven by steps and code samples — no ceiling if genuinely required.
+- **Length**: what the content needs — don't pad, don't cut substance. Opinion, Personal Story and Thought Leadership run short and tight. Lessons Learned and Launch run a little longer. How-To and Tutorial are driven by steps and code samples and run as long as those require.
```

**Findings**

- F4 changes how long drafts come out, so I would test it on one or two real drafts before keeping it. The other hunks remove or reword text without changing behavior.
- F2 and F3 are removal hypotheses. If a draft or edit regresses, re-add the minimal one-line form, not the old wording.
- For F1, drop the `Diverges` note at `CROSS_REFERENCES.md:129` only if the two Launch templates stop matching after the edit.
- I did not run `validate.py`, and I applied nothing.

Architecture: if the F1 hunk lands, bump `ceh-blog` to a PATCH version in both `plugin.json` and `marketplace.json`, and add the CHANGELOG and `PLUGIN_VERSIONS.md` rows.
