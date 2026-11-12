# Architecture schema

`product/ARCHITECTURE.md` in the target repo, committed, unless the repo's `CLAUDE.md` names another
path. `ceh-codebase-explanation:document-architecture` writes it, and
`ceh-build-plan:implement-from-plan` appends Key Decisions to it. This file is copied word for
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

## architecture/v3: YAML with generated Markdown

An `architecture/v3` document is `ARCHITECTURE.yaml` beside the `ARCHITECTURE.md` it renders, a
copy of `../assets/architecture.template.yaml`. The Markdown is generated in the `v2` layout above
and committed beside it: nobody edits it, and it opens with `generated_from: ARCHITECTURE.yaml` and
a do-not-edit `generated_note`. The renderer writes the section numbers, the Contents list and
every anchor, so the YAML holds none of them. The format in code is `architecture-model.py` beside
this file, and `scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check product/ARCHITECTURE.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render product/ARCHITECTURE.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `architecture/v3`.
- `overview`: `bullets` (at least one) and `flow`, the one-line `flowchart LR` without its fence.
- `diagrams`: in order, each with `name` (`System context`, `Components`, `Key flows`,
  `Data model` or `State machines`), `walkthrough`, `notice` (at most 3, `[]` when none), and
  exactly one of `mermaid` (the diagram without its fence) and `parts`. A part is a numbered
  subsection: `title`, `walkthrough`, `notice`, `mermaid`.
- `key_decisions`: newest last, each with `date`, `title`, `status`, `context`, `decision`,
  `consequences`. `status` is `Accepted`, or `Superseded by YYYY-MM-DD <title>` naming another
  entry by its date and title. An entry is never deleted.

No title or name holds an em dash, which would leave a double hyphen in its anchor. Free text goes
in `|` blocks or quotes, because ` #` starts a YAML comment and a `: ` in a plain value breaks it.

A `v1` or `v2` `ARCHITECTURE.md` with no YAML beside it is moved on its next update: write
`ARCHITECTURE.yaml` from it, render, and check `git diff --word-diff` on the Markdown before the
update itself. Text the YAML cannot hold goes in the nearest free-text field, and the reply names
the move and any line the diff shows changed. A diagram set split into `product/architecture/`
files moves back into the one YAML.
