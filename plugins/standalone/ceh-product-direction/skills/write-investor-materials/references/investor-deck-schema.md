# Investor deck schema

The deck outline `write-investor-materials` saves to
`.agents_workspace/product/business/INVESTOR_DECK.yaml`, with its `.md` rendered beside it, local
and not committed. A reference to it names the `.yaml`. Its layout is
`../assets/investor-deck.template.md`, relative to this file. A new deck is written as
`investor-deck/v2` YAML, per the section at the end. A deck saved as `investor-deck/v1`, an
`INVESTOR_DECK.md` with no YAML beside it, is still edited in place when the skill next updates
it, its `schema:` line included.

## Frontmatter

- `plan`: the path to the business plan the deck is built from.
- `pmf_gate`: the plan's `pmf_gate` when the deck was written.
- `plan_updated`: the plan's `updated` date when the deck was written, so a later reader can tell
  the deck is stale.

## Body

- **Title:** the company name and its one-liner.
- **Slides:** one numbered `## <n>. <headline claim>` per slide, in the order the skill sets.
  Under it, one bullet per proof line, each ending in the plan's confidence tag: `[evidence]`,
  `[assumption]`, or `[hypothesis-to-test]`. The slide ends with `Source: §<NN>`, the plan
  section every line traces to.
- A deck written on an unvalidated plan carries `Draft: gate <N>/8` as its first body line.

## investor-deck/v2: YAML with generated Markdown

An `investor-deck/v2` deck is `INVESTOR_DECK.yaml`, a copy of
`../assets/investor-deck.template.yaml`, and `INVESTOR_DECK.md` is generated from it in the layout
above, beside it. The YAML is the source: agents read and edit it, and nobody edits the Markdown,
which opens with `generated_from: INVESTOR_DECK.yaml` and a do-not-edit `generated_note`. The
format in code is `investor-deck-model.py` beside this file, and `scripts/artifact.py` in the
skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check <dir>/INVESTOR_DECK.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render <dir>/INVESTOR_DECK.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `slides.0` is
slide 1.

**Keys**, each required, and no other key allowed, every value one line:

- `schema`: `investor-deck/v2`. `plan`: as in `v1`. `pmf_gate`: an integer from 0 to 8, rendered
  as `N/8`. `plan_updated`: an unquoted date.
- `draft`: `true` when the deck is written on an unvalidated plan, which renders the
  `Draft: gate <N>/8` line. A `pmf_gate` below 8 needs `true`.
- `company` and `one_liner`: the title's two parts.
- `slides`: at least one, each with `headline`, `lines` (at least one, each a `text` and a `tag`:
  `evidence`, `assumption` or `hypothesis-to-test`) and `source`, the plan section number as an
  integer, rendered `§NN`. The renderer numbers the slides from 1, so no number is stored.

**Quote a value that holds `: ` or ` #`, or starts with a quote**, because YAML reads ` #` as a
comment.
