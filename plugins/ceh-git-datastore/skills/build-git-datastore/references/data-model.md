# Data model

How to shape the data so the store stays fast, stays readable, and survives the
eventual move to SQL without a rewrite.

## Records

One JSON document per file. Every record carries the same four fields, always:

```json
{
  "id": "01J8ZQ3K4M5N6P7Q8R9S0T1U2V",
  "created_at": "2026-03-01T10:00:00.000Z",
  "updated_at": "2026-03-01T10:00:00.000Z",
  "schema_version": 1,
  "title": "Ship the thing",
  "status": "open"
}
```

- `id` is duplicated inside the record even though it is already the filename.
  Exports, log lines, and API responses all carry the record alone, and a record
  that cannot identify itself is painful in every one of those places.
- `created_at` / `updated_at` in UTC, ISO-8601, milliseconds, `Z` suffix. Fix
  the format now; mixed timestamp formats are the most common thing that makes
  a later migration miserable.
- `schema_version` is an integer you bump when the shape changes. It costs one
  field and it is the difference between a confident migration and archaeology.

### Serialise deterministically

Write JSON with sorted keys and stable indentation. This is not cosmetic:

- An unchanged record hashes to the same blob, so rewriting identical data
  creates no new object.
- `git diff` between two commits shows what actually changed, in a form a human
  can read during an incident.

Note that if you stamp `updated_at` on every write, a "no change" write still
produces a new blob. That is usually the behaviour you want — an explicit write
is an event — but be aware of it, and guard against committing an unchanged tree
so history does not fill with empty commits.

## Ids

Use ULIDs: 26 characters, Crockford base32, 48-bit timestamp prefix, 80 random
bits. `scripts/gitstore.py` includes a stdlib implementation.

`git ls-tree` returns entries in byte order, so a time-prefixed id means
directory order _is_ creation order. "Most recent 20 records" becomes a slice of
a listing rather than a sort of the whole collection. UUIDv4 gives you random
order and throws that away for nothing.

They also survive migration unchanged. An auto-increment integer does not exist
in the git store, so choosing one at migration time means inventing a total
order after the fact and rewriting every foreign reference.

Do not use a user-supplied slug as the id unless it is genuinely immutable —
renaming means moving a file, which breaks every reference to the old path and
leaves the old version alive in history anyway.

## Collections

`collections/<name>/<id>.json`. Names should be lowercase, plural, stable, and
map cleanly onto future table names.

Git trees handle a few thousand entries per directory comfortably. Past roughly
10k in one directory, tree objects get large and every write rewrites the whole
tree object for that directory. Shard by id prefix at that point:

```
collections/events/01J8/01J8ZQ3K4M5N6P7Q8R9S0T1U2V.json
collections/events/01J9/01J9AB3K4M5N6P7Q8R9S0T1U2V.json
```

Because ULIDs are time-prefixed, a prefix shard is also a time bucket, which
makes "records from around this period" cheap and archiving old shards easy.
Decide sharding _before_ you have 10k records — resharding later means rewriting
every path.

## References between records

Store the foreign id as a plain string field, exactly as SQL would:

```json
{ "id": "01J...", "task_id": "01H...", "body": "looks good" }
```

There are no foreign keys and no cascade. Nothing stops a dangling reference, so
either check it on write, or sweep for orphans periodically, and accept that a
delete leaves references behind. Write down which of those you chose.

Do not nest child records inside parents to fake a join. Two writers editing two
different comments on one task would then contend on the same file, and you have
recreated the write contention that orphan branches exist to avoid.

## Cross-project data

Anything shared across projects — users, plans, global settings — does not belong
on a project branch. Put it on `refs/heads/main` under `shared/`. Keep it small
and low-churn: it is a single ref, so every write to it serialises globally.

If shared data is high-churn, that is a real signal the pattern is being
outgrown. Note it against the migration trigger.

## Schema evolution

Adding an optional field needs nothing. Everything else follows one of two
routes:

**Lazy migration** (default). Bump `schema_version`, and upgrade a record on
read when you see an old version. Cheap, no downtime, but old shapes linger
indefinitely and you carry the upgrade code until you sweep.

**Eager migration.** Walk every record and rewrite it in one transaction per
project. Because a transaction is one commit, each project either fully migrates
or does not — and if it goes wrong, `update-ref` back to the previous sha is an
instant rollback. Do this when a field becomes required, or before a migration
to SQL, where mixed shapes are the main source of pain.

Keep JSON Schema files in `schema/<collection>.json` and validate on write in
development. The `ceh-git-datastore:migrate-git-datastore` skill uses them to propose DDL, and
falls back to profiling actual records when they are absent — the profile is
always worth checking even when the schemas exist, since the schemas describe
intent and the records describe reality.

## Queries and derived indexes

The store supports exactly two access patterns: fetch by id, and list a
collection. Anything else is a scan in application memory.

At a few thousand records per project a scan is genuinely fine — reading 700
records takes ~220 ms in one batch, and filtering them in Python is microseconds.
Do not build an index before measuring.

When a scan does become the bottleneck, build a derived index rather than a
second source of truth:

```
collections/tasks/<id>.json          <- source of truth
indexes/tasks_by_status.json         <- derived, rebuildable
```

Three rules keep this from rotting:

1. Update the index **in the same transaction** as the record. One commit means
   they can never be out of step, which is the failure mode that makes hand-rolled
   indexes worse than no index.
2. Make it rebuildable from the records with a script, and actually run that
   script periodically to confirm it still matches.
3. Never read the index for anything correctness depends on. It is a cache.

If you find yourself building a third index, that is the pattern telling you it
wants to be a database. Take the hint.

## Deletion

Prefer soft deletion — a `deleted_at` field — because a hard delete leaves the
record in history anyway, so a hard delete buys you nothing except a confusing
gap. Filter deleted records at the store boundary so no caller has to remember.

If you need the record genuinely gone (an erasure request, a leaked secret),
history rewriting is the only option: `git filter-repo`, force-update the ref,
expire reflogs, `gc --prune=now`, and re-clone every backup and mirror. This is
disruptive and easy to get wrong. If it is a recurring requirement rather than a
rare incident, see the gate in SKILL.md — the pattern is the wrong fit.
