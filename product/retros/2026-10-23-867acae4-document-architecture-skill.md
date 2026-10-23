# Retro: document-architecture skill, from the usage-insights ARCHITECTURE.md rewrite

- **Date:** 2026-10-23
- **Session:** 867acae4-ec2f-4302-9500-ecbfcc48d00f
- **Skill:** `ceh-codebase-explanation:document-architecture` (1.2.7), its
  `assets/architecture.template.md` and `references/architecture-schema.md`
- **Trigger:** the user found the skill's output for `apps/usage-insights/product/ARCHITECTURE.md`
  hard to read for a new developer, and asked for the changes below. This file records what to
  change and why. Written in `claude-code-command-center` and moved here, where the changes landed
  in `ceh-codebase-explanation` 1.2.8 and `ceh-build-from-plan` 1.0.10.
- **Result in `claude-code-command-center`:** branch `docs/usage-insights-architecture-readability`, the worked
  example of every change below.

## What went wrong in the skill's output

1. **One Components diagram for the whole app.** It had 20+ edges, several unlabeled, edges
   crossing the whole width, and lines back-tracking to `server.py`. The skill says "split it by
   subsystem" only when a diagram stops fitting one screen. It fitted, and was still unreadable.
2. **Sections were bare diagrams or bare tables.** The skill's "one line of prose per diagram"
   produced no explanation a newcomer could follow: nothing said which way to read a diagram or
   what in it would surprise them.
3. **The Overview was one dense paragraph.** Six separate ideas (what it is, export, aggregate,
   render, chat, shared libraries) sat in one block of prose.
4. **No section numbers and no table of contents** in a document over 270 lines.

## Changes to make in the skill

### 1. Replace the one-sentence and one-line hard limits with "the minimum text needed"

User's words: the one-sentence hard limit should be relaxed to the minimal amount of text or
sentences needed.

- **Overview:** drop "One sentence". Allow a short bullet list, one bullet per idea a newcomer
  needs (what it is, then each stage of the system), keeping the 3-to-6-node spine flowchart
  under it. Keep the domain-words rule.
- **Each diagram section:** drop "One line of prose per diagram". Allow a short walkthrough: one
  or two sentences on how to read the diagram, then up to three bullets on what to notice (the
  surprising branch, the lock, the two-request round trip). It must not restate the diagram, the
  table, or Key Decisions. Keep the ban on walls of text.
- Update the same wording in `references/architecture-schema.md` ("Each opens with one line
  stating what the diagram shows") and the template placeholder `<what the diagram shows>`.

### 2. Split diagrams by readability, not only by screen size

- Split Components by stage or subsystem when the edges stop reading cleanly (crossing,
  back-tracking, more than about a dozen edges), not only when it stops fitting one screen.
- Let a node shared between two split diagrams (a database, the server) be the join point, and
  say so in the section's walkthrough.
- When a diagram has many outbound calls to one node, consider naming the endpoint inside each
  calling node instead of drawing every arrow to it. In usage-insights' browser diagram this
  removed five long crossing edges.
- Group externals in `subgraph`s (inputs, fetched over the network) and draw one edge to the
  group, instead of one edge per external.
- Add a check step: render every Mermaid block (for example with `@mermaid-js/mermaid-cli`) and
  look at the images before finishing. Two of the four flowcharts in this session still had
  crossing edges after the first rewrite and were only caught that way.

### 3. Number sections and add a table of contents

- Number every `##` section `01.`, `02.`, and so on, and every `###` subsection with two digits
  as well: `03.01`, `03.02`, never `03.1`.
- Put a linked `## Contents` list at the top, after the title and before `01. Overview`, with
  subsections indented under their section.
- Key Decisions is numbered too (it is the last section), but needs no walkthrough. Its entries
  (`### YYYY-MM-DD — title`) are not numbered and not listed in the contents.
- GitHub heading anchors drop the dots: `### 03.01 Export: ...` links as `#0301-export-...`.
  Avoid em dashes in numbered headings, since they leave a double hyphen in the anchor.
- Update the schema's section names (`System context`, `Components`, ...) to allow the number
  prefix, and the template to show it.

## Out of scope here

- Key Decisions entries were left as they were.
- The two sequence diagrams were already clean. They only gained a number and a walkthrough.
