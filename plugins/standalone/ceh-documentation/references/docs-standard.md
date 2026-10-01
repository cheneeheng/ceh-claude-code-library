# Documentation Standard

The one format every `ceh-documentation` writing skill produces. A page written by any of them must
be indistinguishable in layout, naming, and furniture from a page written by another, so a docs set
built across several runs reads as one site. Where a skill's own text disagrees with this file, this
file wins.

## 1. Layout

All docs live under `<root>/docs/`, where `<root>` is the project being documented.

```text
docs/
├── index.md              # site front page — no breadcrumb
├── why.md                # site-level page
├── migration.md          # site-level page
├── guide/                # section: tutorials, how-to, troubleshooting — the user's tasks
│   ├── index.md          # section hub
│   ├── getting-started.md
│   ├── troubleshooting.md
│   └── how-to/           # HT-NN pages
├── operations/           # section: the operator's runbook, OP-NN pages
│   └── index.md          # nested folders chain the prefix (OP-DB-NN)
├── concepts/             # section: CO-NN pages
│   └── index.md
├── reference/            # section: pages named after the code, never numbered
│   └── index.md
└── examples/             # section: EX-NN pages
    └── index.md
```

- **Section** — a folder directly under `docs/`. Every section has an `index.md` hub.
- **Subfolder** — a folder inside a section (`guide/how-to/`). No hub; its section hub lists it.
- **Only write what has content.** A section or subfolder that would hold one page is a single
  file at its parent level instead (`docs/concepts.md`, `guide/troubleshooting.md`). Once it grows
  to two pages, it becomes a folder.
- **Existing pages keep their path.** An existing page that fills a planned slot (an old
  `docs/setup.md` serving as the install how-to) takes that slot's mode, is listed by that
  section's hub, and gets the breadcrumb its location calls for. When the slot is in a numbered
  folder, the page stays outside it: the hub lists it at its old path, the folder numbers the
  remaining pages from `01`, and it joins no footer chain. "Edit in place" means keep the path; the
  content may be rewritten when the user asked for a redo.
- **Design records are not docs pages.** ADRs, decision logs, and RFCs under `docs/` are linked
  from the concept pages that cite them, never restyled, renamed, or held to §4.
- **Only `write-project-docs` creates `docs/index.md`.** A skill run on its own writes its section
  and hub, and leaves the front page to that skill.

## 2. Page modes

Every page has exactly one mode. A page that needs two modes is two pages.

| Mode       | Answers                           | Lives in                                                                 | Voice                        |
| ---------- | --------------------------------- | ------------------------------------------------------------------------ | ---------------------------- |
| Tutorial   | "Get me to a first success"       | `guide/getting-started.md`                                               | Imperative, no options       |
| How-to     | "How do I do this task?"          | `guide/how-to/`, `operations/`, `guide/troubleshooting*`, `migration.md` | Imperative, numbered steps   |
| Concept    | "How does this work, and why?"    | `concepts/`, `why.md`                                                    | Explanatory, no procedures   |
| Reference  | "What exactly does this item do?" | `reference/`                                                             | Terse, complete, no teaching |
| Example    | "Show me a whole working program" | `examples/`                                                              | Code first, one-line framing |
| Hub        | "What is in this section?"        | `<section>/index.md`                                                     | One line per page            |
| Front page | "What is this and where do I go?" | `docs/index.md`                                                          | One screen, routes only      |

The "Lives in" column is where the mode usually sits, not a constraint on the folder: a runbook's
system-overview page in `guide/operations/` is Concept mode, and a standalone guide's settings table
is Reference mode. What stays fixed is one mode per page. These seven names are the only values of
the report's Mode column.

## 3. File naming

- **Site-level and section-level pages** — plain kebab-case, no prefix, no number:
  `why.md`, `guide/getting-started.md`.
- **Numbered pages** — every page inside a numbered folder is `<PREFIX>-<NN>-<kebab-name>.md`.
  `NN` is two digits from `01`, contiguous, and is the reading order. Appending takes the next
  number; inserting or removing renumbers the rest of that folder and fixes every link to a renamed
  file in the same pass. Never leave a gap.
- **Fixed prefixes** — use these exactly:

  | Folder                   | Prefix |
  | ------------------------ | ------ |
  | `guide/how-to/`          | `HT`   |
  | `operations/`            | `OP`   |
  | `guide/troubleshooting/` | `TS`   |
  | `concepts/`              | `CO`   |
  | `examples/`              | `EX`   |

  Any other numbered folder takes a capitalized abbreviation of its name, at least 2 characters,
  unique across the docs tree. A nested folder chains its parent prefix (`operations/database/` →
  `OP-DB-`) and restarts at `01`.

- **Reference pages are never numbered.** They are named after the code they document
  (`reference/client.md`, `reference/cli.md`, `reference/configuration.md`, `reference/errors.md`),
  because readers arrive by name, not in order.
- A docs framework never renames a file out of this scheme. Nav order and titles go in frontmatter
  or nav config.

## 4. Page anatomy

Every page, in this order:

