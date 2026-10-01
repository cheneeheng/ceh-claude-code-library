# Operations

Set this up before launch. The store is fine to run in production within its
limits, but only if garbage collection, backup, and a rehearsed restore exist.

## Deployment topology

The store is a directory on a disk, which fixes the architecture:

- **One app node** with a persistent volume. Multiple app processes on that node
  are fine — `update-ref` is atomic across processes, which is exactly why the
  compare-and-swap matters.
- **Not multiple nodes.** Two nodes with two disks are two divergent databases,
  and there is no replication story that makes them one. A shared network
  filesystem does not fix it either: `update-ref` relies on atomic
  `rename()`/`O_EXCL` semantics that NFS does not reliably provide, so
  concurrent writers can both think they won.
- **Not serverless.** No durable disk means pushing to a remote on every write,
  which puts network latency and rate limits in the request path.

If horizontal scaling is on the roadmap, that is the migration trigger, and
`ceh-git-datastore:migrate-git-datastore` is the next step.

## Garbage collection

Every write creates loose objects. Without repacking, the store bloats roughly
20x — a measured 7.5 MB became 0.4 MB after `git gc`.

```bash
git --git-dir data.git config gc.auto 256
git --git-dir data.git config gc.autoDetach true
```

That is enough for most stores: git repacks opportunistically in the background.
Add a scheduled full gc during a quiet window as a backstop:

```bash
git --git-dir /srv/data.git gc --quiet
```

`gc` takes a lock; concurrent writes are safe (they retry) but a large gc can
stall writers briefly. Schedule it off-peak, and be aware the pause grows with
history depth.

### Reflog expiry is a retention decision

Reflogs keep objects alive after their ref moves — that is what makes rollback
possible, and it also means "deleted" data is still on disk. Set the window
deliberately rather than inheriting the default:

```bash
git --git-dir data.git config gc.reflogExpire "90 days"
git --git-dir data.git config gc.reflogExpireUnreachable "30 days"
```

Longer window: better undo, more disk, longer tail of deleted data. Match it to
whatever the data-retention policy actually says.

## Backup

Backup is a push. Restore is a clone. Both are boring, which is the point.
`scripts/sync.py` does it properly; the commands below are what it runs.

```bash
python sync.py setup /srv/data.git git@host:org/app-data.git --name backup
python sync.py push  /srv/data.git
```

### Do not use `git push --mirror`

It is the obvious command and it is wrong here. `--mirror` pushes every ref
under `refs/`, and after a successful push git creates remote-tracking refs at
`refs/remotes/backup/*`. The next mirror push then ships those to the remote as
a second, stale copy of your entire dataset:

```
refs/heads/project/p0
refs/remotes/backup/project/p2      <- a project you deleted, still on the remote
```

Those tracking refs also keep deleted projects reachable **locally**, so `git gc`
can never reclaim a deleted project's objects. Use an explicit refspec instead:

```bash
git --git-dir /srv/data.git push --prune backup 'refs/heads/*:refs/heads/*'
```

That pushes exactly the project branches and prunes remote branches that no
longer exist locally — the behaviour `--mirror` was wanted for, without the rest.
Also drop the remote's fetch refspec so the tracking refs never appear:

```bash
git --git-dir /srv/data.git config --unset-all remote.backup.fetch
```

### Push out of the request path

A push inside a write handler couples write latency to network conditions and
turns every network blip into a user-visible error. Run it in the background:

```python
from sync import Syncer

syncer = Syncer(
    "/srv/data.git",
    remote="backup",
    debounce=5.0,  # coalesce a burst into one push
    min_interval=60.0,  # never push more often than this
    on_error=log.warning,
).start()

store.put("acme", "tasks", None, {...})
syncer.notify()  # non-blocking; safe on every request

syncer.stop(final_push=True)  # on shutdown -- see below
```

`stop(final_push=True)` matters more than it looks. Writes since the last push
exist only on the local disk, so a process that exits without a final push loses
however much was pending. That window is the one data-loss path this design has;
keep `debounce` small enough that you can live with losing it.

