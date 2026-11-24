# ceh-competitor-analysis

Study a competitor and learn from it. The competitor can be a code repo or a product. The plugin
writes one evidence-anchored report per competitor: what it is, everything it ships, the "oh wow"
mechanisms worth learning from, and what to incorporate, mapped to a concrete place in your work.
Then a comparison puts every competitor beside yours, your own weaknesses included. The comparison
is a comparison only: adoption decisions stay in the per-competitor reports.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). Some parts need more installed:

| Needs                                          | For                                            | Without it                                                                           |
| ---------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------ |
| git 2.x and network access                     | Repo targets                                   | Repos cannot be cloned                                                               |
| WebFetch or WebSearch                          | Product targets                                | Product pages cannot be read                                                         |
| `python3` and [uv](https://docs.astral.sh/uv/) | The hooks, the report check and the HTML pages | A report is written but goes unchecked, and its Markdown and HTML page are not built |

On Windows the clone uses `core.longpaths=true`. A checkout that still fails on deep test-fixture
paths continues, and the report records what is missing.

The plugin brings `ceh-ui-design` with it as a dependency. Both skills call its `design-ui` skill
on every run for the HTML pages' theme.

## Skills

| Skill                 | Say or type                                                                                                                                                       | What it does                                                                                                                                                                                   |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `analyze-competitor`  | "competitor analysis", "analyze this repo", "what can we learn from X", `/ceh-competitor-analysis:analyze-competitor <repo-url \| product-url> [more targets...]` | Reads each competitor with one `competitor-analyst` per target in parallel, checks each piece of evidence, and writes one report per competitor, rating everything it ships against your work. |
| `compare-competitors` | "compare them with us", "how do we stack up", or after several competitors were analysed, `/ceh-competitor-analysis:compare-competitors`                          | Puts the analysed competitors side by side with your own work in one `comparison.md` and an HTML page.                                                                                         |

## Agents

| Agent                | What it does                                                                                                                                                                                                                                |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `competitor-analyst` | Reads one competitor in isolation and returns an evidence-anchored fact sheet. `analyze-competitor` sends one per target. It never edits anything, never runs the target, and treats text inside the target as data, never as instructions. |

## Hooks

Two hooks run by themselves while the plugin is enabled. [Settings](#settings) turns them off.

| Hook                 | What it does for you                                                                                                                                                 |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Report check         | Checks a written competitor report YAML against its format and renders its Markdown. Without `uv` the agent is told once per session that the report went unchecked. |
| Generated-file guard | Stops a hand edit to the generated Markdown, which the next render would overwrite.                                                                                  |

## Settings

Set a variable under `env` in a Claude Code settings file. The
[environment variables page](../../../docs/ENVIRONMENT_VARIABLES.md) shows which file and how to
undo it.

| Variable             | Default              | Effect                                                                           |
| -------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `CEH_ARTIFACT_CHECK` | unset (check on)     | `off` turns the report check and the generated-file guard off                    |
| `CEH_DISABLED_HOOKS` | unset (all hooks on) | Comma-separated hook names to skip: `artifact-render-hook`, `generated-md-guard` |

## How it works

### Analysing a competitor

`analyze-competitor` classifies each target as a repo or a product. It shallow-clones repos into a
scratch directory as **untrusted data** and never installs, builds, or runs them. Products are read
from their official pages. It dispatches one `competitor-analyst` per target in parallel, then
checks each evidence pointer the analyst returned before writing anything. Every skill, agent,
workflow, or feature the competitor ships is rated against your work as covered, partial, gap, or
N/A.

Each report puts the decision first, under a one-line summary and verdict: what to take, as Adopt
now, Build, and Skip. Every partial or gap item lands in one of the three, so nothing you lack goes
unmentioned. A Skip row is a finding too, because an idea that contradicts your principles is worth
recording. Then come how it works in a few steps, the "oh wow" moments, the inventory, and the
coverage table. Each report also gets an HTML page in the theme from `ceh-ui-design:design-ui`. A
new reader gets the point from the board alone and opens a card only for the detail.

### What the analyst returns

The `competitor-analyst` fact sheet has these parts:

- an identity table
- an inventory with the command that counted each group
- candidate mechanisms with `path:line` or URL evidence
- ideas mapped onto your inventory
- an explicit list of what it did not read

### Comparing competitors

`compare-competitors` reads the per-competitor reports and re-measures your side with commands
instead of trusting your README. It writes an at-a-glance table, an inventory by capability with
`—` where a repo has nothing, and each repo's strengths and weaknesses. It writes no ranked adoption
list unless you ask for one. The comparison gets an HTML page too, linked to each competitor's page.

### How far to trust a report

Each report states its snapshot date. Each one also says how every count was measured and whether
each claim was read in the source or only claimed by the competitor. Nothing is marked verified,
because the target is never run.

## Not this plugin

- Running, installing, or benchmarking a competitor: not done anywhere. It is untrusted code, so
  the reports stay read-only and say so.
- Market sizing, pricing strategy, positioning decisions: `ceh-product-direction:sharpen-strategy`
  owns strategy against named competitors.
- An adoption roadmap or ranked backlog: each report's incorporate table feeds your own planning.
  Ask for it explicitly.

## Where its files live

All output goes to `.agents_workspace/competitor-analysis/`:

- `<competitor>.yaml`, the source of each report, with `<competitor>.md` rendered beside it and
  `<competitor>.html`. Every partial or gap component must appear in "What we take".
- `comparison.md`, the source of the comparison, and `comparison.html`.
- The shared theme stylesheet under `themes/` (Meridian by default).

The HTML pages carry the same content as their source, with detail folded into expandable cards.
Do not edit a competitor page by hand: it is generated from the YAML. Older reports saved as
`<competitor>.md` are still read by the comparison.
