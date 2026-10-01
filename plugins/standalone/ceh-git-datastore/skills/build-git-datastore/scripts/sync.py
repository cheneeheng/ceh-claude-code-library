#!/usr/bin/env python3
"""
sync.py - Push a git-backed datastore to a remote, out of the request path.

Backup here is `git push`, but a push in a write handler couples write latency
to network conditions and makes every blip a user-visible error. So this runs a
background worker: writers call notify(), the worker coalesces bursts and pushes
once, and failures back off instead of failing requests.

    syncer = Syncer("/srv/data.git", remote="backup",
                    debounce=5.0, min_interval=60.0)
    syncer.start()

    store.put("acme", "tasks", None, {...})
    syncer.notify()                  # cheap, non-blocking, safe to spam

    syncer.status()                  # for a health endpoint / metrics
    syncer.stop(final_push=True)     # on shutdown

The single most important thing here is the mass-deletion guard. `push --mirror`
deletes remote refs that no longer exist locally, which is what you want when a
project is deleted -- and is also how a corrupted or restored-from-stale local
repo destroys the remote on the next push. The guard refuses a push that would
drop an implausible fraction of refs, and makes you pass --force-prune to say
you meant it.

CLI:
    python sync.py setup   <repo> <remote-url> [--name backup]
    python sync.py push    <repo> [--name backup] [--force-prune]
    python sync.py bundle  <repo> <dir> [--keep 7]
    python sync.py status  <repo>
    python sync.py daemon  <repo> [--name backup] [--debounce 5] [--min-interval 60]
    python sync.py restore <source> <dest>
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Any

STATE_FILE = "sync-state.json"

# A push that removes more than this fraction of the remote's refs is treated as
# a bug rather than an intention. Deleting a few projects is normal; deleting
# half of them in one push is what a restored-from-stale-backup repo looks like.
PRUNE_GUARD_FRACTION = 0.25
PRUNE_GUARD_MIN_REFS = 8


class PushRejected(RuntimeError):
    """Remote refused the push. Usually non-fast-forward -- see the message."""


class PruneGuard(RuntimeError):
    """Push would delete an implausible number of remote refs."""


# --------------------------------------------------------------------------


def _git(repo: str, *args: str, timeout: int = 300) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.setdefault("GIT_TERMINAL_PROMPT", "0")  # never hang waiting for a password
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes")
    return subprocess.run(
        ["git", "--git-dir", repo, *args],
        capture_output=True,
        env=env,
        timeout=timeout,
    )


def _ok(repo: str, *args: str, **kw) -> str:
    p = _git(repo, *args, **kw)
    if p.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)}: {p.stderr.decode('utf-8', 'replace').strip()}"
        )
    return p.stdout.decode("utf-8", "replace").strip()


def _state_path(repo: str) -> str:
    return os.path.join(repo, STATE_FILE)


def read_state(repo: str) -> dict:
    try:
        with open(_state_path(repo)) as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_state(repo: str, state: dict) -> None:
    # Write-then-rename so a crash mid-write cannot leave unparseable state and
    # wedge the guard on the next push.
    tmp = _state_path(repo) + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(state, fh, indent=2)
    os.replace(tmp, _state_path(repo))


def local_refs(repo: str, prefix: str = "refs/heads/") -> dict[str, str]:
    txt = _ok(repo, "for-each-ref", "--format=%(refname)%09%(objectname)", prefix)
    return dict(line.split("\t") for line in txt.splitlines() if "\t" in line)


def remote_refs(repo: str, name: str) -> dict[str, str]:
    """Ask the remote what it has. Requires network; raises if unreachable."""
    txt = _ok(repo, "ls-remote", name, timeout=60)
    out = {}
    for line in txt.splitlines():
        if "\t" not in line:
            continue
        sha, ref = line.split("\t", 1)
        if ref.endswith("^{}"):
            continue
        if ref.startswith("refs/heads/"):
            out[ref] = sha
    return out


# --------------------------------------------------------------------------


def _record_failure(repo: str, message: str) -> None:
    state = read_state(repo)
    state.update(
        {
            "last_attempt_at": time.time(),
            "last_error": message[-2000:],
            "consecutive_failures": state.get("consecutive_failures", 0) + 1,
        }
    )
    write_state(repo, state)


def setup(repo: str, url: str, name: str = "backup") -> None:
    existing = _git(repo, "remote", "get-url", name)
    if existing.returncode == 0:
        _ok(repo, "remote", "set-url", name, url)
    else:
        _ok(repo, "remote", "add", name, url)
    # Drop the fetch refspec so git stops creating refs/remotes/<name>/* after
    # each push. Those tracking refs keep deleted projects reachable, which
    # means `git gc` can never reclaim a deleted project's objects -- and if you
    # ever mirror-push, they get shipped to the remote as a second, stale copy
    # of your entire dataset.
    _git(repo, "config", "--unset-all", f"remote.{name}.fetch")
    stale = _git(repo, "for-each-ref", "--format=%(refname)", f"refs/remotes/{name}/")
    for ref in stale.stdout.decode().split():
        _git(repo, "update-ref", "-d", ref)
    print(f"remote '{name}' -> {url}")


def push(
    repo: str, name: str = "backup", force_prune: bool = False, timeout: int = 300
) -> dict:
    """One synchronous push of all project refs. Raises on refusal."""
    started = time.time()
    local = local_refs(repo)

    try:
        remote = remote_refs(repo, name)
    except RuntimeError as e:
        # An unreachable remote is a transient condition, not a data problem --
        # but it must still count as a failure. A health check reporting zero
        # failures while every backup is silently failing is worse than useless.
        _record_failure(repo, f"cannot reach remote '{name}': {e}")
        raise PushRejected(f"cannot reach remote '{name}': {e}") from e

    would_delete = [r for r in remote if r not in local and r.startswith("refs/")]
    if would_delete and not force_prune:
        n_remote = max(1, len(remote))
        frac = len(would_delete) / n_remote
        if len(would_delete) >= PRUNE_GUARD_MIN_REFS and frac > PRUNE_GUARD_FRACTION:
            raise PruneGuard(
                f"push would delete {len(would_delete)} of {n_remote} remote refs "
                f"({frac:.0%}). This is what a stale or corrupted local repo looks "
                f"like. Confirm the local store is authoritative, then re-run with "
                f"--force-prune. Examples: " + ", ".join(sorted(would_delete)[:5])
            )

    # An explicit refspec instead of --mirror. --mirror means "push every ref
    # under refs/", which includes refs/remotes/* and refs/stash -- none of which
    # is data. This pushes exactly the project branches and prunes the ones that
    # no longer exist locally, which is the behaviour --mirror was wanted for.
    p = _git(
        repo, "push", "--prune", name, "refs/heads/*:refs/heads/*", timeout=timeout
    )
    err = p.stderr.decode("utf-8", "replace").strip()
    now = time.time()

    if p.returncode != 0:
        _record_failure(repo, err)
        if "non-fast-forward" in err or "fetch first" in err:
            raise PushRejected(
                "non-fast-forward: the remote has commits this repo does not. "
                "That means something else wrote to it -- almost always a second "
                "app node, which this design does not support. Do not force-push "
                "until you know which side is authoritative. " + err[-500:]
            )
        raise PushRejected(err[-1000:] or f"push failed ({p.returncode})")

    state = read_state(repo)
    state.update(
        {
            "last_attempt_at": now,
            "last_success_at": now,
            "last_error": None,
            "consecutive_failures": 0,
            "ref_count": len(local),
            "deleted_refs_last_push": len(would_delete),
            "duration_s": round(now - started, 3),
        }
    )
    write_state(repo, state)
    return {
        "pushed": True,
        "refs": len(local),
        "deleted": len(would_delete),
        "duration_s": state["duration_s"],
    }


def bundle(repo: str, outdir: str, keep: int = 7) -> str:
    """A bundle is a single file holding every ref and all history.

    Worth having alongside the mirror precisely because it is NOT a mirror: a
    bad local state that propagates to the remote on the next push cannot reach
    yesterday's bundle."""
    os.makedirs(outdir, exist_ok=True)
    stamp = time.strftime("%Y-%m-%dT%H%M%S", time.gmtime())
    path = os.path.join(outdir, f"data-{stamp}.bundle")
    _ok(repo, "bundle", "create", path, "--all", timeout=1800)
    # Verify before trusting it. A bundle that was never verified is a backup
    # that was never taken.
    _ok(repo, "bundle", "verify", path, timeout=600)

    olds = sorted(
        f for f in os.listdir(outdir) if f.startswith("data-") and f.endswith(".bundle")
    )
    for f in olds[:-keep] if keep > 0 else []:
        os.unlink(os.path.join(outdir, f))
    return path


