# Plan Document Schema

Planning documents come in two artifact types: **SKELETON** and **ITER_NN**.

## File Naming and Version Variants

The base filenames are `SKELETON.md` and `ITER_NN.md`. A planning set may carry an optional
**version tag** — e.g. `v2`, `v3` — when more than one version of the app is planned in the same
location. The tag attaches as a prefix or suffix, bound by a `_`, `-`, or `.` separator:

- `SKELETON_v2.md`, `v2_SKELETON.md`, `SKELETON-v2.md`
- `ITER_03_v2.md`, `v2_ITER_03.md`, `ITER_03-v3.md`

The canonical emit form is a `_vN` suffix (`SKELETON_v2.md`, `ITER_03_v2.md`), though a `v2_`
prefix is also read.

Match plan files as the base name `SKELETON` or `ITER_NN` (`NN` = two digits) with an optional
separator-bound tag on either side, plus the `.md` extension. Untagged files (`SKELETON.md`,
`ITER_NN.md`) belong to the **default (untagged) family**.

Files that share a version tag form one **plan family**. The `NN` iteration counter restarts
within each family — `ITER_01_v2.md` is the first iteration of the `v2` family, independent of
`ITER_01.md`.

### Cross-version dependencies

Versions are linked, not isolated. A later version builds on an earlier one through the standard
`depends_on` frontmatter field (see Frontmatter) — a `v2` file lists the `v1` artifacts it builds
on and inherits every section it does not re-specify. Because `depends_on` names artifacts by
**stem** (filename without `.md`, which carries the version tag), one mechanism covers both
same-sequence iteration chaining (`[SKELETON, ITER_01]`) and cross-version inheritance
(`[SKELETON_v1, ITER_03_v1]`). A version's SKELETON is optional — a version may be ITER files
alone that depend on the previous version's SKELETON.

## Frontmatter

Every plan file opens with a YAML frontmatter block.

**SKELETON.md:**

```yaml
---
artifact: SKELETON
status: ready
created: YYYY-MM-DD
app: <one-line app name>
stack: <comma-separated key technologies>
sections: [01, 02, 03, 04, 05] # sections present in this file
---
```

**ITER_NN.md:**

```yaml
---
artifact: ITER_01 # NN increments per iteration; stem = filename without .md
status: ready
created: YYYY-MM-DD
scope: <what this iteration adds or changes>
sections_changed: [02, 05] # sections with substantive content in this file
sections_unchanged: [01, 03, 04] # sections using pointers (resolve via depends_on)
depends_on: [SKELETON] # artifacts this iteration builds on; e.g. [SKELETON, ITER_01]
---
```

The **terminator** — the final iteration that reaches the MVP — carries two extra frontmatter
fields that no other artifact has (`mvp: true` and `mvp_target`), plus a `## Out of MVP scope`
body block listing the features and concerns consciously deferred from this MVP:

```yaml
---
artifact: ITER_04
status: ready
created: YYYY-MM-DD
scope: <one-line description of what this iteration adds or changes>
sections_changed: [02, 04]
sections_unchanged: [01, 03, 05]
depends_on: [SKELETON, ITER_01, ITER_02, ITER_03]
mvp: true # present and true ONLY here — marks the MVP terminator
mvp_target: <one-line description of the MVP this family reaches>
---
```

Every non-terminal iteration **omits** the `mvp` key entirely (absence means false), so
non-terminal iterations are schema-identical whichever planner wrote them and a family can be
planned partly with each. The skeleton carries no MVP fields: the MVP boundary is recorded on the
terminator iteration only.

**Terminator body — Out of MVP scope.** The terminator must include a short `## Out of MVP scope`
block listing the deferred features and concerns, one short bulleted phrase per line. This is the
plan's visible hard edge: it lives on the terminator so the full boundary (`mvp: true`,
`mvp_target`, and the deferred list) sits on one artifact and the skeleton stays untouched. Treat
the block as scope boundary, not as work to implement.

A **patch** is a small, non-feature change made to a version _after_ it was implemented (bug fix,
copy/config tweak, validation change, small post-MVP polish). It rides as an ordinary `ITER_NN.md`
that continues the family counter and carries `patch: true` in its frontmatter. A patch ITER is the
**only** artifact allowed past the terminator — it depends on the terminator (or a prior patch) and
never carries `mvp`. Because it stays within the existing architecture, its `sections_changed`
touches implementation sections (§04/§05), not §02; a change that touches §02 (data model or API
surface) is a feature iteration, not a patch. Patches are produced only by `patch-built-version`;
the planning skills never emit `patch: true`.