```markdown
# HT-02 — Reset a password

[← Guide](../index.md)

Reset a user's password from the admin console. Use this when a user is locked out.

## <Body headings>

…

---

[← HT-01 Change your email](HT-01-change-email.md) · [Guide](../index.md) · [HT-03 Export data →](HT-03-export-data.md)
```

1. **H1** — exactly one. A numbered page repeats its ID: `# <PREFIX>-<NN> — <Title>`. A reference
   page uses the module or resource name. Other pages use a plain title.
2. **Breadcrumb** — the line directly under the H1, linking the nearest hub:

   | Page                                                                 | Breadcrumb                                                                                   |
   | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
   | `docs/index.md`                                                      | none                                                                                         |
   | Site-level page (`why.md`, a one-file section such as `concepts.md`) | `[← Docs home](index.md)`, only when `docs/index.md` exists or is written in the same run    |
   | Section hub (`guide/index.md`)                                       | `[← Docs home](../index.md)`, only when `docs/index.md` exists or is written in the same run |
   | Section-level page (`guide/getting-started.md`)                      | `[← Guide](index.md)`                                                                        |
   | Page in a subfolder (`guide/how-to/HT-02-…`)                         | `[← Guide](../index.md)`                                                                     |
   | Page in a nested subfolder                                           | `[← Guide](../../index.md)`                                                                  |
   | Page in a numbered section (`concepts/CO-02-…`)                      | `[← Concepts](index.md)`                                                                     |

   The label is the hub's name: Docs home, Guide, Operations, Concepts, Reference, Examples.

3. **Summary** — one or two sentences: what the page answers and when to read it. No heading.
4. **Body** — `##` and below, never skipping a level.
5. **Footer** — numbered pages only: a `---` rule, then prev · hub · next, following `NN` order
   **within the page's own folder**. The first page drops prev, the last drops next. Never link
   across two folders' chains. Unnumbered pages and hubs have no footer.

**Hub pages** list every page of their section — grouped by subfolder; a hub with a single group
drops the group heading — in `NN` order, each as
`- [<ID> <Title>](<path>) — read this when <situation>.` An unnumbered page drops the ID:
`- [Troubleshooting](troubleshooting.md) — read this when <situation>.` The site `index.md` routes to the section
hubs and site-level pages; it does not list every page.

## 5. Markdown rules

- **A single newline is not a line break.** Separate paragraphs with a blank line. Use two trailing
  spaces only where a blank line would wrongly split a block.
- One blank line before and after every heading, list, table, fenced block, and blockquote.
- Do not hard-wrap prose at a fixed column; the renderer wraps.
- Headings in sentence case. How-to headings start with a verb ("Rotate the signing key"); concept
  headings are nouns. **Troubleshooting and incident entries** are headed by the symptom or the
  literal error text the reader will search for ("`QueueFullError: queue holds 100 jobs`"); for an
  HTTP error, the status code plus the `detail` text, spelled exactly as its reference heading
  (`` `401 invalid api key` ``).
  **Reference headings** are the item's name only, in backticks — `Queue.run`, `POST /notes`,
  `QueueFullError` — never the full signature, which goes in the code block below it: a heading
  that carries defaults changes its anchor whenever a default changes.
- Numbered lists only for ordered steps; bullets for everything else. Inside a numbered step, indent
  a nested block by 3 spaces so the list does not restart.
- **Every fenced block has a language tag** — the language's usual tag (`bash`, `powershell`,
  `python`, `ts`, `json`, `yaml`, `toml`, …), `text` for output and trees, `mermaid` for diagrams.
  Commands carry no `$` prompt.
- A command the reader runs as a step is fenced. A short command mentioned inside a sentence or a
  table cell ("`docker ps` lists it") stays inline.
- Output goes in its own `text` block introduced by "Expected output:". When the output is long or
  differs per machine (`pip install`, `python --version`), state the success signal in prose
  instead ("the last line reads `Successfully installed tinyq-0.3.0`"). When a step prints nothing
  useful, omit the output.
- Diagrams are Mermaid, never ASCII art. Directory trees are the one exception, in a `text` block.
- Tables have a header separator row and leading and trailing `|`, at most 5 columns; a literal
  pipe inside a cell is `\|`.
- Bold UI labels exactly as shown: **Save**. Code names, paths, flags, and env vars in backticks.

## 6. Links

- Relative paths with the `.md` extension: `../reference/client.md#clientstream`.
- Troubleshooting and incident entries link the error's reference entry, or — for an error the
  project does not own (`ModuleNotFoundError`) — the reference entry of the input that causes it. In
  a standalone guide with no `docs/reference/`, the guide's own settings page is the reference.
- Anchors are GitHub-style slugs of the target heading: lowercase, spaces to `-`, punctuation
  except `-` and `_` dropped. Check the slug against the real heading, never guess it.
- Every link must resolve to an existing file and heading by the end of the run. Linking a page
  planned in the same run but not yet written is allowed; the final link pass must find it.
- External links use the full URL.
- **Explain once, link everywhere.** A concept is explained on its concept page, an exact value
  lives in its reference entry, a procedure in its how-to. Every other page links there.

