# Approval schema

`{run}/approval-<stage-id>.md`, written by the runner when a stage reaches `awaiting-approval`, per
`flow-config-schema.md` beside this file. A new file is a copy of `../assets/approval.template.md`,
relative to this file. The `schema: approval/v1` line stays as written. This file is copied word for
word into `ceh-workflow-builder` and `ceh-workflow-runner`.

## Frontmatter

- `flow`: the flow's name.
- `run`: the run id.
- `stage`: the id of the stage awaiting approval, matching the file name.

## Body

- **Show:** what the stage's `show` asks for, exactly as the run would have asked about it.
- **Closing line:** stays as the template words it, with the stage id filled in.