def restore(source: str, dest: str) -> None:
    """Clone a remote URL or a .bundle file back into a working bare store."""
    if os.path.exists(dest):
        raise SystemExit(f"refusing to overwrite existing path: {dest}")
    p = subprocess.run(["git", "clone", "--mirror", source, dest], capture_output=True)
    if p.returncode != 0:
        raise SystemExit(p.stderr.decode("utf-8", "replace"))
    _ok(dest, "fsck", "--no-progress", timeout=1800)
    n = len([r for r in local_refs(dest) if r.startswith("refs/heads/project/")])
    print(f"restored {dest}: {n} project refs, fsck clean")


# --------------------------------------------------------------------------


@dataclass
class Syncer:
    repo: str
    remote: str = "backup"
    debounce: float = 5.0
    """Wait this long after the last write before pushing, so a burst of 50
    writes produces one push rather than 50."""
    min_interval: float = 60.0
    """Never push more often than this, however busy the app is."""
    max_backoff: float = 900.0
    on_error: Any = None
    """Optional callable(exc) -- wire it to your logger or metrics."""

    _dirty: threading.Event = field(default_factory=threading.Event, init=False)
    _stop: threading.Event = field(default_factory=threading.Event, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _thread: threading.Thread | None = field(default=None, init=False)
    _last_push: float = field(default=0.0, init=False)
    _failures: int = field(default=0, init=False)

    def notify(self) -> None:
        """Call after a write. Non-blocking; safe to call on every request."""
        self._dirty.set()

    def start(self) -> "Syncer":
        if self._thread and self._thread.is_alive():
            return self
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run, name="gitstore-sync", daemon=True
        )
        self._thread.start()
        return self

    def stop(self, final_push: bool = True, timeout: float = 60.0) -> None:
        self._stop.set()
        self._dirty.set()
        if self._thread:
            self._thread.join(timeout=timeout)
        if final_push and self._dirty_since_push():
            # Losing the last few writes because the process shut down is the
            # one data-loss path this design has; take it seriously.
            try:
                self.push_now()
            except Exception as e:
                self._report(e)

    def push_now(self, force_prune: bool = False) -> dict:
        """Synchronous push. Use for CLI, admin endpoints, and shutdown."""
        with self._lock:
            self._dirty.clear()
            res = push(self.repo, self.remote, force_prune=force_prune)
            self._last_push = time.time()
            self._failures = 0
            return res

    def status(self) -> dict:
        st = read_state(self.repo)
        last = st.get("last_success_at")
        return {
            "remote": self.remote,
            "running": bool(self._thread and self._thread.is_alive()),
            "pending": self._dirty.is_set(),
            "consecutive_failures": st.get("consecutive_failures", 0),
            "last_error": st.get("last_error"),
            "last_success_at": last,
            "seconds_since_success": round(time.time() - last, 1) if last else None,
            "ref_count": st.get("ref_count"),
        }

    # -- internals ----------------------------------------------------------

    def _dirty_since_push(self) -> bool:
        return self._dirty.is_set()

    def _report(self, exc: Exception) -> None:
        if self.on_error:
            try:
                self.on_error(exc)
                return
            except Exception:
                pass
        print(f"[sync] {type(exc).__name__}: {exc}", file=sys.stderr)

    def _run(self) -> None:
        while not self._stop.is_set():
            # Wait for a write. The timeout keeps the loop responsive to stop().
            if not self._dirty.wait(timeout=1.0):
                continue
            if self._stop.is_set():
                return
            # Coalesce: sleep the debounce window, and if more writes land during
            # it, the flag is simply still set -- one push covers all of them.
            self._stop.wait(self.debounce)
            if self._stop.is_set():
                return
            wait = self._last_push + self.min_interval - time.time()
            if wait > 0 and self._stop.wait(wait):
                return
            try:
                self.push_now()
            except PruneGuard as e:
                # Never retry a guard trip -- retrying cannot help, and the whole
                # point is that a human decides.
                self._report(e)
                self._dirty.clear()
            except Exception as e:
                self._failures += 1
                self._report(e)
                backoff = min(self.max_backoff, 2 ** min(self._failures, 10))
                # Leave _dirty set so the write is not forgotten during backoff.
                self._dirty.set()
                if self._stop.wait(backoff):
                    return


