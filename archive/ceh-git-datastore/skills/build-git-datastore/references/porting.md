# The store contract, and keeping migration cheap

`scripts/gitstore.py` is the reference implementation. This file describes the
interface it implements, so the same store can be written in another language,
and so the git backend can later be swapped for a database without touching
application code.

## Why the interface matters more than the implementation

The git store is explicitly a stage, not a destination. Everything about how
painful the migration will be is decided now, by whether application code talks
to an interface or to git.

If a route handler runs a git command, migration means rewriting every route
handler, and the app is down while you do it. If every route handler calls
`store.list(project, "tasks")`, migration means writing a second implementation
of that interface and changing one line of wiring — and you can run both at once
to compare them. That is the difference between a week and a quarter.

So: **no git command outside the store module.** Not in a handler, not in a
template, not in a background job, not "just this once" in a script. Enforce it
with a lint rule or a grep in CI if the team is bigger than one person.

## The contract

```
create_project(pid, meta)              -> meta        create-if-absent
list_projects()                        -> [meta]
delete_project(pid)                    -> None

get(pid, collection, rid)              -> record      raises NotFound
list_ids(pid, collection)              -> [rid]       ordered by id
list_records(pid, collection)          -> [record]    ordered by id
put(pid, collection, rid|None, doc)    -> record      upsert; None generates an id
delete(pid, collection, rid)           -> None        idempotent

transaction(pid, message)              -> Tx          blind writes, one commit
atomic(pid, fn, message)               -> result      read-modify-write, retries
history(pid, limit)                    -> [entry]     OPTIONAL, git-only
```

Every method is scoped to a project. That is not incidental: it keeps the
interface implementable by a SQL backend where `project_id` is a column, and it
means no caller can accidentally write a cross-project query that the git
backend cannot serve.

### The two write paths, and why there are two

`transaction()` collects blind writes — "set these paths to these values" — and
commits them together. On a lost race the operations are replayed on top of the
winner's tree, which is correct because the values did not depend on what was
there before.

`atomic(fn)` re-runs your whole function against fresh state on a lost race.
Use it whenever the new value is computed from the old one: counters, appending
to a list field, state machines, anything read-then-write. Using `transaction()`
there silently loses the other writer's update.

`fn` must be pure and free of side effects, because it can run several times.
No emails, no external calls, no logging you would be confused to see twice.

### What `history()` is for

Debugging and admin tooling only. It is the one method with no SQL equivalent,
so anything the _product_ depends on must not come from it — if users can see
"who changed this", write an `events` collection instead. Treating commit history
as application data welds the app to git and does not survive migration.

## Rules that keep migration cheap

1. **Uniform records.** `id`, `created_at`, `updated_at`, `schema_version` on
   every record, always. The migration tooling keys off these.
2. **Timestamps in one format.** UTC, ISO-8601, milliseconds, `Z`. Mixed formats
   are the single biggest source of migration pain.
3. **One type per field, forever.** A field that is an int in old records and a
   string in new ones cannot become a typed column without a cleanup pass, and
   you will find out halfway through a backfill. Validate on write.
4. **Absent or null — pick one.** SQL collapses both to NULL, so any distinction
   you rely on is lost at migration. Decide now and normalise on write.
5. **Flat records.** Deep nesting maps to JSONB, which cannot be indexed usefully
   without extra work. Keep the fields you filter and sort by at the top level.
6. **No git in the domain layer.** Repeated because it is the one that matters.
7. **Write the migration trigger in the README.** The record count, write rate,
   or feature that means it is time. A trigger nobody wrote down is a trigger
   nobody notices.

## TypeScript sketch

The same design, ported. Node's `child_process` replaces `subprocess`; the
plumbing sequence is identical.

```ts
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

const run = promisify(execFile);

export class GitStore {
  constructor(private repo: string) {}

  private git(
    args: string[],
    opts: { input?: Buffer; env?: NodeJS.ProcessEnv } = {},
  ) {
    return run("git", ["--git-dir", this.repo, ...args], {
      env: { ...process.env, ...opts.env },
      encoding: "buffer",
      maxBuffer: 256 * 1024 * 1024, // a bulk cat-file can be large
    } as never);
  }

  ref(pid: string) {
    if (!/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(pid))
      throw new Error("bad id");
    return `refs/heads/project/${pid}`;
  }

  async get(pid: string, coll: string, id: string) {
    const { stdout } = await this.git([
      "cat-file",
      "-p",
      `${this.ref(pid)}:collections/${coll}/${id}.json`,
    ]);
    return JSON.parse(stdout.toString());
  }

  // Writes follow the same six steps as the Python version:
  //   1. pin OLD          rev-parse
  //   2. private index    GIT_INDEX_FILE in a temp dir
  //   3. read-tree OLD
  //   4. hash-object + update-index --index-info   (batch the whole transaction)
  //   5. write-tree + commit-tree -p OLD
  //   6. update-ref REF NEW OLD   -- retry with backoff on non-zero exit
}
```

Three things to get right in the port, each of which has bitten someone:

- **Buffers, not strings.** Record content can be any UTF-8; decoding stdout as
  a string mangles binary framing in `cat-file --batch` output.
- **`maxBuffer`.** Node's default is small enough that a bulk read of a large
  collection truncates silently. Raise it or stream.
- **Concurrency inside one process.** Node's single-threaded event loop makes it
  easy to interleave two writes to one project. The CAS still protects you, but
  a per-ref promise queue avoids the wasted retries.

## Swapping in a SQL backend

When migration comes, implement the same interface over SQL:

- `get` → `SELECT ... WHERE project_id = $1 AND id = $2`
- `list_records` → `SELECT ... WHERE project_id = $1 ORDER BY id`
- `put` → `INSERT ... ON CONFLICT (project_id, id) DO UPDATE`
- `transaction` / `atomic` → a real DB transaction; `atomic` maps to
  `SELECT ... FOR UPDATE` or a serializable transaction with retry, which is the
  same optimistic-retry shape you already had
- `history` → drop it, or read the archived bundle

Because the shapes line up, you can run both implementations side by side during
the cutover and compare their outputs on live traffic. The
`ceh-git-datastore:migrate-git-datastore` skill covers the sequencing.
