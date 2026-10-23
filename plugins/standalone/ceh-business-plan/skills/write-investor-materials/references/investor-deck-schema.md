# Investor deck schema

The deck outline `write-investor-materials` saves to
`.agents_workspace/product/business/INVESTOR_DECK.md`, local and not committed. A new deck is a copy of `../assets/investor-deck.template.md`, relative
to this file. The `schema: investor-deck/v1` line stays as written.

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
