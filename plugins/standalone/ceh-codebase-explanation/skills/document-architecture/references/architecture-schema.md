# Architecture schema

`product/ARCHITECTURE.md` in the target repo, committed, unless the repo's `CLAUDE.md` names another
path. `ceh-codebase-explanation:document-architecture` writes it, and
`ceh-build-from-plan:implement-from-plan` appends Key Decisions to it. This file is copied word for
word into both plugins. A new file is a copy of `../assets/architecture.template.md`, relative to
this file. The `schema: architecture/v1` line stays as written.

## Sections

- **Overview:** one sentence on what the system does, and for whom, in problem-domain words, then
  a left-to-right Mermaid `flowchart` of 3 to 6 domain nodes in one line.
- **Diagram sections:** one `##` section per diagram, named `System context`, `Components`,
  `Key flows`, `Data model`, or `State machines`. Each opens with one line stating what the
  diagram shows, then the Mermaid block.
- **Key Decisions:** always the last section. Entries are appended newest last and never deleted.
  A changed decision gets a new entry, and the old one is marked Superseded.

## Key Decisions entry

- **Heading:** `### YYYY-MM-DD — <title>`, a short, descriptive title.
- **Status:** `Accepted`, or `Superseded by <date title>` naming the entry that replaced it.
- **Context:** the problem, the constraints, and the options considered.
- **Decision:** what was decided, explicit and unambiguous.
- **Consequences:** trade-offs, limitations, and follow-ups.
