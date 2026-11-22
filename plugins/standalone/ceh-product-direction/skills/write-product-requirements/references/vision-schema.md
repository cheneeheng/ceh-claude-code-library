# Vision schema

The vision that `write-vision-and-strategy` writes: why the repo exists and the principles that
settle a decision. It goes in `.agents_workspace/product/VISION.yaml`, with its Markdown rendered
beside it, because later sessions and other stages read it, and users of the product do not. A
reference to it names the `.yaml`. An existing file at `VISION.md`, `docs/VISION.md`, or a path the
repo's `CLAUDE.md` names stays there. The `v1` layout below is what the Markdown keeps. A `v1` file
is a copy of `../assets/vision.template.md`, relative to this file, and its `schema: vision/v1`
line stays as written.

## Frontmatter

- `status`: `draft` while any `[assumed]` remains or the owner has not confirmed the file, `adopted`
  once they have. Only an adopted file binds later sessions.
- `updated`: the date of the last change.

## Sections

- **Identity:** one sentence on what the repo is, then what it is and what it is not. Each "is not"
  is something a reader could reasonably have expected.
- **Vision:** the end state, a few sentences, written as what is true once it is reached.
- **Scope:** what belongs here, ending in one test question an agent can apply to a new idea, and
  naming one tempting thing the test refuses.
- **Goals:** numbered, each with how someone tells it is met or not.
- **Non-goals:** each something tempting, with why it is refused. Nobody needs to refuse what nobody
  wants.
- **Principles:** one `###` per principle: the rule, its reason, and a closing `**Ask:**` question
  for a review. The reason lets a reader apply the rule to a case the text does not cover.
- **When principles conflict:** an order over the principles, with one worked example.
- **Where the repo does not match yet:** each difference between this file and the repo, or "No
  known gaps as of YYYY-MM-DD." A line leaves in the change that closes it.
- **Changing this file:** how a change lands, such as its own pull request, and what must change
  with it.

## Marks

`[assumed]` follows a statement of intent no source backs. It is the owner's to confirm or correct,
and it never appears in an adopted file.

## vision/v2: YAML with generated Markdown

A `vision/v2` file is `VISION.yaml` beside the `VISION.md` it renders, a copy of
`../assets/vision.template.yaml`. The Markdown is generated in the `v1` layout above and saved
beside it: nobody edits it, and it opens with `generated_from: VISION.yaml` and a do-not-edit
`generated_note`. The format in code is `vision-model.py` beside this file, and
`scripts/artifact.py` in the skill checks and renders it through uv (`check <file>`, then
`render <file>`). Exit `0` is valid, `1` lists each error with its field path, `2` is any other
failure, and `3` means no model for that version.

**Keys**, each required, and no other key allowed: `schema` (`vision/v2`), `status`, `updated`
(an unquoted date), `identity` (`name`, `sentence`, which ends with its full stop and renders as
"<name> is <sentence>", `is` as `trait` and `meaning`, `is_not`), `vision`, `scope` (`text`,
`test`, `refuses`), `goals` (`goal`, `measure`), `non_goals` (`thing`, `reason`), `principles`
(`name`, `rule`, `ask`, numbered by position), `conflicts` (`order` as `principle` and `protects`,
each naming a principle in the list, and `example`), `gaps`, `extra_sections` (`title`, `body`)
and `changing`. A trait, goal or non-goal renders in bold with a full stop after it, so write it
without one. An empty `gaps` renders "No known gaps as of <updated>.", and an empty list is `[]`.
`status: adopted` with `[assumed]` anywhere in the file is an error.

`extra_sections` holds a section an existing file had that the template does not. It renders
before Changing this file, so its old position is not kept.

A `v1` `VISION.md`, or one with no `schema:` line, is moved on its next update: write `VISION.yaml`
from it, render, and check `git diff --no-index --word-diff` between a copy of the old Markdown and
the rendered one before the update itself. The
reply names the move and any line the diff shows changed.
