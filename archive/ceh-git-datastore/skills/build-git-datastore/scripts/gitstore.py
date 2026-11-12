#!/usr/bin/env python3
"""
gitstore.py - A git-backed document store. Python stdlib only.

Data lives in a BARE git repository. There is no working tree and no checkout,
ever. Reads go through `git cat-file`; writes go through a per-call temporary
index and `git update-ref` compare-and-swap. That is what makes this safe to
call from a concurrent web app: two requests touching two different projects
never share a lock, and two requests touching the SAME project are serialised
by an atomic ref update rather than by a mutex you have to remember to hold.

Layout:

    data.git/                          bare repo, one per deployed instance
      refs/heads/main                  instance metadata (optional)
      refs/heads/project/<pid>         one ORPHAN branch per project
                                         meta.json
                                         collections/<name>/<record-id>.json

Orphan branches are the point: each project gets its own independent ref, so
writes to project A never contend with writes to project B. They cost nothing
extra in storage -- git objects are content-addressed and shared across the
whole object database regardless of commit ancestry.

CLI:
    python gitstore.py init <repo>
    python gitstore.py projects <repo>
    python gitstore.py create-project <repo> <pid> [name]
    python gitstore.py put <repo> <pid> <collection> <id|-> [< data.json]
    python gitstore.py get <repo> <pid> <collection> <id>
    python gitstore.py list <repo> <pid> <collection>
    python gitstore.py delete <repo> <pid> <collection> <id>
    python gitstore.py history <repo> <pid> [limit]
"""

from __future__ import annotations

import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator

__all__ = ["GitStore", "ConflictError", "NotFound", "new_id"]

# --------------------------------------------------------------------------
# ids
# --------------------------------------------------------------------------

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_id() -> str:
    """ULID-ish: 26 chars, lexicographically sortable by creation time.

    Sortable ids matter here because `git ls-tree` returns paths in byte order.
    That gives you "list newest N records" without an index, and it survives a
    later move to SQL unchanged (unlike an auto-increment integer, which you
    would have to invent during migration)."""
    ms = int(time.time() * 1000)
    rnd = random.getrandbits(80)
    n = (ms << 80) | rnd
    out = []
    for _ in range(26):
        out.append(_CROCKFORD[n & 0x1F])
        n >>= 5
    return "".join(reversed(out))


# --------------------------------------------------------------------------
# errors
# --------------------------------------------------------------------------


class NotFound(KeyError):
    pass


class ConflictError(RuntimeError):
    """Ref moved under us more times than we were willing to retry."""


# --------------------------------------------------------------------------
# validation
# --------------------------------------------------------------------------

_SAFE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def _check(kind: str, value: str) -> str:
    # Path and ref components come from user input in most apps. Rejecting
    # anything but a conservative charset is cheaper and more predictable than
    # trying to escape it later, and it keeps ids identical if you migrate.
    if not _SAFE.match(value) or ".." in value or value.endswith(".lock"):
        raise ValueError(f"invalid {kind}: {value!r}")
    return value


# --------------------------------------------------------------------------
# store
# --------------------------------------------------------------------------