**Field rules:**

- `artifact` — filename without extension (the stem; carries the version tag for versioned files).
- `status` — always `ready` on delivery.
- `created` — ISO date.
- `app` (SKELETON only) — short human-readable name.
- `stack` (SKELETON only) — key technologies (e.g. `Python, FastAPI, React, PostgreSQL`).
- `sections` (SKELETON only) — the section numbers present in this file.
- `scope` (ITER only) — what this iteration covers.
- `sections_changed` (ITER only) — sections with content in this file.
- `sections_unchanged` (ITER only) — sections that use pointers.
- `depends_on` (ITER only) — prior artifacts this iteration relies on, named by stem. Within a
  family it is the same-sequence chain (e.g. `[SKELETON_v2, ITER_01_v2]`); the first iteration of
  an iterations-only new version points back into the prior family's terminal artifacts — its
  skeleton plus its `mvp: true` iteration (e.g. `[SKELETON, ITER_03]`) — whereas a version with
  its own `SKELETON_vN` depends on that instead. Points only backward — never to a later
  iteration or version. Resolution traces this field, and so does the planners' cross-iteration
  audit, to catch forward references.
- Skeletons carry no `depends_on` — a skeleton is fresh scaffolding, and a versioned skeleton is
  assumed to build on the prior family.
- `mvp` (terminator ITER only) — present and `true` exactly once per family, on the final
  iteration. It marks where the plan stops; nothing is _planned_ past it except patches. All
  other iterations omit the key.
- `mvp_target` (terminator ITER only) — one line stating the MVP this family reaches. Lives
  alongside `mvp: true` so the boundary travels with the artifact that closes it.
- `patch` (patch ITER only) — present and `true` on an iteration that patches an already-built
  version. Continues the family `NN` counter, `depends_on` the terminator or a prior patch, never
  carries `mvp`, and may follow the terminator. `sections_changed` stays within implementation
  sections (§04/§05); a §02 change means it is a feature iteration, not a patch. All non-patch
  iterations omit the key.

> **The MVP terminator may be absent.** Not every plan declares one — iteratively-planned
> families often have no terminator yet. When no iteration carries `mvp: true`, do not infer one
> — treat the highest-numbered ITER reachable through the `depends_on` chain as the end of the
> sequence, and otherwise rely on `depends_on` order alone.

## Sections

The planners read `section-specs.md` for the full expected content of each section. This table
condenses it.

| ID  | Title        | Skeleton content                                                                                           | Iteration content                                                                             |
| --- | ------------ | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| §01 | Concept      | What the app does, who it's for, the single most important user flow                                       | What changed; pointer if unchanged                                                            |
| §02 | Architecture | Mermaid component diagram, data model (entity names + key fields), API surface (method + path + one-liner) | Changed entities/routes only + updated Mermaid diagram showing the change; pointer otherwise  |
| §03 | Tech Stack   | Language/runtime versions, one framework per layer, database, key libraries                                | New deps + rationale, version pins if relevant; pointer otherwise                             |
| §04 | Backend      | File/module tree (2–3 levels), one representative stub per route group, `how to run`, env var names        | New modules/files, implementation detail for new endpoints; apply `implementation-gotchas.md` |
| §05 | Frontend     | Page/screen list with routes, top-level component tree, `how to run`, placeholder data strategy            | New screens/components, state changes, new API calls; apply `implementation-gotchas.md`       |
| §06 | LLM/Prompts  | _Skip if no LLM integration._ Model + provider, stub system prompt, input/output shape                     | Revised prompts, context strategy changes, eval approach                                      |

## Pointers

When a section appears in `sections_unchanged`, the ITER file contains a pointer (e.g. "See SKELETON §02"). Do not treat this as content — look up the referenced document and section to get the actual spec.

## Resolution Order

Resolution follows the `depends_on` chain backward — never a forward reference.

To find the authoritative spec for a given section:

1. If a pointer names a specific artifact, honor it directly.
2. Walk the `depends_on` chain backward from the target. The authoritative spec lives in the
   nearest artifact (closest to the target) whose `sections_changed` (ITER) or `sections`
   (SKELETON) lists that section number.
3. For a version variant the chain crosses into the base version's artifacts. It never moves
   forward to a later iteration or version; the trace ends at a SKELETON.
