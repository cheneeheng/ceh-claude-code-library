# Model audit: ceh-ag-ui

- Date: 2026-10-23
- claude-code 2.1.309
- Edits applied: no

## Unpinned audit against fable-5, fable-5-1, haiku-5-5, opus-5, opus-5-5, sonnet-5, sonnet-5-5

Audit model: sonnet-5-5, effort: medium. Raw output: [ceh-ag-ui.doctor.md](ceh-ag-ui.doctor.md).

## Kept changes

### plugins/standalone/ceh-ag-ui/skills/build-ag-ui/SKILL.md:35

- **Rule:** 4, with 1 as backing. The positive form says the same thing as the negative.
- **Backing quote:** "Tell Claude what to do instead of what not to do. Instead of: 'Do not use markdown in your response'. Try: 'Your response should be composed of smoothly flowing prose paragraphs.'" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices, "Control the format of responses")
- **Before:**
  ```
  `web/` and `agent/` at the repo root). Always copy, and never edit the files under the skill
  directory.
  ```
- **After:**
  ```
  `web/` and `agent/` at the repo root). Copy it, and edit only the copy.
  ```

### plugins/standalone/ceh-ag-ui/skills/build-ag-ui-agent/assets/agent-server/main.py:41

- **Rule:** 4, with 1 as backing. The system prompt already says the app fixes how components look. The rewrite names what to send instead of the prohibition, and Rule 6 of the skill states the same contract.
- **Backing quote:** the same "Control the format of responses" passage as above (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices).
- **Before:**
  ```
  "component fits. How components look is fixed by the app; never try to style them."
  ```
- **After:**
  ```
  "component fits. How components look is fixed by the app, so send content only."
  ```

---

I left out these things:

- **Qualitative text ceiling:** `main.py:39-41` ("keep any text to a sentence or two"). The `/doctor` report flags it as low confidence and leaves it alone. It serves a real layout constraint, and I follow the report.
- **"Keep working" and "stop and report" paragraphs:** Haiku 5.5 and Sonnet 5.5 would benefit from these. The files show no early-stopping need, and the Fable 5.1 text calls its additions "extras only" for open-ended features.
- **Verification instructions:** the Haiku 5.5 and Sonnet 5.5 guides recommend them, but the Opus 5 guide says they cause over-verification. The skills already carry their own mock-agent checks.
- **Fable 5.1 batching and progress-update advice:** none of the five skills or the server file makes independent tool calls or narrates progress, so none applies.
- **Defects:** I found no missing file, command or symbol, and no contradictory instructions. The step-count references line up with the bodies, as the report says.
