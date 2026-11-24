# ceh-codebase-explanation design notes

## Origin

Split out of `ceh-coding-conduct`, which keeps the rules for how an agent behaves while it codes.

## How explain-until-understood builds an explanation

How an explanation is built and what to do when it misses: assume the reader is new to the project and knows nothing about the subject, and say what floor you are building from; read the real code (never a design doc), foundations before the specific case, plain language (concept before name, every term of art defined at first use, project-local names included), verified output over described output, plain-ASCII pictures for structure and time (no box-drawing or arrow glyphs), a numbered walk of one ordinary case end to end, close on a transferable rule plus a self-test. Ships the escalation ladder — prose → steps → pictures → foundations — with the rule that a miss at pictures means a skipped foundation, not a missing detail; a reader lost on a _word_ is not on the ladder at all. Writes no files by default — `.agents_workspace/` scratch notes on request, an opt-in learning workspace (`.agents_workspace/product/learning/<subject>.yaml`, rendered to its `.md`: terms the reader has said back, rules, self-test history, what comes next) that a later session opens with two self-test questions, and one narrow repo path for a subsystem explainer no other skill owns.

## Architecture render and generated Markdown guard

`document-architecture` saves `.agents_workspace/product/ARCHITECTURE.yaml` (`architecture/v3`).
After every write to it, the render hook checks the YAML against its model through `uv` and renders
the `ARCHITECTURE.md` beside it with its section numbers and Contents list, or reports each error back
to the agent and leaves the Markdown as it was. `maintain-glossary` saves `GLOSSARY.yaml`
(`glossary/v2`), and the same hook checks it and renders `GLOSSARY.md`. `explain-until-understood`
keeps its learning record at `.agents_workspace/product/learning/<subject>.yaml` (`learning/v2`),
which the hook checks and renders too.

## History

Since 2026-11-14 this plugin saves and reads product files in `.agents_workspace/product/`.
