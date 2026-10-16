# Model audit: ceh-seo

- Date: 2026-10-16
- claude-code 2.1.301
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-seo.doctor.md](ceh-seo.doctor.md).

## Kept changes

### plugins/standalone/ceh-seo/skills/write-llms-txt/SKILL.md:19
- **Rule:** 4 (missing statement of when the task is done, added to the file's opening)
- **Backing:** "Be specific about the desired output format and constraints." (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, "Be clear and direct"). The other two skills in the plugin already open with a done condition. `make-page-crawlable` says "A public page is not done until…" and `write-project-listing-text` says "Done means…". This one gives none.
- **Change:**
  - Before: `…the parts that get it wrong are the ordering rules and the curation, not the markdown.` (then `## Procedure`)
  - After: the same sentence, then a new line: `Done means the file has an H1 and a summary blockquote, every link points at a page that resolves, and the links are ordered by what a newcomer needs first.`

### plugins/standalone/ceh-seo/skills/write-llms-txt/SKILL.md:88
- **Rule:** 4 (negative instruction rewritten as the positive it implies)
- **Backing:** "Tell Claude what to do instead of what not to do" (same general page, "Control the format of responses").
- **Change:**
  - Before: `- **Do not dump the sitemap into it.** A file listing 200 URLs has made zero decisions and is strictly worse than the sitemap it copied.`
  - After: `- **Select the links that earn a place.** A file listing 200 URLs has made zero decisions and is strictly worse than the sitemap it copied.`

### plugins/standalone/ceh-seo/skills/write-llms-txt/SKILL.md:90
- **Rule:** 4
- **Backing:** "Tell Claude what to do instead of what not to do" (same general page).
- **Change:**
  - Before: `- **Do not write marketing copy in the blockquote.** The agent is deciding what to read, not whether to buy.`
  - After: `- **Write the blockquote as a plain factual summary.** The agent is deciding what to read, not whether to buy.`

### plugins/standalone/ceh-seo/skills/write-llms-txt/SKILL.md:92
- **Rule:** 4
- **Backing:** "Tell Claude what to do instead of what not to do" (same general page).
- **Change:**
  - Before: `- **Do not duplicate page content inline.** `llms.txt` links; it does not host. That is what `llms-full.txt` is for.`
  - After: `- **Keep page content on its own page.** `llms.txt` links; it does not host. That is what `llms-full.txt` is for.`

### plugins/standalone/ceh-seo/skills/write-project-listing-text/SKILL.md:66
- **Rule:** 4
- **Backing:** "Tell Claude what to do instead of what not to do" (same general page).
- **Change:**
  - Before: `- No badge wall before the pitch — the excerpt window fills with shield URLs.`
  - After: `- Put the pitch before any badges — otherwise the excerpt window fills with shield URLs.`

### plugins/standalone/ceh-seo/skills/write-project-listing-text/SKILL.md:67
- **Rule:** 4
- **Backing:** "Tell Claude what to do instead of what not to do" (same general page).
- **Change:**
  - Before: `- No marketing adjectives without a verifiable fact attached.`
  - After: `- Attach a verifiable fact to every marketing adjective.`

### plugins/standalone/ceh-seo/skills/write-project-listing-text/SKILL.md:69
- **Rule:** 4
- **Backing:** "Tell Claude what to do instead of what not to do" (same general page).
- **Change:**
  - Before: `- No different pitches on different surfaces (see step 3).`
  - After: `- Use the one canonical one-liner from step 3 on every surface.`
