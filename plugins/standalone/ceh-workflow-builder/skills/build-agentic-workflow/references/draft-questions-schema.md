# Draft questions schema

`<build-dir>/<name>-draft/QUESTIONS.md`, written by `build-agentic-workflow` when it drafts a
workflow with no human to answer. A later interactive run reads it and asks the questions. A new
file is a copy of `../assets/draft-questions.template.md`, relative to this file. The
`schema: draft-questions/v1` line stays as written.

## Frontmatter

- `workflow`: the workflow's name.
- `spec`: the path to the workflow spec the draft was built from.
- `date`: the date of the draft.

## Sections

- **Open spec rows:** one numbered line per spec row the interview left open: the row number, its
  question, and a recommended answer. The draft marks each spot it shapes `OPEN: spec row <n>`.
- **Assumptions to confirm:** one numbered line per conservative choice the draft took in place of
  a question, with a recommendation: keep it, or the alternative.
