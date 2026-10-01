# Git-backed datastore

A database-free persistence layer for an application, using a bare git
repository as the datastore. One repo per deployed instance, one orphan branch
per project, JSON records in trees.

This is the companion narrative to the two skills in this plugin — the reasoning
and the API, in the order a person reads it rather than the order an agent needs
it. It deliberately does not repeat what the skills carry:

| For                                                                  | Read                                                  |
| -------------------------------------------------------------------- | ----------------------------------------------------- |
| The full fit gate, the design rules, measured numbers, anti-patterns | `skills/build-git-datastore/SKILL.md`                 |
| Exact git command sequences                                          | `skills/build-git-datastore/references/plumbing.md`   |
| Records, ids, collections, schema versioning, sharding               | `skills/build-git-datastore/references/data-model.md` |
| gc, backup, restore, monitoring, security                            | `skills/build-git-datastore/references/operations.md` |
| The store contract and porting it to another language                | `skills/build-git-datastore/references/porting.md`    |
| Leaving the store for Postgres or SQLite                             | `skills/migrate-git-datastore/SKILL.md`               |

Both skills are stdlib Python plus the `git` binary. No packages to install.

---

## Contents

- [Before you start](#before-you-start)
- [Quick start](#quick-start)
- [Deployment and multi-node](#deployment-and-multi-node)
- [FAQ](#faq)

---

## Before you start

`build-git-datastore` opens with a seven-row gate covering write rate, record
count, record size, hosting, query shape, cross-project reads, and deletion.
Run it there. Two of those rows are hard stops rather than trade-offs, and they
are the two people talk themselves past:

**Serverless or multi-node hosting.** The store is a directory on a disk. Two
app nodes with two disks are two different databases. Serverless runtimes have
no durable disk at all, so every write would have to reach a remote, putting
network latency and API rate limits in the request path. See
[Deployment and multi-node](#deployment-and-multi-node) for what to do instead.

**Right to erasure.** Git history is append-only by construction. "Delete this
user's data" means rewriting every commit that touched it and force-updating the
ref, which invalidates every clone and backup. If the app handles personal data
under GDPR/CCPA-style erasure obligations, keep that data out of the git store
entirely — store an opaque id and hold the personal data somewhere you can
actually `DELETE` from.

Deciding _against_ the pattern is a good outcome, and much cheaper than
migrating in three months.

---

## Quick start

```bash
python gitstore.py init ./data.git
```

```python
from gitstore import GitStore

store = GitStore("./data.git").init()
store.create_project("acme", {"name": "Acme Corp"})

rec = store.put("acme", "tasks", None, {"title": "Ship it", "status": "open"})
store.get("acme", "tasks", rec["id"])
store.list_records("acme", "tasks")
```

### The two write paths

Picking the wrong one causes silent data loss, so this is the one API detail
worth internalising.

**`transaction()` — blind writes.** "Set these paths to these values." Several
records land in one commit or none do. On a lost race the operations are
replayed on top of the winner's tree, which is correct because the values did
not depend on what was already there.

```python
with store.transaction("acme", "transfer") as tx:
    tx.put("accounts", "A", {"balance": 90})
    tx.put("accounts", "B", {"balance": 110})
```

**`atomic()` — read-modify-write.** Whenever the new value is computed from the
old one: counters, appending to a list field, state machines. The function
re-runs from scratch against fresh state if another writer commits first, so it
must be pure and free of side effects.

```python
def bump(tx):
    c = tx.get("counters", "hits")
    c["n"] += 1
    tx.put("counters", "hits", c)


store.atomic("acme", bump)
```

Using `transaction()` where `atomic()` was needed silently discards the other
writer's update. In testing, six processes doing ten increments each produced 58
instead of 60 before this distinction existed.

---

## Deployment and multi-node

### What works

| Setup                             | Verdict                                                                                                                                     |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| One server, N worker processes    | **Fine.** CAS is atomic across processes.                                                                                                   |
| One server, N threads             | **Fine.** Same mechanism.                                                                                                                   |
| Two servers, separate disks       | **Broken.** Two stores that both believe they are authoritative.                                                                            |
| Two containers, shared NFS volume | **Broken, silently.** `update-ref` needs `O_EXCL` + rename semantics NFS does not reliably provide, so both can believe they hold the lock. |
| Kubernetes `replicas: 2`          | **Broken.** Same as two servers.                                                                                                            |
| Autoscaling group                 | **Broken**, and it will work fine right up until it scales.                                                                                 |

Two subtler cases: blue-green deploys briefly run both versions, and a rolling
restart overlaps old and new pods. Even a single-replica deployment needs
`strategy: Recreate` rather than `RollingUpdate`.

### Why "pull first, then push" does not fix it

The naive version fails immediately — another node can push between your pull
and your push, so you are back to a rejection with extra steps. Retrying
converges, but the real problems are elsewhere:

- **You already acknowledged the write.** The local commit succeeded and the
  request returned 200 before the push was attempted. When the push is rejected,
  recovering means rebasing onto the other node's commit — survivable for a
  blind write, a lost update for read-modify-write, because the new value was
  computed from a tree that no longer exists.
- **`git pull` means merge, and git's merge is line-based text.** Two nodes
  editing different fields of the same record produce either a plausible-looking
  wrong result or literal `<<<<<<<` conflict markers inside your data files.
  There is no semantic merge for records.

A version that _is_ correct exists: do not commit locally first — build the
commit object, push it with `--force-with-lease=<ref>:<old-sha>`, and only
update the local ref and return 200 if the remote accepts. That is a
compare-and-swap over the network.

It is also useless. Every write becomes a network round trip, and the git server
becomes the single serialisation point — so writes have not scaled at all, the
bottleneck has just moved somewhere slower, behind a service that rate-limits
you. Reads remain stale unless you fetch before each one. The result is a
distributed database with worse latency and worse consistency than the one you
were avoiding, plus a text-based merge function.

### What to do instead

Multi-node is usually three separate requirements wearing one label, and only
one of them touches the store.

**If it is traffic or CPU — put the store behind a small internal service.**

```
    [app node 1] ─┐
    [app node 2] ─┼──HTTP──> [storage service] ──> data.git on a volume
    [app node N] ─┘             (replicas: 1)
```

The app tier scales horizontally, autoscales, and deploys with rolling updates,
because it is stateless. Exactly one process ever opens `data.git`, so every
guarantee holds unchanged.

Expose the store contract — `get`, `list`, `put`, `transaction`, `atomic` — over
HTTP. It is a couple of hundred lines. The payoff is that when the service does
become the bottleneck, you swap its internals for Postgres and no app node
changes, because they were already talking to the interface.

Cost: a network hop per data access (~1 ms in-cluster), and one component that
must stay up.

**If it is high availability — active/passive with a lease.**

One writer, one standby that restores from the remote and serves nothing until
promoted. Promotion requires a fencing token (a lease in Redis, etcd, or a cloud
lock) so the old node cannot keep writing after being declared dead. Without
fencing, split brain gives you two divergent stores and a manual merge.

RPO equals the time since the last push, so tune the sync worker to whatever
data loss is acceptable. If the answer is "zero", you need synchronous
replication, which git does not do — that is the migration trigger.

**If it is genuinely concurrent write throughput across nodes — migrate.**

Do not build sharded refs or network CAS. Run
`gitexport.py inventory` and start the migration skill.

### Recommendation

Ship single-node: one container, one persistent volume, `replicas: 1`,
`strategy: Recreate`. A CRUD app on one modern node goes further than people
expect, and single-node is precisely why this design is simple enough to be
worth having. Introduce the storage service the first time a second app node is
genuinely needed.

---

## FAQ

**Is `data.git` just `.git` renamed?**

Effectively yes, with one difference. A bare repo is the contents of a `.git`
directory standing alone — same `HEAD`, `config`, `objects/`, `refs/` — but with
no `index` (there is no staging area without a working tree) and `core.bare` set
to true.

The `.git` name is a default, not a rule. Its only special property is
_auto-discovery_: `git status` walks up the directory tree looking for a folder
named `.git`. Since every command here passes `--git-dir` explicitly, discovery
never happens and the name is pure convention. You can point git at a directory
called anything at all. The `.git` suffix on bare repos is a signal to humans.

**"Stdlib only" — how, for git operations?**

It means no third-party _packages_ — no GitPython, no pygit2. The store shells
out to the `git` binary through `subprocess`. So the real dependency list is
Python 3.10+ and `git` on `PATH`.

That is a deliberate trade. Shelling out means every command is exactly what is
documented, so you can paste it into a terminal to debug, and there is no
binding-version skew. It also means process spawn is the performance floor —
~1.8 ms per point read is mostly fork/exec. `pygit2` would take reads into
microseconds at the cost of a compiled dependency and a codebase you cannot
debug by hand. The middle path is a long-lived `cat-file --batch` process.

**What is `refs/remotes/backup/*` for?**

Remote-tracking refs — git's local cache of where it last saw the remote's
branches. Git creates and maintains them itself based on the fetch refspec that
`git remote add` writes into your config. They are what make `origin/main` exist
and what lets git report "ahead by 2 commits" offline. Useful in a normal
workflow, useless here, and actively harmful — see "Do not use
`git push --mirror`" in `skills/build-git-datastore/references/operations.md`.

**Does "multi-node" mean multiple servers?**

Yes — separate machines or containers with separate filesystems. Multiple
processes or threads on _one_ machine are fine; that is exactly what the
compare-and-swap handles.

**Can I use a shared network volume so both nodes see one store?**

No, and the failure is silent. `update-ref` gets its atomicity from `O_EXCL`
lockfile creation plus rename, and NFS does not reliably provide those semantics
across clients, so two nodes can both believe they hold the lock.

**Can I shard projects across nodes so no two nodes write the same ref?**

That is technically correct — the refs are independent. It is also a hand-rolled
sharding layer with a routing table, a failover story, and a rebalancing
procedure. Postgres is strictly less work than maintaining it.

**Why one orphan branch per project rather than directories on one branch?**

Write contention. One branch means every write in the app serialises on a single
ref. Per-project refs mean writes to different projects never contend.

**Do orphan branches waste storage?**

No. Git objects are content-addressed and shared across the whole object
database regardless of commit ancestry. "Orphan" severs commit history, not
deduplication.

**How do I delete data for real?**

You do not, easily — history is append-only. Prefer soft deletion, since a hard
delete leaves the record in history anyway. If a record must genuinely be gone,
history rewriting is the only option: `git filter-repo`, force-update the ref,
expire reflogs, `gc --prune=now`, and replace every backup and mirror. If that
is a recurring requirement rather than a rare incident, the pattern is the wrong
fit.