# --------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("setup")
    p.add_argument("repo")
    p.add_argument("url")
    p.add_argument("--name", default="backup")

    p = sub.add_parser("push")
    p.add_argument("repo")
    p.add_argument("--name", default="backup")
    p.add_argument("--force-prune", action="store_true")

    p = sub.add_parser("bundle")
    p.add_argument("repo")
    p.add_argument("dir")
    p.add_argument("--keep", type=int, default=7)

    p = sub.add_parser("status")
    p.add_argument("repo")

    p = sub.add_parser("daemon")
    p.add_argument("repo")
    p.add_argument("--name", default="backup")
    p.add_argument("--debounce", type=float, default=5.0)
    p.add_argument("--min-interval", type=float, default=60.0)

    p = sub.add_parser("restore")
    p.add_argument("source")
    p.add_argument("dest")

    a = ap.parse_args()

    if a.cmd == "setup":
        setup(a.repo, a.url, a.name)
    elif a.cmd == "push":
        try:
            print(json.dumps(push(a.repo, a.name, a.force_prune), indent=2))
        except (PushRejected, PruneGuard) as e:
            print(f"{type(e).__name__}: {e}", file=sys.stderr)
            return 1
    elif a.cmd == "bundle":
        print(bundle(a.repo, a.dir, a.keep))
    elif a.cmd == "status":
        print(json.dumps(Syncer(a.repo).status(), indent=2))
    elif a.cmd == "restore":
        restore(a.source, a.dest)
    elif a.cmd == "daemon":
        s = Syncer(a.repo, a.name, a.debounce, a.min_interval).start()
        print(
            f"syncing {a.repo} -> {a.name} "
            f"(debounce {a.debounce}s, min interval {a.min_interval}s)"
        )
        try:
            while True:
                s.notify()  # a standalone daemon cannot see writes, so
                time.sleep(a.min_interval)  # it just pushes on a fixed cadence
        except KeyboardInterrupt:
            s.stop(final_push=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
