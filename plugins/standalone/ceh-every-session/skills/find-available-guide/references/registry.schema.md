# Registry schema

What each column of `registry.txt` means. The file has no header and no comment lines, because
`validate.py` reads every non-blank line as an entry and the skill's Grep would match a header.

One line per entry and install method, eight cells split on `|`:

```text
name | aliases | kind | beats | method | install | source | checked
```

| #   | Column    | Holds                                                                                            | Rule                                                               |
| --- | --------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| 1   | `name`    | The framework, library, or service as its project spells it                                      | Searched by the skill's Grep                                       |
| 2   | `aliases` | Other words the work may use for it, comma-separated                                             | Searched by the skill's Grep                                       |
| 3   | `kind`    | What the entry is                                                                                | `skill`, `plugin`, or `mcp`                                        |
| 4   | `beats`   | What the agent does without the entry, which is also why the entry is listed                     | Plain phrase, shown to the user in the note                        |
| 5   | `method`  | How the entry installs                                                                           | `plugin` (marketplace), `mcp-add` (`claude mcp add`), `skill-copy` |
| 6   | `install` | The exact command, copied from the source on the `checked` date. Several commands joined by `&&` | Shown as written, never run by the skill                           |
| 7   | `source`  | Where the command was read                                                                       | Starts with `https://`                                             |
| 8   | `checked` | The date the command was read at its source                                                      | Real `YYYY-MM-DD`, not in the future                               |

- An entry with several ways to install has several lines, the preferred method first.
- A `name` and `install` pair is unique, ignoring case.
- No cell is empty and no cell contains `|`.
- Entries are our own pointers. Never paste third-party text into a cell, because the skill's
  output carries the weight of a user instruction.
- `kind` and `method` differ on purpose: a skill or an MCP server can reach the user by more than
  one method, and only `plugin` goes through a marketplace.

`python tools/validate-plugins/validate.py` enforces the cell count, `kind`, `method`, `source`,
`checked`, and the unique pair. It does not check that `install` is still current.
