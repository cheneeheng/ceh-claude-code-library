---
name: review-against-plan
description: >-
  Load this skill when auditing or verifying that the codebase matches a SKELETON.md or ITER_NN.md
  planning document, including version-tagged variants like SKELETON_v2.md or v2_ITER_03.md. For
  each in-scope section, checks the actual implementation against the spec, identifies gaps,
  deviations, and errors, then fixes them and reports a compliance table. Trigger on "review
  against plan", "verify the plan is implemented", "audit the code against the plan", "does the
  build match the skeleton", or when the user points at a plan file and asks to audit it. Not for
  building the plan in the first place (use implement-from-plan), writing the plan (use
  plan-fullstack-app-iteratively or plan-fullstack-app-to-mvp), or reviewing a pull request (use
  ceh-git-workflow:code-review).
argument-hint: "[plan-file]"
disable-model-invocation: false
user-invocable: true
license: Apache-2.0
---

# Review Against Plan

Audit the codebase against a SKELETON.md or ITER_NN.md: find gaps, deviations, and errors between
what the plan specifies and what is implemented, then fix them. Done means every in-scope section
is audited and the compliance report is delivered.

Read `${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md` before starting. It defines the planning
document schema, and its section table and pointer resolution rules are authoritative.

## Procedure

### 1. Locate and parse the plan docs

1. Find the target plan files. If the user did not specify, look for `SKELETON` and `ITER_NN`
   files (`.md`) under `.agents_workspace/planning/` (where the planning skills write them) or any
   subfolder within it. Filenames may carry a version tag as a prefix or suffix, e.g.
   `SKELETON_v2.md`, `v2_ITER_03.md`. See "File Naming and Version Variants" in
   `${CLAUDE_PLUGIN_ROOT}/references/plan-schema.md` for the matching rules.
2. Group the discovered files by version tag into plan families (untagged files are the default
   family). If more than one family exists, confirm with the user which version to review. The
   iteration with `mvp: true` is that version's terminator. Read each target artifact's
   `depends_on` and resolve inherited (`sections_unchanged`) sections through that chain for
   context. Audit only each artifact's own `sections_changed`. Treat inherited sections as context,
   not audit scope.
3. Read the frontmatter to determine scope:
   - ITER: audit only `sections_changed`. Resolve pointers for `sections_unchanged` to use as
     context, but do not audit them: a prior review cycle covered them.
   - SKELETON: audit all sections listed in `sections`.
4. If multiple ITER files exist within the target family and the user did not specify, confirm
   which one to review.

### 2. Audit section by section

Work through in-scope sections in numerical order. For each section, check, categorize, then fix.

**Check.** Compare the section spec against the actual codebase. Specifically verify:

| Section          | What to check                                                                                                                                                                                                                                               |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| §02 Architecture | All specified components exist. Data model entities and key fields are present. All listed routes exist with correct method and path. No undocumented routes or entities. Diagram is Mermaid (not ASCII art) and reflects the current/changed architecture. |
| §04 Backend      | All specified modules and files exist. Each route/service is implemented (not just stubbed unless spec says so). Env var names match. `how to run` works.                                                                                                   |
| §05 Frontend     | All specified pages/routes exist. Component tree matches. Placeholder data strategy followed. `how to run` works.                                                                                                                                           |
| §06 LLM/Prompts  | Model and provider match. System prompt implemented. Input/output shape matches.                                                                                                                                                                            |

**Categorize.** Assign each finding a category:

- **Gap**: something the spec requires that is completely missing.
- **Deviation**: something that exists but differs from the spec (wrong method, wrong field name,
  wrong route path, wrong model, etc.).
- **Error**: something that is broken independent of the spec (import error, missing env var
  causing a crash, etc.).

**Fix.** Fix each finding immediately after categorizing it. Do not batch auditing before fixing.

### 3. Report

After all sections, produce the summary table under Output.

## Rules

- Audit scope is each artifact's own `sections_changed` (ITER) or `sections` (SKELETON), nothing
  else.
- Do not mark anything as fixed unless the fix was applied.

## Output

```markdown
## Plan Compliance Report

| Section          | Findings                                                        | Status |
| ---------------- | --------------------------------------------------------------- | ------ |
| §02 Architecture | 2 gaps fixed (missing /users route, missing User.email field)   | Fixed  |
| §03 Tech Stack   | Clean                                                           | OK     |
| §04 Backend      | 1 deviation fixed (POST /items returned 200, spec requires 201) | Fixed  |
| §05 Frontend     | 1 gap fixed (missing /profile page)                             | Fixed  |
```

Below the table, list the items NOT fixed and why.

## Stop conditions

- A fix requires a decision (e.g. a route deviation where both the spec and the implementation
  could be correct) → state the ambiguity and ask before changing anything.
- More than one plan family, or several ITER files in the target family, and the user named none →
  ask which one to review.
