# Cutover

Moving live traffic from the git store to the database without downtime or lost
writes. This assumes application code already goes through a store interface —
if git commands are scattered through route handlers, fix that first, on its own,
with no behaviour change. Doing both at once means a rewrite and a data
migration failing simultaneously, with no way to tell which is at fault.

## Shape of the plan

```
backfill  →  dual-write  →  verify  →  read from DB (per project)  →  DB only
             ↑ git authoritative      ↑ DB authoritative
```

Reads flip per project. Writes flip once, globally, at the end. Between those
two points both stores are live and either can serve.

## 1. Backfill from the pins

```bash
python scripts/gitexport.py export data.git ./export
```

`export/manifest.json` records the commit each project was read at. Everything
downstream depends on it, so treat it as an artefact: commit it, or store it
next to the dump.

Load the JSONL with the bulk path for your engine (see `postgres.md` /
`sqlite.md`). No time pressure — the source cannot move.

## 2. Verify the backfill before dual-writing

Dump what the database actually returns and compare:

```bash
python scripts/verify.py export/tasks.jsonl db_tasks.jsonl \
  --unnest extra --coerce points:int
```

Non-zero exit means stop. Two things this catches that a count check does not:
a row whose content was mangled by a bad cast, and a row that arrived twice.
Matching row counts are not verification — a test store with one corrupted row
and one dropped row had identical counts on both sides.

## 3. Dual-write

Both backends on every write, git authoritative:

```
write(record):
    git_store.put(...)            # authoritative; failure fails the request
    try:
        db_store.put(...)         # shadow; failure logs, does not fail
    except Exception as e:
        metrics.increment("dualwrite.db_failure")
        log.warning(...)
```

Deliberate asymmetry: a database problem must not take down an app that is still
running on git. Invert this only after reads have moved.

Two things to watch:

- **Divergence rate.** Every shadow-write failure is a schema or data mismatch
  you have not found. It should trend to zero within hours. If it plateaus, stop
  and fix the cause rather than waiting it out.
- **Delete parity.** Deletes must be dual-written too. This is the most common
  omission, and it is invisible until someone notices a record they deleted is
  back after cutover.

Run dual-write long enough to cover the natural cycle of the app — if there is a
weekly batch job or a monthly close, it has to run at least once under
dual-write, because those paths write differently to everything else.

## 4. Catch up on the migration window

Records changed between the pin and now:

```bash
python scripts/gitexport.py changed data.git export/manifest.json
```

```
M   proj1  tasks  01J8ZQ3K4M5N6P7Q8R9S0T1U2V
D   proj1  tasks  01J8ZQ3K4M5N6P7Q8R9S0T1U2W
A   proj2  tasks  01J9AB3K4M5N6P7Q8R9S0T1U2V
proj5: NEW project since export -- full load required
D   bench59  *  * (project deleted since export)
```

Handle all five statuses. `D` is the one people skip, and skipping it means
deleted records come back. `A` on a project that did not exist at export time
means a full load for that project, not a per-record replay.

Replay these, then re-run `verify.py`. Repeat until `changed` returns nothing
new that dual-write is not already covering.

## 5. Flip reads, one project at a time

This is the payoff of orphan branches: each project is an independent ref, so
each can cut over independently.

```
read(project, ...):
    if project in DB_READ_PROJECTS:
        return db_store...
    return git_store...
```

Order: one internal or low-traffic project first, then the smallest real ones,
then the largest. Migrate the largest project _last_ for reads but investigate it
_first_ during profiling — it is where the schema surprises are.

Before each batch, and again after: run `verify.py` for those projects. After
each batch, watch error rate and latency for a full traffic cycle before
continuing. Resist doing all of them at once because the first few went well;
the point of the staged flip is that a problem affects a few tenants, not all.

**Rollback is removing a project from the read set.** Nothing to undo, no data to
restore — git is still authoritative and still being written. That property is
what makes it safe to move quickly, and it disappears at step 6, so do not rush
through it.

## 6. Flip writes

Only once every project reads from the database and has been stable for a
meaningful period.

Invert the asymmetry: the database becomes authoritative, git becomes the shadow.
Keep writing to git for a further period — a week is reasonable — because that is
the last point at which rollback is free.

Then stop writing to git.

## 7. Archive

```bash
git --git-dir data.git gc --quiet
git --git-dir data.git bundle create /backups/data-final-$(date +%F).bundle --all
sha256sum /backups/data-final-*.bundle
```

Store it somewhere durable with the manifest. Do not delete the repo for at least
a full backup-retention cycle.

Then remove the git store implementation from the codebase. Leaving it behind
means the next person cannot tell which backend is live, and dead branches in a
data layer are how a stale write path gets accidentally re-enabled.

## Gates

Do not advance a phase until:

| Phase                        | Gate                                                     |
| ---------------------------- | -------------------------------------------------------- |
| Backfill → dual-write        | `verify.py` exits 0 for every collection                 |
| Dual-write → read flip       | Divergence rate at zero for 24h; delete parity confirmed |
| Read flip batch → next batch | Error rate and latency stable for a full traffic cycle   |
| Read flip → write flip       | Every project reading from DB, stable for a week         |
| Write flip → archive         | DB authoritative for a week with backups verified        |

## If it goes wrong

- **Verification fails after backfill.** Truncate and reload. Nothing is live yet;
  this is the cheap failure and the reason verification comes before dual-write.
- **Divergence during dual-write.** Git is authoritative and correct. Fix the DB
  path, re-run the affected replay, re-verify. No user impact.
- **A project misbehaves after read flip.** Remove it from the read set. Instant,
  no data movement.
- **A problem appears after the write flip.** This is the expensive one. Git is
  stale by however long ago you stopped writing to it, so you cannot simply flip
  back — you would lose everything written since. Recovery means exporting the DB
  back into git shape and reconciling. This is precisely why the write flip
  happens last and only after a week of stability.
