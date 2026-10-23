# Architecture schema

`product/ARCHITECTURE.md` in the target repo, committed, unless the repo's `CLAUDE.md` names another
path. `ceh-codebase-explanation:document-architecture` writes it, and
`ceh-build-from-plan:implement-from-plan` appends Key Decisions to it. This file is copied word for
word into both plugins. A new file is a copy of `../assets/architecture.template.md`, relative to
this file. The `schema: architecture/v2` line stays as written. A `v1` file gets its sections
numbered, a Contents list, and the `v2` line on its next update.

## Numbering

- **Sections:** every `##` section after Contents is numbered with two digits, `01.`, `02.`, in
  order, and every `###` subsection with two digits as well: `03.01`, `03.02`, never `03.1`.
- **Anchors:** GitHub heading anchors drop the dots, so `### 03.01 Export: the CLI` links as
  `#0301-export-the-cli`. No em dash in a numbered heading, since it leaves a double hyphen in the
  anchor.

## Sections

- **Contents:** an unnumbered `## Contents` after the title, a linked list of every numbered
  section, with subsections indented under their section. Key Decisions entries are not listed.
- **Overview:** `01. Overview`. A short bullet list, one bullet per idea a newcomer needs: what the
  system does and for whom, then each stage of the system, in problem-domain words. Then a
  left-to-right Mermaid `flowchart` of 3 to 6 domain nodes in one line.
- **Diagram sections:** one numbered `##` section per diagram, named `System context`,
  `Components`, `Key flows`, `Data model`, or `State machines` after the number. A diagram split by
  stage or subsystem gets one numbered `###` subsection per part. Each diagram opens with a short
  walkthrough: one or two sentences on how to read it, then up to three bullets on what to notice,
  then the Mermaid block. The walkthrough never restates the diagram, its table, or Key Decisions.
- **Key Decisions:** always the last section, numbered like the others, with no walkthrough.
  Entries are appended newest last and never deleted. A changed decision gets a new entry, and the
  old one is marked Superseded.

## Key Decisions entry

- **Heading:** `### YYYY-MM-DD — <title>`, a short, descriptive title. Entries are not numbered.
- **Status:** `Accepted`, or `Superseded by <date title>` naming the entry that replaced it.
- **Context:** the problem, the constraints, and the options considered.
- **Decision:** what was decided, explicit and unambiguous.
- **Consequences:** trade-offs, limitations, and follow-ups.
