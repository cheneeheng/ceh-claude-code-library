# Investor outreach schema

The outreach notes `write-investor-materials` saves to `product/INVESTOR_OUTREACH.md`, beside the
deck. A new file is a copy of `../assets/investor-outreach.template.md`, relative to this file. The
`schema: investor-outreach/v1` line stays as written.

## Frontmatter

- `plan`: the path to the business plan the notes are built from.

## Body

- **Fit:** the investor profile this plan matches: stage, cheque size, sector, and the thesis.
- **Investors:** the names the user supplied, or `none supplied`. The skill never invents names.
- **Email:** at most 120 words. The subject is the one-liner. The body says what it is, the
  traction number, the ask, and the link.
- **Follow-up:** one line, sent two weeks later, with something new since the first email.
- Notes written on an unvalidated plan carry `Draft: gate <N>/8` as their first body line.