## 7. Markers

Use these literals exactly, so a reader and a grep both find them. `<version>` is always spelled as
the git tag spells it (`v0.3.0`); the changelog only decides which release an item belongs to. With
no tags, spell it as the changelog heading does (`1.2.0`). An item that neither the changelog nor
git history dates gets no marker and is treated as initial-release.

| Marker          | Format                                                                                                                                                                                                    | Where                                                                                                                                                                              |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Unverified      | `[VERIFY: <what to check>]` inline, at the claim                                                                                                                                                          | Any page; every one is also listed under Open items in the report                                                                                                                  |
| Samples not run | `[VERIFY: samples on this page not run]` once, directly under the summary; when only some ran, `[VERIFY: sample below not run]` directly above each unrun block                                           | Any page with a sample — a fenced command, code block, expected output, or example response body — that was derived from reading the code, not executed                            |
| New item        | `_Added in <version>._` after the entry's first sentence; for a new parameter, at the end of its table row; when every item on a page arrived in one release, once at the end of the page summary instead | Items added in the last three releases, never the initial release                                                                                                                  |
| Changed         | `_Changed in <version>: <what changed>._` after the Added marker, or after the first sentence when there is none; for a changed parameter, at the end of its table row                                    | Behavior or default changes in the last three releases                                                                                                                             |
| Deprecated      | `> **Deprecated in <version>:** use <replacement>. Removed in <version>.`                                                                                                                                 | First line after the reference heading                                                                                                                                             |
| Warning         | `> **Warning:** <risk and blast radius>`                                                                                                                                                                  | Before the action it guards: in prose, the block before it; in a numbered procedure, the first block **inside** the dangerous step, indented 3 spaces so the list does not restart |
| Note            | `> **Note:** <aside>`                                                                                                                                                                                     | Sparingly; never to hold a required step                                                                                                                                           |
| Placeholder     | `<angle-brackets>` with a concrete example beside it                                                                                                                                                      | Commands and config                                                                                                                                                                |

A registry install (`pip install tinyq`, `npm install slugkit`) checked only from a local copy is
not verified: it carries an inline `[VERIFY: published on <registry> under this name]`.

A copied sample keeps its source's status: a snippet copied onto `docs/index.md` from a page marked
"samples not run" is not run either, and carries the marker too.

## 8. Voice

- Second person, present tense, active voice. Procedures are imperative: "Run the migration".
- One term per concept across the whole docs set; the reference name wins a conflict.
- No marketing adjectives, no emoji, no "simply" or "just".
- **Never invent.** Every command, flag, default, signature, label, and rationale comes from the
  code, its history, a design record, or the documented behavior of a named dependency or tool
  (Docker, uvicorn, the stdlib). Anything else is a `[VERIFY: …]`.
- **Conventions are not inventions, if declared.** When a procedure needs a name the project does
  not define (a container name, a volume, a backup directory), pick one, declare every such name
  once in a "Names used in this guide" table — on the system-overview page when there is one,
  else on the hub — with a single
  `[VERIFY: match these names to the real deployment]`, and use them consistently. A setting the
  code supports may be recommended with a value the repo never uses; a setting it does not
  support may not. An operational choice the project leaves open (a restart policy, file
  permissions, a backup method) is a recommendation: state it once with its one-line reason.

## 9. Frontmatter

None by default. When a docs framework is configured (`mkdocs.yml`, `docusaurus.config.*`,
`astro.config.*` with Starlight, Sphinx `conf.py`), add only the keys it needs for nav and title,
and register every new page in its nav config in the same pass. Keep existing nav entries and
their labels; append site-level pages, then one group per section with its hub first and its pages
in `NN` order, labelled by title:

```yaml
nav:
  - Home: index.md
  - Why notesvc: why.md
  - Guide:
      - guide/index.md
      - Get started: guide/getting-started.md
      - HT-01 Delete a note: guide/how-to/HT-01-delete-a-note.md
  - Reference:
      - reference/index.md
      - Notes API: reference/notes.md
```

## 10. Report

Every writing skill ends its reply with the same shape:

```markdown
<One line: what was written, for whom, where.>

| Page                            | Mode     | Status  |
| ------------------------------- | -------- | ------- |
| `docs/guide/getting-started.md` | Tutorial | written |

### Open items

- `docs/reference/client.md` — [VERIFY: default for `retries`]
```

Mode is one of the seven names in §2. Status is `written`, `updated`, `unchanged`, or
`cut — <reason>`; a skill may append detail after an em dash (`written — why: ADR 0001`). "Open
items" lists every `[VERIFY: …]` left in the docs and anything counted but not documented, except
the samples-not-run marker, which gets one line naming every page that carries it. Write "None"
when empty. A reference coverage line, when there is one, sits above the table in one form:
`Reference coverage: 19 of 19 public items documented (API 12/12, CLI 4/4, configuration 1/1, errors 2/2).`

**When another skill called this one**, return only the table rows and open items. The caller
merges every delegated result into the single report it ends its own reply with — the user sees one
report per run, not one per skill.
