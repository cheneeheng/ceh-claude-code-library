# Research note schema

The note `write-research-note` saves to `.agents_workspace/research/<YYYYMMDD>-<topic>.md`. A new
note is a copy of `../assets/research-note.template.md`, relative to this file. The
`schema: research-note/v1` line stays as written.

## Frontmatter

- `question`: the question researched.
- `feeds`: the decision the answer feeds.
- `researched`: the research date.

## Body

- **Header lines:** the decision fed and the date, then `Checked:` naming the claims the session
  re-fetched itself and the result.
- **Answer:** three to five sentences, each with its source number `[n]`.
- **Findings:** one bullet per claim, each with its source numbers. A contested claim is quoted.
  What follows from the cited findings, rather than from a source, is labelled `Inference:`.
- **Not found:** what was searched for and where, with no result.
- **Sources:** numbered, each with its title, URL, published or updated date, and `primary` or
  `secondary`.
