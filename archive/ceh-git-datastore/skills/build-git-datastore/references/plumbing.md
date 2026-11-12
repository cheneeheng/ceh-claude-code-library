# Git plumbing for a bare-repo datastore

Every command here runs against a bare repo with `--git-dir` and never touches a
working tree. Porcelain commands (`add`, `commit`, `checkout`, `mv`, `rm`) all
assume a working tree; none of them appear below, and none should appear in an
app.

## Setup

```bash
git init --bare data.git
git --git-dir data.git config core.logAllRefUpdates true   # reflog = free undo
git --git-dir data.git config gc.auto 256                  # repack automatically
```

`core.logAllRefUpdates` is off by default in bare repos. Turning it on records
every ref movement with a timestamp, which is what makes "put project X back to
how it was an hour ago" a one-liner. It costs disk — objects stay reachable
until the reflog expires — so pair it with a deliberate `gc.reflogExpire`.

## Reads

Reads never lock anything and never conflict with writes. A read is a lookup in
the object database, and objects are immutable.

```bash
# one record
git --git-dir data.git cat-file -p refs/heads/project/p1:collections/tasks/ID.json

# ids in a collection (byte order == creation order with sortable ids)
git --git-dir data.git ls-tree --name-only refs/heads/project/p1:collections/tasks

# collections in a project
git --git-dir data.git ls-tree --name-only refs/heads/project/p1:collections

# every project ref plus its current commit
git --git-dir data.git for-each-ref --format='%(refname)%09%(objectname)' refs/heads/project/

# does a project exist
git --git-dir data.git rev-parse --verify --quiet refs/heads/project/p1^{commit}
```

### Bulk reads: one process, not N

The single most important performance habit. Feed many specs to one
`cat-file --batch`:

```bash
printf 'refs/heads/project/p1:collections/tasks/A.json\nrefs/heads/project/p1:collections/tasks/B.json\n' \
  | git --git-dir data.git cat-file --batch
```

Output framing per object: a header line (`<oid> <type> <size>`), then exactly
`<size>` bytes, then a newline. A missing object yields `<spec> missing` with no
payload — that is how you distinguish "this project has no meta.json" from a
failed read.

Reading 700 records this way takes ~220 ms. As 700 separate `cat-file` calls it
takes minutes: fork/exec dominates, not git.

For a hot read path, keep one `cat-file --batch` process alive for the life of
the app and write specs to its stdin. Reads drop into the tens of microseconds.
Do this when measurement says to, not before — it adds a process to supervise.

## Writes

The sequence, and why each step exists:

```bash
REF=refs/heads/project/p1
OLD=$(git --git-dir data.git rev-parse "$REF")      # 1. pin the base

export GIT_INDEX_FILE=$(mktemp -u)                  # 2. private index
git --git-dir data.git read-tree "$OLD"             # 3. load current tree

BLOB=$(printf '%s' "$JSON" | git --git-dir data.git hash-object -w --stdin)
printf '100644 %s\t%s\n' "$BLOB" "collections/tasks/ID.json" \
  | git --git-dir data.git update-index --index-info      # 4. stage

TREE=$(git --git-dir data.git write-tree)                 # 5. materialise tree
NEW=$(git --git-dir data.git commit-tree "$TREE" -p "$OLD" -m "put tasks/ID")
git --git-dir data.git update-ref "$REF" "$NEW" "$OLD"    # 6. compare-and-swap
rm -f "$GIT_INDEX_FILE"
```

**Step 2 is the whole trick.** `GIT_INDEX_FILE` pointing at a private temp path
gives the write its own staging area. Without it every concurrent request fights
over `.git/index`, and you have reinvented a global lock.

**Step 6 is the concurrency control.** `update-ref <ref> <new> <old>` updates
only if the ref still equals `<old>`; git enforces this atomically via a
lockfile, so it holds across processes and across separate app workers. Non-zero
exit means someone else committed first — back off and retry.

Note that step 1 and step 6 must use the _same_ `OLD`. Re-resolving the ref
after computing the new value is the classic lost-update bug: another writer
lands in between, your CAS succeeds against their commit, and their write
vanishes with no error anywhere.

### Staging deletes

```bash
NULL=$(printf '0%.0s' $(seq 40))
printf '000000 %s\t%s\n' "$NULL" "collections/tasks/ID.json" \
  | git --git-dir data.git update-index --index-info
```

Mode `000000` with the null oid removes a path. Do **not** reach for
`git update-index --force-remove`: it looks right, but when the path is not
already in the index git falls back to stating the filesystem and fails with
`fatal: this operation must be run in a work tree`.

Batch every put and delete in a transaction into a single `--index-info` call.

### Creating an orphan branch

```bash
# build an index containing just meta.json, then:
NEW=$(git --git-dir data.git commit-tree "$TREE" -m "create project p1")   # no -p
git --git-dir data.git update-ref refs/heads/project/p1 "$NEW" ""
```

No `-p` is what makes it an orphan: a root commit with no parent. The empty
old-value in `update-ref` means "only if this ref does not exist", so two
concurrent creates cannot both win.

### Deleting a project

```bash
git --git-dir data.git update-ref -d refs/heads/project/p1 "$CURRENT_SHA"
```

Passing the current sha makes the delete conditional too, so you cannot
accidentally drop a project that changed while you were deciding.

## Empty tree

Do not hardcode `4b825dc642cb6eb9a060e54bf8d69288fbee4904`. That is the SHA-1
value; a repo created with `--object-format=sha256` has a different one. Get it
at runtime with `git mktree </dev/null`.

## Snapshots and time travel

A commit sha is an immutable snapshot of an entire project. Everything below
falls out of that, and it is why migration later is tractable.

```bash
# read a record as it was at an old commit
git --git-dir data.git cat-file -p <sha>:collections/tasks/ID.json

# what changed between two points, with add/modify/delete status
git --git-dir data.git diff --name-status <old_sha> <new_sha>

# history of one record
git --git-dir data.git log --format='%H %aI %an %s' -- collections/tasks/ID.json

# roll a project back (still a CAS -- fails if someone wrote meanwhile)
git --git-dir data.git update-ref refs/heads/project/p1 <old_sha> <current_sha>

# what has this ref pointed at recently
git --git-dir data.git reflog show refs/heads/project/p1
```

## Ref naming

Use `refs/heads/project/<id>` and validate `<id>` against a conservative charset
(`[A-Za-z0-9][A-Za-z0-9._-]*`, no `..`, no trailing `.lock`) before it reaches
git. Reject rather than escape: it is cheaper, predictable, and keeps ids
identical after migration.

`refs/heads/*` rather than a custom namespace like `refs/projects/*` because
`git push --mirror` and `git clone` handle `refs/heads` by default, and backup
being boring is a feature. A custom namespace works but needs an explicit
refspec everywhere, and one forgotten refspec is a silent backup gap.

`refs/heads/project` and `refs/heads/project/p1` cannot both exist — git refs
are filesystem paths. Never create a bare `project` ref.

## Verifying integrity

```bash
git --git-dir data.git fsck --no-progress    # object graph is intact
git --git-dir data.git count-objects -vH     # loose vs packed, disk usage
```

`fsck` is cheap enough to run nightly and is the honest answer to "is the data
still fine after all those concurrent writes".
