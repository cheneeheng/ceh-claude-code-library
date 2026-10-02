# skills-sync

Copy Claude Code skills from a GitHub repo or a local folder into a project's
`.claude/skills/` directory — install, update, add, remove, and list skills,
tracked by a small manifest.

This is standalone meta-tooling, separate from the `ceh-*` plugin marketplace
in this repo. It works
against any source repo or folder containing skills (directories with a
`SKILL.md`), detected recursively — no particular layout (e.g. a plugin
marketplace structure) is assumed.

## Implementations

Four behaviorally-equivalent implementations — pick whichever fits your
environment:

| File               | Requires                                                                                     |
| ------------------ | -------------------------------------------------------------------------------------------- |
| `skills-sync.py`   | Python 3.8+ (standard library only)                                                          |
| `skills-sync.sh`   | bash, curl, tar, jq                                                                          |
| `skills-sync.ps1`  | PowerShell 7+ (`pwsh`)                                                                       |
| `skills-sync.html` | A Chromium-based browser (File System Access API) — open the file directly, no server needed |

All four produce byte-compatible `.claude/skills/.manifest.json` manifests
(same keys, key order, 2-space indent, trailing newline, LF line endings), so
you can switch between them on the same project.

`skills-sync.html` loads its styles and logic from sibling `skills-sync.css`
and `js/*.js` files via classic (non-module) `<script>`/`<link>` tags, so it
keeps working when opened directly via `file://`. Keep the whole
`tools/skills-sync/` directory together when copying or distributing the
HTML implementation — `skills-sync.html` alone is not enough.

## Commands

- `install` — fresh install of selected skills from a GitHub repo or local folder; writes the manifest
- `update` — re-copy skills already tracked by the manifest from its recorded source (or a `--skills` selection)
- `add` — install additional skills, unioned with what's already tracked
- `remove` — delete a skill's folder and untrack it
- `list` — print the source and tracked skills

`install` replaces the current selection. `update` with no `--skills` re-syncs
the intersection of the manifest and what's currently available from the
source; `update`/`add` with `--skills` union the new selection into the
manifest. `remove` is the only command that deletes a skill's folder and
untracks it. Re-syncing a skill wipes and replaces its folder under
`.claude/skills/<name>/`.

## Examples (Python)

```bash
# Install all skills from a GitHub repo into ./my-project/.claude/skills/
./skills-sync.py install --repo owner/name --target ./my-project

# Install only specific skills
./skills-sync.py install --repo owner/name --skills foo,bar --target ./my-project

# Install from a local folder instead of GitHub
./skills-sync.py install --path ../other-repo --target ./my-project

# Re-sync everything tracked by the manifest from its recorded source
./skills-sync.py update --target ./my-project

# Add another skill to an already-installed project
./skills-sync.py add --skills baz --target ./my-project

# Remove a skill
./skills-sync.py remove --skills baz --target ./my-project

# List what's installed
./skills-sync.py list --target ./my-project
```

The bash and PowerShell scripts accept the same subcommands and flags
(`--repo`/`-Repo`, `--path`/`-Path`, `--ref`/`-Ref`, `--skills`/`-Skills`,
`--target`/`-Target`, `--token`/`-Token`). The HTML page provides the same
operations through a form: pick a project folder, pick a source (GitHub repo
or local folder), check the skills you want, and sync.

Use `--token`/`-Token` (or the token field in the HTML page) for private
GitHub repos.

## What gets written

- `.claude/skills/<name>/` — a full copy of each synced skill's directory
- `.claude/skills/.manifest.json` — tracks the source (`github`: `repo` +
  `ref`, or `local`: `path`), the last-updated timestamp, and the list of
  tracked skill names
- `.claude/.gitignore` — ignores `skills/.manifest.json` and `skills/<name>/`
  for each tracked skill, so synced skills aren't committed to your project
  while any custom skills you keep alongside them in `.claude/skills/` stay
  trackable

If `.claude/.gitignore` already has the older blanket `skills/` line (from a
previous version of this tool), it's migrated away on the next
`install`/`update`/`add` and replaced by the per-manifest/per-skill lines
above. `remove` deletes only that skill's `skills/<name>/` line, leaving
everything else untouched.

## Notes

- Skills are detected recursively by searching for `SKILL.md` files; the
  directory containing `SKILL.md` becomes the skill, named after its own
  directory basename.
- A `.manifest.json` only records skill names, not paths — if a skill moves
  within the source between syncs, `update` still finds it as long as the
  directory basename is unchanged.
