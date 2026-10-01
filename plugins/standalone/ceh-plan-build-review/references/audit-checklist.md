# Pre-delivery audit checklist

Run this before delivering any plan artifact (SKELETON.md or ITER_NN.md). The goal is to catch
decisions that will block a developer mid-build.

For each gap: if it is your call, resolve it and add the resolution inline. If it needs user input,
collect all such items and present them together before finalising.

**Scope**

- [ ] Does the plan cover only the current release? Remove anything that belongs to a future
      iteration.
- [ ] Are deferred decisions explicitly marked as deferred (not left ambiguous)?
- [ ] Does every section pointer reference the correct artifact (by stem, including version tag)
      and section?
- [ ] (ITER) Does `depends_on` name every artifact the pointers rely on, and does it point only
      backward, never to a later iteration or version?
- [ ] (Version family) Does every file carry the right `_vN` tag, does the `NN` counter restart
      within the family, and, if the family has an MVP terminator, does exactly one iteration carry
      `mvp: true`?

**Architecture (§02)**

- [ ] Is the component diagram in Mermaid, not ASCII art? (ITER) Does it visualize what changed
      this iteration, not just the current state?
- [ ] Is the data model complete enough to start building? (Entity names, key fields,
      relationships: not full schema, but no mystery fields)
- [ ] Is the API surface defined with methods, paths, and expected response shapes?
- [ ] Are cross-origin concerns addressed? (Which origins are allowed, cookie policy)
- [ ] Is auth handled or explicitly deferred? (Not silently assumed)

**Tech Stack (§03)**

- [ ] Is every dependency in the plan actually needed for this iteration?
- [ ] Are there conflicting dependencies? (e.g. two state management libraries)
- [ ] Is the local dev setup runnable from the plan alone? (Runtime versions, how to start)

**Backend (§04)**

- [ ] Does every planned endpoint have a defined request and response shape?
- [ ] Is ownership/access control addressed for every resource endpoint?
- [ ] Are list endpoints paginated, or is pagination explicitly deferred?
- [ ] Are environment variables named (not necessarily valued)?
- [ ] Is the database migration strategy clear for this iteration?

**Frontend (§05)**

- [ ] Does every screen in the plan have a defined route?
- [ ] Are loading and error states mentioned, or explicitly deferred?
- [ ] Is the API client setup addressed? (Base URL, auth header/cookie strategy)
- [ ] Are there empty states for any list views?

**LLM (§06, if applicable)**

- [ ] Is the model and provider specified?
- [ ] Is the context window strategy defined, or explicitly deferred?
- [ ] Are role constraints for the target API addressed in the message-building logic?

**Completeness scan (run last).** Scan the artifact for:

- Placeholder code (`pass`, `TODO`, `...`, `// implement this`)
- Prose like "adjust as needed" without specifying what
- References to files, endpoints, or types that are not defined anywhere in the plan
- Fields named in one section but missing from the corresponding schema in another
