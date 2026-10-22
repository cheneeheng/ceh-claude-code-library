# Learning schema

The opt-in learning workspace of `explain-until-understood`, one file per subject at
`.agents_workspace/learning/<subject>.md`. A new file is a copy of
`../assets/learning.template.md`, relative to this file. The `schema: learning/v1` line stays as
written.

## Frontmatter

- `subject`: the subject being learned, matching the file name.

## Body

- **Goal:** what the reader wants to be able to do, in their words.
- **Next:** the one thing the next session explains first.
- **Terms:** one row per term, with the definition as the reader put it back. A term is recorded
  only once the reader has said it back in their own words.
- **Rules of thumb:** each transferable rule an explanation closed on.
- **Self-test:** one row per question. Last answer is `unaided`, `missed`, or `—` when not yet
  asked, and Date is when it was last asked.
- **Open questions:** questions the reader raised that no explanation has settled yet.
