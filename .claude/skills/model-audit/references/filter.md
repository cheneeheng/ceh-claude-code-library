Review the plugin at `{plugin_dir}`, starting from the `/doctor prompt-audit` report at
`{raw_report}`.

The plugin's unpinned skills and agents run on every in-use model, so a change must fit all of
them. Fetch every page below before judging anything.

General best practices, which apply to every model:

- {general_page}

New model guides to act on. Each is written as the differences from its predecessor:

{guide_urls}

Other in-use model guides, which a change must not hurt:

{other_guide_urls}

Read the report and the files it cites, then the plugin's other skill and agent files. Add any
change the pages call for that the report missed. Keep a change when one of these holds:

1. The general page backs it. Removals, rewrites, and additions all count, but add a technique
   only where the file's task shows the need that section describes: a parallel-calls rule
   belongs in an agent that makes independent tool calls, not in every file.
2. A model guide says it benefits that model, and no other guide above says it hurts its model.
   If a guide is silent on the instruction, treat that model as unaffected.
3. It fixes a model-independent defect: a reference to a missing file or command, or two
   instructions that contradict each other.
4. It cuts prose that changes no behavior, model-independent too: a sentence whose deletion
   changes nothing the model does ("be thorough", "use good judgment"), a negative instruction
   rewritten as the positive one it implies where both say the same, or a missing statement of
   when the task is done, added to the file's opening.

Where a page above and the `/doctor` report disagree on the same instruction, follow the report.
Its patterns are written for current models, while the general page's sample prompts can use
phrasing the report removes, such as CAPS or "you MUST".

Leave out everything else, including any change that helps one model but a guide says hurts
another, and any change written for one model only, such as "on Sonnet, do X". Quote the statement that
backs every kept change, with its URL. Ignore these pinned files, which are tuned separately:
{pinned_files}

{apply_instruction}

Reply with only this Markdown, no preamble:

## Kept changes

One `### <file>:<line>` heading per change, then: the rule it keeps under (1 to 4), the
backing quote with its URL, for rule 2 the models it benefits and why the others are unaffected,
and the change as a before/after pair. Write "None." if nothing survived.
