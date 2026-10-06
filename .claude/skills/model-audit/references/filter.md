Filter the `/doctor prompt-audit` report at `{raw_report}` for the plugin at `{plugin_dir}`.

The plugin's unpinned skills and agents follow Anthropic's general prompting techniques and must
work on every model, so they never get model-specific additions. A finding survives only when it
proposes removing or softening an instruction that one of these model guides says causes problems,
for example forced self-verification, "keep progress updates brief", heavy anti-markdown blocks,
or CRITICAL/MUST phrasing:

{guide_urls}

Fetch each guide, then read the report and the files it cites. For every finding:

- Keep it if a guide statement supports the removal. Quote that statement and link its guide.
- Drop it otherwise, including anything that adds model-specific wording.
- Drop findings on these pinned files, which are tuned separately: {pinned_files}

{apply_instruction}

Reply with only this Markdown, no preamble:

## Kept findings

One `### <file>:<line>` heading per finding, then: the instruction, the guide quote with its URL,
and the proposed edit as a before/after pair. Write "None." if nothing survived.

## Dropped findings

One bullet per dropped finding: `<file>:<line>`, what it proposed, and why it was dropped.
