# PRD schema

The product requirements: the features a product has or will have, each with its requirements
and acceptance criteria, what the product refuses, and what a later version replaced. It goes in
`.agents_workspace/product/PRD.yaml` in the target repo, with its Markdown rendered beside it,
unless the repo's `CLAUDE.md` names another location, because later sessions and the Build stage
read it, and users of the product do not. A reference to it names the `.yaml`. There is one per
repo, revised in place. `ceh-product-direction:write-product-requirements` writes it.
`ceh-build-plan:write-build-plan` and `ceh-build-plan:implement-from-plan` write only a feature's
`status` and `plans`, and `updated`. `ceh-build-plan:write-technical-design` and
`ceh-every-session:whats-next` read it. This file is copied
word for word into every skill that reads a PRD.

## prd/v1: YAML with generated Markdown

A `prd/v1` file is `PRD.yaml` beside the `PRD.md` it renders, a copy of
`../assets/prd.template.yaml`, relative to this file. The Markdown is generated and saved beside
it: nobody edits it, and it opens with `generated_from: PRD.yaml` and a do-not-edit
`generated_note`. The renderer writes the section numbers, the Contents list, the feature table
and every anchor, so the YAML holds none of them. The format in code is `prd-model.py` beside this
file, and `scripts/artifact.py` in the skill checks and renders it through uv:

```bash
uv run --script scripts/artifact.py check .agents_workspace/product/PRD.yaml   # errors, or a stale .md
uv run --script scripts/artifact.py render .agents_workspace/product/PRD.yaml  # check, then write the .md
```

Exit `0` is valid, `1` lists each error as `<path>: <field path>: <error>`, `2` is any other
failure, and `3` means no model for that version. Field paths count from 0, so `features.0` is the
first feature. A rule across keys is reported at the top level, and its message names the feature
id.

**Keys**, each required unless marked optional, and no other key allowed:

- `schema`: `prd/v1`.
- `status`: `draft` while any `[assumed]` remains or the owner has not confirmed the file,
  `adopted` once they have. `updated`: the date of the last change, unquoted.
- `features`: at least one, in build order: a feature comes after every feature it depends on.
  Each has:
  - `id`: `F` and two or more digits, such as `F01`. Unique, and never reused or renumbered, so
    a plan or a commit that names it stays right.
  - `name`: one line, with no em dash. `user`: one line, who the feature is for.
  - `requirements`: at least one, each a behaviour a user or caller can observe, never an
    implementation.
  - `acceptance`: at least one, each a statement a command or a named manual check can pass or
    fail.
  - `depends_on`: the ids of features listed before it, `[]` when none.
  - `status`: `todo` (no plan yet), `planned` (a plan exists) or `built`.
  - `plans`: the repo-relative path of each build plan that delivers it, each ending `.yaml`,
    `[]` when none. A path uses forward slashes on every OS, with no leading slash, drive
    letter, backslash, or empty, `.` or `..` segment, so one plan has one spelling.
- `non_functional`: requirements that hold across features, such as speed, security or
  platforms, `[]` when none.
- `non_goals`: `item` and `reason` per feature deliberately not built, `[]` when none. An item
  renders in bold with a full stop after it, so write it without one. `id` (optional) is the id
  of a feature that was dropped: it stays here so no later feature takes it.
- `replaced` (optional): the features a later version replaced, oldest first. It is history,
  never a requirement: `features` alone says what the product is now. With nothing replaced,
  leave the key out. It renders as `## 04. Replaced features`, and a file without it renders no
  such section. Each entry has:
  - `id` and `name`: the id and the name the feature had in `features`.
  - `date`: the day it was replaced, unquoted.
  - `replaced_by`: at least one id, each a feature, the `id` of a `non_goals` entry (a
    successor that was dropped later), or a `replaced` entry listed later (a successor that
    was replaced in turn).
  - `reason`: what the feature did, in a sentence, and why that no longer holds. Its old
    requirements are not kept here: the plans hold what was built, and `git log` the old text.
  - `plans`: the plans that built it, as a feature's `plans`, `[]` when none.

**Rules across keys:** an id appears once, across the features, the `non_goals` that carry
one, and `replaced`. A `depends_on` id names a feature listed earlier, which rules out a feature
depending on itself and any cycle, so a feature that depended on a replaced one names its
successor or drops the dependency. A `replaced_by` id names a feature, a `non_goals` id or a
later `replaced` entry, which rules out an entry replaced by itself and any cycle. `depends_on`,
`replaced_by` and `plans` each list an entry once. A `todo` feature has no plans, and a
`planned` one has at least one. A `built` feature may have none, because a product that existed
before its PRD has features no plan built. `status: adopted` with `[assumed]` anywhere in the file
is an error.

## Marks

`[assumed]` follows a statement no source backs. It is the owner's to confirm or correct, and it
never appears in an adopted file.

Free text goes in `|` blocks or quotes, because ` #` starts a YAML comment and a `: ` in a plain
value breaks it. Every value is strict, so quote a value that must stay text.
