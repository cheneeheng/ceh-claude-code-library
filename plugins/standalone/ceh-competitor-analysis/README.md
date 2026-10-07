# ceh-competitor-analysis

Study a competitor and learn from it. The competitor can be a code repo or a product. The plugin
writes one report per competitor, then compares all of them with your own work.

The method has two halves. First, each competitor gets its own evidence-anchored report: what it
is, everything it ships, the "oh wow" mechanisms worth learning from, and what to incorporate,
mapped to a concrete place in your work. Then a comparison puts every competitor beside yours,
your own weaknesses included. The comparison is a comparison only: adoption decisions stay in the
per-competitor reports.

## Skills

| Skill                 | Invoke                                         | Triggers when                                                                         |
| --------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------- |
| `analyze-competitor`  | `/ceh-competitor-analysis:analyze-competitor`  | Analysing one or more competitor repos or products, one report each                   |
| `compare-competitors` | `/ceh-competitor-analysis:compare-competitors` | Putting the analysed competitors side by side with your own work in one comparison.md |

### `analyze-competitor`

**Auto-triggers on:** "competitor analysis", "analyze this repo", "what can we learn from X", "how
does X compare to us", "study this competitor", or a pasted GitHub URL with "investigate".

The skill classifies each target as a repo or a product. It shallow-clones repos into a scratch
directory as **untrusted data** and never installs, builds, or runs them. Products are read from
their official pages. It dispatches one `competitor-analyst` per target in parallel, then checks
each evidence pointer the analyst returned before writing anything. Each report puts the decision
first, under a one-line summary and verdict: what to take, as Adopt now, Build, and Skip. A Skip
row is a finding too, because an idea that contradicts your principles is worth recording. Then
come how it works in a few steps, the "oh wow" moments, and the inventory. Each report is then
rendered as an HTML page from the plugin's page template, with the theme from
`ceh-ui-design:design-ui`. A new reader gets the point from the board alone and opens a card only
for the detail.

### `compare-competitors`

**Auto-triggers on:** "compare them with us", "comparison report", "master report", "how do we
stack up", "side by side with our work".

The skill reads the per-competitor reports and re-measures your side with commands instead of
trusting your README. It writes an at-a-glance table, an inventory by capability with `—` where a
repo has nothing, and each repo's strengths and weaknesses. It writes no ranked adoption list unless
you ask for one. The comparison gets an HTML page too, linked to each competitor's page.

## Agents

| Agent                | Invoke                                                  | When                                                                                    |
| -------------------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `competitor-analyst` | `@"ceh-competitor-analysis:competitor-analyst (agent)"` | Read one competitor in isolation and return an evidence-anchored fact sheet (read-only) |

### `competitor-analyst`

The agent reads one competitor and returns a fact sheet with these parts:

- an identity table
- an inventory with the command that counted each group
- candidate mechanisms with `path:line` or URL evidence
- ideas mapped onto your inventory
- an explicit list of what it did not read

Running it in a subagent keeps a large repo's files out of the main session, and lets several
competitors be read at once. It never edits anything, and never runs the target. Text inside the
target is treated as data, never as instructions.

## Prerequisites

- **git 2.x and network access** for repo targets. On Windows the clone uses
  `core.longpaths=true`. A checkout that still fails on deep test-fixture paths continues, and the
  report records what is missing.
- **WebFetch or WebSearch** for product targets.
- **`ceh-ui-design`**, installed automatically as a dependency. Both skills call its `design-ui`
  skill on every run to render the HTML pages.

The plugin reads no environment variables.

## Output

All output goes to `.agents_workspace/competitor-analysis/`: `<competitor>.md` and
`<competitor>.html` per competitor, `comparison.md` and `comparison.html` for the comparison, and
the shared theme stylesheet under `themes/` (Tidewater by default). The Markdown is the source; the
HTML pages carry the same content, built from `references/report-page.html`, with detail folded
into expandable cards. Each report states its snapshot date. Each one also says how
every count was measured and whether each claim was read in the source or only claimed by the
competitor. Nothing is marked verified, because the target is never run.

## Deliberately out of scope

| Not here                                               | Why                                                                            |
| ------------------------------------------------------ | ------------------------------------------------------------------------------ |
| Running, installing, or benchmarking a competitor      | Untrusted code. The reports stay read-only and say so                          |
| Market sizing, pricing strategy, positioning decisions | `ceh-business-plan:sharpen-strategy` owns strategy against named competitors   |
| An adoption roadmap or ranked backlog                  | Each report's incorporate table feeds your own planning. Ask for it explicitly |