@dataclass
class GitStore:
    repo: str
    author: str = "gitstore <gitstore@localhost>"
    max_retries: int = 8
    _empty_tree: str = field(default="", init=False, repr=False)

    # -- process plumbing ---------------------------------------------------

    def _git(
        self,
        *args: str,
        stdin: bytes | None = None,
        env: dict[str, str] | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        e = dict(os.environ)
        e.setdefault("GIT_TERMINAL_PROMPT", "0")
        if env:
            e.update(env)
        p = subprocess.run(
            ["git", "--git-dir", self.repo, *args],
            input=stdin,
            capture_output=True,
            env=e,
        )
        if check and p.returncode != 0:
            raise RuntimeError(
                f"git {' '.join(args)} failed ({p.returncode}): "
                f"{p.stderr.decode('utf-8', 'replace').strip()}"
            )
        return p

    def _out(self, *args: str, **kw: Any) -> str:
        return self._git(*args, **kw).stdout.decode("utf-8").strip()

    # -- lifecycle ----------------------------------------------------------

    def init(self) -> "GitStore":
        if not os.path.exists(os.path.join(self.repo, "HEAD")):
            os.makedirs(self.repo, exist_ok=True)
            subprocess.run(["git", "init", "--bare", "--quiet", self.repo], check=True)
        # Reflogs are the free undo button: every ref update is recorded with a
        # timestamp, so "restore project X to how it looked an hour ago" is a
        # one-liner. Bare repos disable them by default, so turn them on.
        self._git("config", "core.logAllRefUpdates", "true")
        # Loose objects accumulate fast when every write is a commit. Let git
        # repack on its own rather than discovering a 40k-file directory later.
        self._git("config", "gc.auto", "256")
        self._git("config", "receive.denyCurrentBranch", "ignore")
        return self

    @property
    def empty_tree(self) -> str:
        # Do not hardcode 4b825dc... -- it is the SHA-1 value, and a repo
        # created with --object-format=sha256 has a different one.
        if not self._empty_tree:
            self._empty_tree = self._out("mktree", stdin=b"")
        return self._empty_tree

    # -- refs ---------------------------------------------------------------

    @staticmethod
    def ref(pid: str) -> str:
        return f"refs/heads/project/{_check('project id', pid)}"

    def _resolve(self, ref: str) -> str | None:
        p = self._git(
            "rev-parse", "--verify", "--quiet", ref + "^{commit}", check=False
        )
        out = p.stdout.decode().strip()
        return out or None

    # -- reads --------------------------------------------------------------

    def list_projects(self) -> list[dict]:
        """One process, not one process per project.

        for-each-ref gives the ref names; cat-file --batch streams every
        meta.json blob back over a single pipe. Doing this as N subprocess
        calls is the most common way to make this design look slow when it
        isn't -- process spawn dominates, not git."""
        refs = self._out(
            "for-each-ref", "--format=%(refname)", "refs/heads/project/"
        ).splitlines()
        refs = [r for r in refs if r]
        if not refs:
            return []
        specs = "\n".join(f"{r}:meta.json" for r in refs).encode() + b"\n"
        p = self._git("cat-file", "--batch", stdin=specs)
        out: list[dict] = []
        for ref, blob in zip(refs, _parse_batch(p.stdout)):
            pid = ref.split("refs/heads/project/", 1)[1]
            meta = json.loads(blob) if blob is not None else {}
            meta.setdefault("id", pid)
            out.append(meta)
        return sorted(out, key=lambda m: m.get("id", ""))

    def get(self, pid: str, collection: str, rid: str, at: str | None = None) -> dict:
        path = self._path(collection, rid)
        p = self._git("cat-file", "-p", f"{at or self.ref(pid)}:{path}", check=False)
        if p.returncode != 0:
            raise NotFound(f"{pid}/{collection}/{rid}")
        return json.loads(p.stdout)

    def list_ids(self, pid: str, collection: str, at: str | None = None) -> list[str]:
        _check("collection", collection)
        p = self._git(
            "ls-tree",
            "--name-only",
            f"{at or self.ref(pid)}:collections/{collection}",
            check=False,
        )
        if p.returncode != 0:
            return []
        return [n[:-5] for n in p.stdout.decode().split("\n") if n.endswith(".json")]

    def list_records(
        self, pid: str, collection: str, at: str | None = None
    ) -> list[dict]:
        """Bulk read. Again: one cat-file process for the whole collection."""
        ids = self.list_ids(pid, collection, at=at)
        if not ids:
            return []
        ref = at or self.ref(pid)
        specs = (
            "\n".join(f"{ref}:collections/{collection}/{i}.json" for i in ids).encode()
            + b"\n"
        )
        p = self._git("cat-file", "--batch", stdin=specs)
        return [json.loads(b) for b in _parse_batch(p.stdout) if b is not None]

    def history(self, pid: str, limit: int = 20) -> list[dict]:
        p = self._git(
            "log",
            f"--max-count={limit}",
            "--format=%H%x1f%aI%x1f%an%x1f%s",
            self.ref(pid),
            check=False,
        )
        if p.returncode != 0:
            return []
        rows = []
        for line in p.stdout.decode().strip().split("\n"):
            if not line:
                continue
            sha, when, who, subject = line.split("\x1f")
            rows.append({"sha": sha, "at": when, "by": who, "message": subject})
        return rows

    # -- writes -------------------------------------------------------------

    @contextmanager
    def transaction(self, pid: str, message: str = "update") -> Iterator["Tx"]:
        """Batch several changes into ONE commit.

        This is the feature that makes a git store better than a folder of JSON
        files: either every change in the block lands or none of them do, and a
        crash mid-block leaves nothing half-written. Use it whenever two records
        have to change together.

        On a lost race the ops are replayed on top of the winner's tree, which
        is right for blind writes ("set these paths to these values"). If your
        block READS a record and computes the new value from it, that replay
        would silently clobber the other writer -- use `atomic()` instead, which
        re-runs your whole function against fresh state."""
        tx = Tx(self, pid)
        yield tx
        if tx.ops:
            self._commit_with_retry(pid, tx, message)

    def atomic(self, pid: str, fn, message: str = "update") -> Any:
        """Read-modify-write. `fn(tx)` may be called more than once.

        Keep the function pure and side-effect free -- it re-runs from scratch
        whenever another writer commits first, which is exactly what makes
        counters and "append to a list field" correct here instead of lossy."""
        for attempt in range(self.max_retries):
            base = self._resolve(self.ref(pid))
            if base is None:
                raise NotFound(f"no such project: {pid}")
            tx = Tx(self, pid, base=base)
            result = fn(tx)
            if not tx.ops or self._commit(pid, tx, message):
                return result
            time.sleep(0.005 * (2**attempt) * (0.5 + random.random()))
        raise ConflictError(f"{pid}: ref kept moving after {self.max_retries} tries")

    def _commit_with_retry(self, pid: str, tx: "Tx", message: str) -> None:
        for attempt in range(self.max_retries):
            if self._commit(pid, tx, message):
                return
            time.sleep(0.005 * (2**attempt) * (0.5 + random.random()))
        raise ConflictError(f"{pid}: ref kept moving after {self.max_retries} tries")

    def put(self, pid: str, collection: str, rid: str | None, doc: dict) -> dict:
        rid = rid or doc.get("id") or new_id()
        with self.transaction(pid, f"put {collection}/{rid}") as tx:
            tx.put(collection, rid, doc)
        return self.get(pid, collection, rid)

    def delete(self, pid: str, collection: str, rid: str) -> None:
        with self.transaction(pid, f"delete {collection}/{rid}") as tx:
            tx.delete(collection, rid)

    def create_project(self, pid: str, meta: dict | None = None) -> dict:
        ref = self.ref(pid)
        if self._resolve(ref):
            raise ValueError(f"project exists: {pid}")
        meta = {
            "id": pid,
            "created_at": _now(),
            "schema_version": 1,
            **(meta or {}),
        }
        idx = _tmp_index()
        try:
            blob = self._out(
                "hash-object",
                "-w",
                "--stdin",
                stdin=_dump(meta),
                env={"GIT_INDEX_FILE": idx},
            )
            self._git(
                "update-index",
                "--add",
                "--cacheinfo",
                f"100644,{blob},meta.json",
                env={"GIT_INDEX_FILE": idx},
            )
            tree = self._out("write-tree", env={"GIT_INDEX_FILE": idx})
        finally:
            _rm(idx)
        # No -p: this commit has no parent, which is exactly what makes the
        # branch orphaned.
        commit = self._out(
            "commit-tree", tree, "-m", f"create project {pid}", env=self._ident()
        )
        # An empty old-value means "only if the ref does not exist yet" -- a
        # create-if-absent, so two concurrent creates cannot both win.
        p = self._git("update-ref", ref, commit, "", check=False)
        if p.returncode != 0:
            raise ValueError(f"project exists: {pid}")
        return meta

    def delete_project(self, pid: str) -> None:
        ref = self.ref(pid)
        cur = self._resolve(ref)
        if not cur:
            raise NotFound(pid)
        self._git("update-ref", "-d", ref, cur)

    # -- internals ----------------------------------------------------------

    def _path(self, collection: str, rid: str) -> str:
        return f"collections/{_check('collection', collection)}/{_check('record id', rid)}.json"

    def _ident(self) -> dict[str, str]:
        name, _, email = self.author.partition(" <")
        email = email.rstrip(">") or "gitstore@localhost"
        return {
            "GIT_AUTHOR_NAME": name or "gitstore",
            "GIT_AUTHOR_EMAIL": email,
            "GIT_COMMITTER_NAME": name or "gitstore",
            "GIT_COMMITTER_EMAIL": email,
        }

    def _commit(self, pid: str, tx: "Tx", message: str) -> bool:
        ref = self.ref(pid)
        old = tx.base or self._resolve(ref)
        if old is None:
            raise NotFound(f"no such project: {pid}")
        idx = _tmp_index()
        env = {"GIT_INDEX_FILE": idx}
        try:
            # A private index file per write is what removes the shared lock.
            # `git add` in a working tree would serialise every request in the
            # whole app on .git/index; this does not.
            self._git("read-tree", old, env=env)
            lines = []
            null = "0" * len(self.empty_tree)
            for op in tx.ops:
                if op[0] == "put":
                    _, path, payload = op
                    blob = self._out(
                        "hash-object", "-w", "--stdin", stdin=payload, env=env
                    )
                    lines.append(f"100644 {blob}\t{path}")
                else:
                    # Mode 000000 + the null oid is how you stage a deletion
                    # without a work tree. `--force-remove` looks fine but
                    # stats the filesystem when the path is not already in the
                    # index, which blows up in a bare repo.
                    lines.append(f"000000 {null}\t{op[1]}")
            # One update-index call for the whole transaction. Spawning a
            # process per record is what makes this design feel slow at 50
            # records; git itself is not the bottleneck, fork/exec is.
            self._git(
                "update-index",
                "--index-info",
                stdin=("\n".join(lines) + "\n").encode(),
                env=env,
            )
            tree = self._out("write-tree", env=env)
        finally:
            _rm(idx)
        if tree == self._out("rev-parse", f"{old}^{{tree}}"):
            return True  # no-op write; do not litter history with empty commits
        commit = self._out(
            "commit-tree", tree, "-p", old, "-m", message, env=self._ident()
        )
        # The whole concurrency story in one line: swap the ref only if it still
        # points where we think it does. Git does this atomically via a lockfile,
        # so it holds across processes and even across separate app workers.
        return self._git("update-ref", ref, commit, old, check=False).returncode == 0


@dataclass
class Tx:
    store: GitStore
    pid: str
    base: str | None = None
    ops: list[tuple] = field(default_factory=list)

    # Reads go to `base` -- the exact commit this transaction started from --
    # not to the live ref. A commit sha is an immutable snapshot, so this gives
    # real snapshot isolation for free. Reading the live ref instead is subtly
    # wrong: another writer can land between your read and your compare-and-swap,
    # and you would overwrite them while the CAS still succeeds.
    def _src(self) -> str:
        return self.base or self.store.ref(self.pid)

    def get(self, collection: str, rid: str) -> dict:
        return self.store.get(self.pid, collection, rid, at=self._src())

    def list_records(self, collection: str) -> list[dict]:
        return self.store.list_records(self.pid, collection, at=self._src())

    def put(self, collection: str, rid: str | None, doc: dict) -> str:
        rid = rid or doc.get("id") or new_id()
        now = _now()
        created = doc.get("created_at")
        if created is None:
            # An update must not reset created_at. Callers routinely pass a
            # partial doc, so look up the existing record rather than trusting
            # the payload to carry the original timestamp.
            try:
                created = self.store.get(self.pid, collection, rid, at=self._src()).get(
                    "created_at", now
                )
            except (NotFound, RuntimeError):
                created = now
        body = {
            **doc,
            "id": rid,
            "created_at": created,
            "updated_at": now,
            "schema_version": doc.get("schema_version", 1),
        }
        self.ops.append(("put", self.store._path(collection, rid), _dump(body)))
        return rid

    def delete(self, collection: str, rid: str) -> None:
        self.ops.append(("delete", self.store._path(collection, rid)))


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _now() -> str:
    from datetime import datetime, timezone

    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _dump(obj: dict) -> bytes:
    # sort_keys is not cosmetic: stable key order means an unchanged record
    # hashes to the same blob, so re-writing identical data produces no new
    # object and no commit. It also makes `git diff` readable by humans.
    return (
        json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    ).encode()


def _tmp_index() -> str:
    fd, path = tempfile.mkstemp(prefix="gitstore-idx-")
    os.close(fd)
    os.unlink(path)  # read-tree wants it absent or valid, not empty
    return path


def _rm(path: str) -> None:
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass


def _parse_batch(data: bytes) -> Iterator[bytes | None]:
    """Parse `git cat-file --batch` output: header line, payload, newline.

    Missing objects come back as `<spec> missing` with no payload, which is how
    you tell "project has no meta.json" from "read failed"."""
    i = 0
    n = len(data)
    while i < n:
        j = data.index(b"\n", i)
        header = data[i:j].decode()
        i = j + 1
        parts = header.split()
        if parts[-1] == "missing":
            yield None
            continue
        size = int(parts[-1])
        yield data[i : i + size]
        i += size + 1


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    cmd, repo, rest = argv[1], argv[2], argv[3:]
    s = GitStore(repo)
    if cmd == "init":
        s.init()
        print(f"initialised {repo}")
    elif cmd == "projects":
        print(json.dumps(s.list_projects(), indent=2))
    elif cmd == "create-project":
        meta = {"name": rest[1]} if len(rest) > 1 else {}
        print(json.dumps(s.create_project(rest[0], meta), indent=2))
    elif cmd == "put":
        doc = json.load(sys.stdin)
        rid = None if rest[2] == "-" else rest[2]
        print(json.dumps(s.put(rest[0], rest[1], rid, doc), indent=2))
    elif cmd == "get":
        print(json.dumps(s.get(rest[0], rest[1], rest[2]), indent=2))
    elif cmd == "list":
        print(json.dumps(s.list_records(rest[0], rest[1]), indent=2))
    elif cmd == "delete":
        s.delete(rest[0], rest[1], rest[2])
    elif cmd == "history":
        print(json.dumps(s.history(rest[0], int(rest[1]) if rest else 20), indent=2))
    else:
        print(f"unknown command: {cmd}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
