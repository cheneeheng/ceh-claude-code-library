# Architecture schema

`.agents_workspace/product/ARCHITECTURE.yaml` in the target repo, with its Markdown rendered beside
it, unless the repo's `CLAUDE.md` names another path. A reference to it names the `.yaml`.
`ceh-codebase-explanation:document-architecture` writes it,
`ceh-build-plan:write-technical-design` writes the Technical Design section and the planned
diagrams settled before the build, and `ceh-build-plan:implement-from-plan` appends Key Decisions
to it and edits a Technical Design entry the build changed. This file is
copied word for word into every skill that reads or writes the file. A new file is a copy of
`../assets/architecture.template.yaml`, relative to this file, per the `architecture/v3` section
below. `../assets/architecture.template.md` is the layout its Markdown is rendered in, and its
`schema: architecture/v2` line names that layout. A `v1` or `v2` Markdown file with no YAML
beside it is moved on its next update, as that section says.

## Numbering

- **Sections:** every `##` section after Contents is numbered with two digits, `01.`, `02.`, in
  order, and every `###` subsection with two digits as well: `03.01`, `03.02`, never `03.1`. A
  `####` part of a Technical Design topic takes a third pair: `04.02.01`.
- **Anchors:** GitHub heading anchors drop the dots, so `### 03.01 Export: the CLI` links as
  `#0301-export-the-cli`, and `#### 04.02.01 Style fields` as `#040201-style-fields`. No em
  dash in a numbered heading, since it leaves a double hyphen in the anchor.

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
- **Technical Design:** the section before Key Decisions, present only when the file holds a
  technical design: the choices several features share, such as the stack or the data model. One
  numbered `###` subsection per topic, which holds the topic's contract as Markdown (lists,
  tables, code blocks), then its **Reason**, then a numbered `####` subsection per part, each a
  small sub-section of the topic. It states the
  current choice, so an entry is edited in place, and a change also adds a Key Decisions entry
  that says what changed and why.
- **Key Decisions:** always the last section, numbered like the others, with no walkthrough.
  Entries are appended newest last and never deleted. A changed decision gets a new entry, and the
  old one is marked Superseded.

## Key Decisions entry

- **Heading:** `### YYYY-MM-DD — <title>`, a short, descriptive title. Entries are not numbered.
- **Status:** `Accepted`, or `Superseded by <date title>` naming the entry that replaced it.
- **Context:** the problem, the constraints, and the options considered.
- **Decision:** what was decided, explicit and unambiguous.
- **Consequences:** trade-offs, limitations, and follow-ups.

## architecture/v3: YAML with generated Markdown

An `architecture/v3` document is `ARCHITECTURE.yaml` beside the `ARCHITECTURE.md` it renders, a
copy of `../assets/architecture.template.yaml`. The Markdown is generated in the `v2` layout above
and saved beside it: nobody edits it, and it opens with `schema: architecture/v3`,
`generated_from: ARCHITECTURE.yaml` and a do-not-edit `generated_note`. The renderer writes the section numbers, the Contents list and
every anchor, so the YAML holds none of them. The format in code is `architecture-model.py` beside
this file, and `scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check .agents_workspace/product/ARCHITECTURE.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render .agents_workspace/product/ARCHITECTURE.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `architecture/v3`.
- `overview`: `bullets` (at least one) and `flow`, the one-line `flowchart LR` without its fence.
- `diagrams`: in order, each with `name` (`System context`, `Components`, `Key flows`,
  `Data model` or `State machines`), `walkthrough`, `notice` (at most 3, `[]` when none), and
  exactly one of `mermaid` (the diagram without its fence) and `parts`. A part is a numbered
  subsection: `title`, `walkthrough`, `notice`, `mermaid`. `planned` (optional) is `true` on a
  diagram of what is not built yet, and is left out of every other diagram: `false` is an error,
  so built has one spelling. Its section opens with `**Planned:** not built yet.` under an
  unchanged heading. A planned diagram that changes what a built one shows is a second entry of
  the same `name`, right after the built one. When the code matches it, the mark is removed and
  the built entry it replaces is deleted.
- `technical_design` (optional): one entry per topic, each with `topic`, `choice`, `reason` and
  `parts` (optional). `topic` is the name a plan cites the entry by, so no two entries share
  one, whatever the case of its letters. `choice` is Markdown that states the contract for the
  topic: paragraphs, lists, tables and code blocks, exact enough to build from. `reason` is one
  short paragraph on why this choice and not the option rejected. `parts` (at least one when
  present) are the topic's sub-sections, each with `title` and `body`, the body Markdown like
  `choice`. A part is small: a body of more than 30 lines is an error, and that part becomes a
  topic of its own. None of the three texts holds a heading line or an unclosed code block,
  which is an error too, because the renderer writes and numbers every heading. The check
  reads Markdown headings (`# x`, a line underlined with `===` or `---`, also at the start of a
  quote or a list item) outside code blocks, and does not see an HTML heading, so write none. An entry
  refers to another by its topic, and to a part by its topic and title, never by a section
  number. A file with no technical design leaves the key out: `[]` is an error, and a
  new file started from the template drops the template's placeholder entry with the key. An
  entry is edited in place when the
  choice changes, and the change gets a `key_decisions` entry. Where an entry covers a topic,
  the entry is what holds now and every `key_decisions` entry on that topic is its history.
- `key_decisions`: newest last, each with `date`, `title`, `status`, `context`, `decision`,
  `consequences`. `status` is `Accepted`, or `Superseded by YYYY-MM-DD <title>` naming another
  entry by its date and title. An entry is never deleted. `[]` when none.

No title or name holds an em dash, which would leave a double hyphen in its anchor. Free text goes
in `|` blocks or quotes, because ` #` starts a YAML comment and a `: ` in a plain value breaks it.

A `v1` or `v2` `ARCHITECTURE.md` with no YAML beside it is moved on its next update: write
`ARCHITECTURE.yaml` from it, render, and check `git diff --no-index --word-diff` between a copy of
the old Markdown and the rendered one before the update itself, which works whether or not the
folder is a git repo. Text the YAML cannot hold goes in the nearest free-text field, and the reply
names the move and any line the diff shows changed. A diagram set split into files in an
`architecture/` folder beside it moves back into the one YAML.
