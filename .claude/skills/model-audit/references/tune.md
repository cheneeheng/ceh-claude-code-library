Tune the pinned file `{file}` for the model `{target}`. Its frontmatter pins `model: {frontmatter_model}`,
and it was last tuned for: {tuned_for}.

Fetch the general best-practices page, then these model guides in order. Each guide is written as
the differences from its predecessor, so together they describe what changed since the last tuning
(or, if never tuned, the current generation of the model):

{guide_urls}

Read the file. Adapt it to both: the general page applies to every model, and the model guides
refine it for `{target}`. Where they disagree, the newest model guide wins. Remove instructions a
page says cause problems, and rewrite or add instructions where a page recommends a different
approach. Model-specific wording is fine here, since only `{target}` runs this file. Keep the
agent's role, tools, inputs, and output contract unchanged. Tie every edit to a page statement.

{apply_instruction}

Reply with only this Markdown, no preamble:

### Proposed edits

One `#### <line or section>` heading per edit, then: the guide quote with its URL, and the edit as
a before/after pair. Write "None." if the file already fits the model.
