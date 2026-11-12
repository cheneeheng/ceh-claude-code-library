# Saved file names

Every file or folder a skill saves with a date or time in its name is named
`<YYYYMMDD-HHMMSS>-<session-id>-<name>`: the time from one `date +%Y%m%d-%H%M%S` call, the whole
session id (`${CLAUDE_SESSION_ID}` in a skill body, the placeholder `<session-id>` everywhere
else), then what the file is. A folder with nothing else to say stops after the session id. A file
already saved under an older form keeps its name, and every reader and hook accepts both forms.
Two names are exempt: a blog draft, `<YYYY-MM-DD>-<slug>`, because the date is the post's, and the
model-audit folder, `audits/<date>/`, because its script also runs in CI, where there is no
session. A date inside a file (`saved`, `date`, a Record line) keeps its own format.

Why: one form sorts by time in any folder, a second run never overwrites the first, and the
session id traces a file to the transcript that wrote it.
