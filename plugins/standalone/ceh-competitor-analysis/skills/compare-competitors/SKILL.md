---
name: compare-competitors
description: >-
  Load this skill when putting competitors side by side with our own work after each has been
  analysed: one comparison.md, also rendered as a styled HTML page, with an at-a-glance table, an
  inventory by capability showing what
  each one ships and where nobody does, and each one's strengths, weaknesses, and positioning.
  A comparison only, with no adoption roadmap unless asked. Trigger on "compare them with us",
  "comparison report", "master report", "how do we stack up", "side by side with our work", or
  right after ceh-competitor-analysis:analyze-competitor when several competitors were analysed.
  Not for analysing a single competitor (use ceh-competitor-analysis:analyze-competitor).
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Compare competitors

Write `.agents_workspace/competitor-analysis/comparison.md`, comparing every analysed competitor
with our work, and render it as `comparison.html` beside it. Done means a reader can see in under a
minute how the options differ and where each one has a gap, every cell traces back to a
per-competitor report or a command run on our side, and the HTML page carries the same content as
the Markdown.

## Procedure

1. **Gather the inputs.** Read every per-competitor report in
   `.agents_workspace/competitor-analysis/`. When a competitor the user named has no report yet,
   run ceh-competitor-analysis:analyze-competitor for it first. Do not compare from memory.
2. **Measure our side fresh.** Count our components with commands (`ls`, `find`, `wc -l`) rather
   than copying numbers from our own README, which drifts. Note the date.
3. **Pick the dimensions.** Start from the fixed rows under Output. Add rows for any axis on which
   the competitors genuinely differ, such as philosophy, host platform, or invocation model. Drop a
   row on which all of them are identical.
4. **Build the capability inventory.** Make one row per capability, such as review, testing,
   security, or docs, and one column per repo, ours last. Put each repo's components in its cells,
   with `—` where it has nothing. Choose the capability rows from the union of everything every
   repo ships, so that a gap on any side is visible.
5. **Write the comparison** in the shape under Output.
6. **Render the HTML page.** Invoke the Skill tool with skill="ceh-ui-design:design-ui" and build
   `comparison.html` from the Markdown, with the same theme file the per-competitor pages link
   (`themes/<theme>.css`, Tidewater unless the user names another). Link each competitor's
   `.html` page where the Markdown links its `.md`. The page adds no claim the Markdown lacks.

## Rules

- **This is a comparison, not a roadmap.** Do not rank what to adopt or write a "next steps"
  section unless the user asks for one. The per-competitor reports already carry the adoption
  tables.
- **Treat our work the way you treat a competitor.** Name our weaknesses as plainly as theirs. A
  comparison that flatters us is useless for deciding anything.
- **Every cell must trace** to a per-competitor report, a file, or a command. When the reports
  disagree on a number, rerun the measurement rather than picking one.
- **Use the same word for the same concept across columns**, such as "skill", "agent", and "hook",
  even where a competitor uses its own term. Note the mapping once below the table.
- **Be concise.** Use tables first. A mermaid diagram is optional: include it only when it shows the
  structural difference faster than a table, and keep it to about ten nodes.

## Output

```markdown
# Comparison: <competitor A> vs <competitor B> vs <ours>

Detail per competitor: [<a>.md](<a>.md), [<b>.md](<b>.md). Snapshot date <YYYY-MM-DD>.

## At a glance

|                      | **<A>** | **<B>** | **<ours>** |
| -------------------- | ------- | ------- | ---------- |
| One-line pitch       |         |         |            |
| Organizing principle |         |         |            |
| Unit of install      |         |         |            |
| Components (counts)  |         |         |            |
| Invocation / trigger |         |         |            |
| Quality gate         |         |         |            |
| Versioning           |         |         |            |
| <added dimension>    |         |         |            |

<Optional small mermaid diagram.>

## Inventory by capability

`—` means there is no equivalent.

| Capability | <A> | <B> | <ours> |
| ---------- | --- | --- | ------ |

## Where each one is strongest

| Repo | Strongest at | Weakest at |
| ---- | ------------ | ---------- |

## Positioning in one line

<One or two sentences on how each one positions itself, ours included.>
```

## Hands off to

- Invoke the Skill tool with skill="ceh-ui-design:design-ui" to render the HTML page (step 6).
