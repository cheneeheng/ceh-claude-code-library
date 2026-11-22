# Strategy schema

The strategy that `write-vision-and-strategy` writes: how the repo gets to its vision, and how the
next piece of work is chosen. It goes in `.agents_workspace/product/STRATEGY.yaml`, with its
Markdown rendered beside it, because later sessions and other stages read it, and users of the
product do not. A reference to it names the `.yaml`. An existing file at `STRATEGY.md`,
`docs/STRATEGY.md`, or a path the repo's `CLAUDE.md` names stays there. The `v1` layout below is
what the Markdown keeps. A `v1` file is a copy of `../assets/strategy.template.md`, relative to
this file, and its `schema: strategy/v1` line stays as written. Where this file and the vision
disagree, the vision wins until it is changed on purpose.

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

## strategy/v2: YAML with generated Markdown

A `strategy/v2` file is `STRATEGY.yaml` beside the `STRATEGY.md` it renders, a copy of
`../assets/strategy.template.yaml`. The Markdown is generated in the `v1` layout above and
saved beside it: nobody edits it, and it opens with `generated_from: STRATEGY.yaml` and a
do-not-edit `generated_note`. The format in code is `strategy-model.py` beside this file, and
`scripts/artifact.py` in the skill checks and renders it through uv (`check <file>`, then
`render <file>`). Exit `0` is valid, `1` lists each error with its field path, `2` is any other
failure, and `3` means no model for that version.

**Keys**, each required, and no other key allowed: `schema` (`strategy/v2`), `status`, `updated`
(an unquoted date), `concept`, `parts` (`columns`, at least two, and `rows`, each as long as
`columns`, so a repo can change the columns and keep one row per part), `work` (`rule`, `reason`,
and `next` as `work` and `why`), `measuring`, `not_to_do` (`approach`, `reason`), `gaps`, `open`
(`question`, `assumption`), `extra_sections` (`title`, `body`) and `changing`. A rule, work item,
approach or question renders in bold, so write it with its own full stop where it needs one. An
empty `gaps` renders "No known gaps as of <updated>.", an empty `open` renders `None`, and an empty
list is `[]`. `status: adopted` with `[assumed]` anywhere in the file is an error.

`extra_sections` holds a section an existing file had that the template does not. It renders
before Changing this file, so its old position is not kept.

A `v1` `STRATEGY.md`, or one with no `schema:` line, is moved on its next update, as for the
vision: write the YAML from it, render, and check `git diff --no-index --word-diff` between a copy
of the old Markdown and the rendered one first.
