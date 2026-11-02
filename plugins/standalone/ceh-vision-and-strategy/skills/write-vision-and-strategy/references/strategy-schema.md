# Strategy schema

The `STRATEGY.md` that `write-vision-and-strategy` writes: how the repo gets to its vision, and how
the next piece of work is chosen. It goes in `product/STRATEGY.md`, committed, because later sessions
and other stages read it, and users of the product do not. An existing file at `STRATEGY.md`,
`docs/STRATEGY.md`, or a path the repo's `CLAUDE.md` names stays there. A new file is a copy of
`../assets/strategy.template.md`, relative to this file. The `schema: strategy/v1` line stays as
written. Where this file and `VISION.md` disagree, the vision wins until it is changed on purpose.

## Frontmatter

- `status`: `draft` while any `[assumed]` remains or the owner has not confirmed the file, `adopted`
  once they have. Only an adopted file binds later sessions.
- `updated`: the date of the last change.

## Sections

- **The concept:** the one idea that joins the parts, and what it was chosen over.
- **The parts:** one row per major part of the repo: its job, what it takes, what it passes on. In a
  repo of documents the parts are its collections. Change the columns when takes and passes do not
  fit, and keep one row per part.
- **How work is chosen:** a rule that accepts or refuses a candidate, with its reason, then the
  likely order next, each with why it comes first.
- **Measuring progress:** what is counted and how, so someone can tell the strategy is working or
  not. Say so when nothing has been measured yet.
- **What not to do:** approaches considered and rejected, each with its reason, so nobody proposes
  them again.
- **Where the repo does not match yet:** each difference between this file and the repo, or "No
  known gaps as of YYYY-MM-DD." A line leaves in the change that closes it.
- **Open questions:** each with the assumption used until it is answered.
- **Changing this file:** how a change lands, and that a change the vision does not allow changes
  the vision first.

## Marks

`[assumed]` follows a statement of intent no source backs. It is the owner's to confirm or correct,
and it never appears in an adopted file.
