1. **Audit scope** · _done_
   I read all 3 skills, the 4 reference files, the README and `plugin.json` in `ceh-blog`. I assumed Sonnet 5.5 as the target model, because no file pins one.
2. **Restated working principles** · _inferred_
   Five bullets in `draft-post/SKILL.md:297-302` restate rules the same file already gives (medium confidence). I propose removing them.
3. **Word-count ranges** · _your call_
   `draft-post/SKILL.md:163-165` caps post length by type, which a current model reads literally (medium confidence). I propose qualitative wording instead.
4. **Scripted messages and duplication** · _inferred_
   Quoted fixed messages at `draft-post:306-307` and `edit-post:50` are flagged only (low). The Voice and structure copies are registered in `CROSS_REFERENCES.md` and agree, so I left them.
5. **Behavioral checks** · _not done_
   I did not probe any change, so nothing here is verified.

---

**Restated working principles**

- Cut "Infer first", "All questions at once", "Read everything first", "Concrete over abstract" and "Use the user's words". Keep "Pick the strongest thread".
- Two clauses are not stated elsewhere. "Put the question that unlocks the post first" moves into step 3's interview rule 1. "Notes with a workable angle get zero questions" is already covered by step 3's opening.

**Word-count ranges**

- If the ranges are a deliberate product spec, drop hunk 1 and keep hunk 2.
- I left the `repurpose-post` limits alone: 280 characters is a platform limit, and the LinkedIn and TL;DR lengths are format specs.

**Scripted messages and duplication**

- I left the banned-tells and AI-writing-tells lists in place. They define the voice and clean the author's text. They are not workarounds for model habits.

---

I checked that every `${CLAUDE_PLUGIN_ROOT}` path and every `/ceh-blog:*` command name resolves. Tool descriptions and request config don't apply to this plugin. I applied no edits.

The full report and the diff are in `.agents_workspace/prompt-audit/2026-10-23-ceh-blog.md`. The filename has no session ID because I don't have one.

**Decision: Apply the two proposed hunks to `draft-post/SKILL.md`?**

1. Apply both hunks (recommended)
2. Apply only the working-principles hunk
3. Apply nothing