For an app that cannot host a thread, run `python sync.py daemon /srv/data.git`
as a sidecar, or just schedule `sync.py push` on a timer.

### Keep a second backup that is not a mirror

A pruning push propagates a local mass-deletion to the remote. `sync.py` guards
against the accidental version — it refuses a push that would delete more than
25% of remote refs and makes you pass `--force-prune` — but a guard is not a
substitute for a backup that cannot be overwritten. Take nightly bundles:

```bash
python sync.py bundle /srv/data.git /backups --keep 14
```

A bundle is a single file containing every ref and all history. `sync.py` runs
`git bundle verify` on each one before rotating, because a bundle nobody verified
is a backup nobody took.

### Monitor the sync, not just the disk

```python
syncer.status()
# {"consecutive_failures": 0, "last_error": null,
#  "seconds_since_success": 42.1, "ref_count": 64, "pending": false}
```

Alert on `seconds_since_success` exceeding a few multiples of `min_interval`.
Silent backup failure is the failure mode that only reveals itself on the day
you need the backup.

## Restore

Rehearse this before you need it, and time it:

```bash
git clone --mirror git@host:org/app-data.git /srv/data-restored.git
# or
git clone --mirror /backups/data-2026-03-01.bundle /srv/data-restored.git

git --git-dir /srv/data-restored.git fsck --no-progress
git --git-dir /srv/data-restored.git for-each-ref --format='%(refname)' refs/heads/project/ | wc -l
```

Point the app at the restored path. A restore that has never been tested is a
backup that has never been tested.

### Rolling back one project

The most common recovery is not a full restore — it is one project after a bad
write:

```bash
git --git-dir data.git reflog show refs/heads/project/p1
git --git-dir data.git update-ref refs/heads/project/p1 <good_sha> <current_sha>
```

Passing the current sha makes it a compare-and-swap, so the rollback fails
rather than clobbering if someone wrote while you were deciding. Worth wiring
into an admin endpoint: it turns "restore from backup" into a click.

## Monitoring

Watch four things:

| Signal                   | How                          | Why it matters                                                     |
| ------------------------ | ---------------------------- | ------------------------------------------------------------------ |
| Repo size                | `git count-objects -vH`      | Bloat means gc is not running                                      |
| Loose object count       | same                         | High count means repacking is behind                               |
| CAS retries per write    | app counter                  | Rising retries = write contention, the leading migration indicator |
| Commit depth per project | `git rev-list --count <ref>` | Very deep histories slow gc and clone                              |

The CAS retry counter is the one to alert on. It degrades gracefully right up
until it does not, and it is the earliest honest signal that write volume has
outgrown the pattern.

Also alert on free disk. The failure mode when a volume fills is partial writes
and a store that will not accept commits.

## Concurrency limits in the app

Two guards worth adding:

- **Serialise writes per project inside the process** (a per-ref lock or queue).
  Retries are correct but wasteful; a local queue converts a retry storm into an
  orderly line and cuts wasted work under bursts.
- **Cap retries and surface the failure.** Silent unbounded retrying turns
  contention into unbounded latency. Return a `409`, let the caller decide.

## Health check

```bash
git --git-dir data.git rev-parse --verify HEAD >/dev/null 2>&1 || echo "store unreadable"
git --git-dir data.git fsck --no-progress --connectivity-only
```

The connectivity-only fsck is fast enough for a periodic check; the full fsck is
a nightly job.

## Security

- The repo is plain files. File permissions are the access control — the app
  user should own it and nothing else should read it.
- Never expose the repo over HTTP or the git protocol. It is internal storage,
  not a remote.
- Validate every project id and record id against a strict charset before it
  reaches a path or a ref. Reject, do not escape.
- Encrypt at rest at the volume level. There is no per-record encryption here,
  and adding one destroys diffability and dedup.
- Remember that history retains everything. A secret committed by mistake stays
  in the repo, in every mirror, and in every bundle until history is rewritten
  and all copies replaced. Treat it like any other git repo in that respect.
