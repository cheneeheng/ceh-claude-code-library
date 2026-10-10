# ceh-git-datastore

Running an app on a bare git repository instead of a database — while that still fits, and how to
leave when it stops.

One repo per deployed instance, one orphan branch per project, JSON records in trees, every access
through plumbing commands. You get atomic multi-record writes, lock-free concurrency that is correct
across processes, immutable point-in-time snapshots, history and undo for free, and `git push` as
the backup story. You give up ad-hoc queries, multi-node hosting, and the ability to actually delete
anything.

The pattern is narrow, so most of this plugin's value is the honest gate in front of it. Talking
someone out of it is a normal, good outcome.

## Skills

| Skill                 | Invoke as                                  | When to use                                                                                                                        |
| --------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| Build Git Datastore   | `/ceh-git-datastore:build-git-datastore`   | An app needs persistence but not a database yet — prototype, MVP, internal tool, or per-tenant isolation with nothing to provision |
| Migrate Git Datastore | `/ceh-git-datastore:migrate-git-datastore` | A git-backed or file-based JSON store has to become Postgres or SQLite, without downtime or lost writes                            |

### `build-git-datastore`

**Auto-triggers on:** "databaseless", "no-DB", "just use files", "JSON file storage", "git as a
database", "store the data in git", "an orphan branch per project", "how do we defer the database
decision" — and on any description of wanting persistence without a database, even when git is never
mentioned.

Opens with a seven-row fit gate (write rate, record count, record size, hosting, query shape,
cross-project reads, deletion), two rows of which are hard stops: serverless or multi-node hosting,
and a right-to-erasure obligation. If the gate fails on one row, the skill names the row and the
alternative rather than building anyway.

Past the gate it is five rules that make the design work — bare repo and never a working tree,
compare-and-swap on the ref as the concurrency control, reads inside a write pinned to the commit
you will CAS against, one git process per operation rather than per record, and sortable ids — plus
a working store implementation, a background remote-sync worker, and measured numbers to argue with.

Ships `scripts/gitstore.py` and `scripts/sync.py`: stdlib Python, no packages, `git` on `PATH` as
the one dependency.

### `migrate-git-datastore`

**Auto-triggers on:** "we have outgrown the file store", "move off files to Postgres", "migrate the
git datastore", "we need a real database now", "derive a schema from these JSON records", "verify
the backfill was correct", plus the symptoms — climbing CAS retries, a second app node, cross-project
reporting becoming a requirement.

Starts by deciding whether it is time at all; "keep the git store another quarter" is a normal
verdict. Then target choice (SQLite is the right answer more often than people expect for a
single-node app), schema inference from the records that actually exist, pinned-snapshot export,
backfill, verification, dual-write, and per-project cutover — because each project is an independent
ref, so cutover is incremental rather than all-at-once.

The section worth reading before planning anything is "What actually breaks": type drift, absent vs
explicitly null, deletes during the migration window, timestamp formats, tenancy that lived in the
ref name, and duplicate ids across projects. Each was observed on a realistic test store, not
hypothesised.

Ships `scripts/gitexport.py` (`inventory`, `infer`, `export`, `changed`) and `scripts/verify.py`,
which exits non-zero so it can gate a deploy.

## Long-form narrative

[`docs/git-datastore.md`](docs/git-datastore.md) is the companion doc for a person rather than an
agent: the quick start and the `transaction()`-vs-`atomic()` distinction that causes silent data loss
when confused, the full multi-node analysis (why "pull first, then push" is either broken or useless,
and what to do instead), and an FAQ. It deliberately does not repeat what the skills carry.

## Relation to other plugins

| Question                                                                              | Owner                                            |
| ------------------------------------------------------------------------------------- | ------------------------------------------------ |
| Should this app use a database at all, yet                                            | `build-git-datastore`                            |
| Is it time to leave, and how                                                          | `migrate-git-datastore`                          |
| PostgreSQL schema, query, transaction, pool, and migration code once you have arrived | `ceh-python-service:write-postgresql-code`       |
| Recording the choice as a durable decision                                            | `ceh-codebase-explanation:document-architecture` |

Neither skill declares a dependency on those: `migrate-git-datastore` targets SQLite as often as
Postgres, so the handoff is a branch most runs never reach.

## Not for

- **Your source repository.** `data.git` holds application data and must never be touched by
  commit, branch, or PR tooling — those need a working tree, which the design forbids. Keep it
  outside the source tree.
- **Binaries.** Every version of every blob is kept forever. Object storage; store the key.
- **Anything needing real erasure.** Git history is append-only by construction.

## Installation

```
/plugin install ceh-git-datastore@ceh-claude-code-library --scope user
```

Or from a local clone: add it as the marketplace with
`/plugin marketplace add ~/ceh-claude-code-library`, then run the same install command. To try the
plugin for one session without installing it, start Claude Code with
`claude --plugin-dir ~/ceh-claude-code-library/plugins/standalone/ceh-git-datastore`.
