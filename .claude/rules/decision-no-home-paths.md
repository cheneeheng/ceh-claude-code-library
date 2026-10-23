# No home paths in committed files

Never commit a file that holds the user's home path or a path built from it: `C:\Users\<name>`,
`/Users/<name>`, `/home/<name>`, or the `C--Users-<name>-...` folder name Claude Code gives a
project under `~/.claude/projects/`. Write `<home>` and `<project>` instead, as in
`<home>/.claude/projects/<project>/<session>.jsonl`. This covers retros, fix records, and scripts
copied in from another repo or a transcript. The `hygiene` check in `validate.py` enforces it on
`product/`, `docs/`, `plugins/`, `tools/`, `.claude/`, `.github/`, `audits/`, `examples/`, and root
Markdown.

Why: the home path names the user and their machine layout, and a public repo publishes it to
anyone who clones it. Retros copied in from transcripts leaked it while `product/` sat outside the
check. Decided 2026-10-23. Source: conversation.
