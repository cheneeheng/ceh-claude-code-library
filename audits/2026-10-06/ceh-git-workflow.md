# Model audit: ceh-git-workflow

- Date: 2026-10-06
- claude-code 2.1.291
- Edits applied: yes

## Unpinned audit against fable-5, fable-5-1, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-git-workflow.doctor.md](ceh-git-workflow.doctor.md).

## Kept changes

### plugins/standalone/ceh-git-workflow/skills/update-readme/SKILL.md:69-75

- **Rule:** 1 (the general page backs it), and the report proposes the same hunk. It also fixes a model-independent defect under rule 3: `Never add marketing language or emojis` contradicts `Match existing voice` when a README already uses emojis.
- **Backing quote:** "Tell Claude what to do instead of what not to do. Instead of: 'Do not use markdown in your response'. Try: 'Your response should be composed of smoothly flowing prose paragraphs.'" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, "Control the format of responses")
- **Guides that disagree:** none. The six model guides are silent on this instruction, and the report's pattern 1e (an output-style prohibition with no stated reason) calls for the same rewrite.
- **Before:**
  ```
  - **Match existing voice.** Preserve tone, heading style, formatting conventions.
  ...
  - Never add marketing language or emojis.
  ```
- **After:**
  ```
  - **Match existing voice.** Preserve tone, heading style, formatting conventions, and keep the prose
    plain and technical.
  ```
  The `Never add marketing language or emojis.` line is removed.

I made no other changes:

- **Report's six flag-only items:** The report proposes no edit for these, so I left them alone. They are the `disallowed-tools` conflict in `code-review`, the quoted-path pattern in `update-changelog`, the `cat` calls, the repeated rules, the history note in the README, and the volatile permission-classifier claim.
- **Model-guide patterns:** I found no instruction in the plugin for the guides' main patterns to act on. Those cover subagents, progress updates, parallel tool calls, thinking-disabled artifacts, reasoning echo, and verification instructions. The `update-changelog` and `release` validator steps run a real script, so I did not treat them as over-verification.

This edit is unverified: I ran no validator and no before/after probe. Per the root `CLAUDE.md`, the commit still needs a PATCH bump to `ceh-git-workflow` in `plugin.json` and `marketplace.json`. It also needs a `CHANGELOG.md` entry, a `docs/PLUGIN_VERSIONS.md` row, and a green `python tools/validate-plugins/validate.py`. I did not touch those files, since the task limits edits to the plugin directory.
