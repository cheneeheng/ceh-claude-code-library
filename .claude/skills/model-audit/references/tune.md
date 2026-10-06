Tune the pinned file `{file}` for the model `{target}`. Its frontmatter pins `model: {frontmatter_model}`,
and it was last tuned for: {tuned_for}.

Fetch the general best-practices page, then these model guides in order. Each guide is written as
the differences from its predecessor, so together they describe what changed since the last tuning:

{guide_urls}

Read the file. Propose edits that fit it to `{target}`: remove instructions a guide says cause
problems on that model, and rewrite or add instructions where a guide recommends a different
approach. Keep the agent's role, tools, inputs, and output contract unchanged. Tie every edit to a
guide statement.

{apply_instruction}

Reply with only this Markdown, no preamble:

### Proposed edits

One `#### <line or section>` heading per edit, then: the guide quote with its URL, and the edit as
a before/after pair. Write "None." if the file already fits the model.
