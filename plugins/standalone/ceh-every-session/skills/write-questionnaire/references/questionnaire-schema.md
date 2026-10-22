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
