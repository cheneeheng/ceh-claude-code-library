# Questionnaire schema

The file `write-questionnaire` saves to `.agents_workspace/questionnaires/<YYYYMMDD>-<topic>.md`,
for someone not in the session to answer. A new file is a copy of
`../assets/questionnaire.template.md`, relative to this file. The `schema: questionnaire/v1` line
stays as written.

## Frontmatter

- `topic`: what the questions are about.
- `from`: who is asking, or `Claude Code session`.
- `date`: the date the file was written.

## Body

- **Intro line:** who is asking and the date, then how to answer. It stays as the template words
  it, because the reader has no other instructions.
- **Questions:** one numbered `## <n>. <question>` per question, the question in one sentence.
  - **Context:** two to four sentences: the facts needed to answer, in plain words.
  - **Blocks:** what work waits on this.
  - **Options:** lettered, each with its consequence, the recommended one marked
    `(recommended)`.
  - **Answer:** left empty for the reader.

## Issue form

With `write --issue`, the same filled file is posted as a GitHub issue body, titled
`Questions on <topic>`, and no file is saved. Only the intro line differs, because the reader may
also answer in a comment: "From: <asker>, YYYY-MM-DD. Answer on the `Answer:` line under each
question, here or in a comment as `Answer <n>: <text>`. Leave a line blank to skip it." Read with
`--issue` takes, per question, the newest of the body's `**Answer:**` line and each comment's
`Answer <n>:` line, the body counting as oldest. A blank newest answer is still open.
