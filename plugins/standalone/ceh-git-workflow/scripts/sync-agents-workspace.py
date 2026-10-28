#!/usr/bin/env python3
"""SessionStart, Stop and SessionEnd hook: give a linked git worktree its own worktree of the
main checkout's .agents_workspace repo, and merge it back.

Claude Code's worktree isolation refuses Edit and Write through a link to the main checkout, so
the worktree gets a real git worktree of the workspace repo instead, at
<worktree>/.agents_workspace, on the branch ceh-ws/<X>/<worktree folder>, where <X> is the
branch the main workspace has checked out.

Arguments, one per event:
  start   in a linked worktree, create its workspace; in a main checkout, catch up: merge every
          ceh-ws/<X>/ branch not yet merged, and report each merge that failed.
  commit  commit the worktree's workspace changes, so a removed worktree loses nothing committed.
  end     commit, then merge the worktree's branch into <X>.

Reads cwd from the hook payload, never os.getcwd(), and does nothing without it. Fails open:
anything unexpected exits 0 silently, because a convenience hook must never stop a session.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE = ".agents_workspace"
PREFIX = "ceh-ws/"
# DECISION_LOG.md merge=union: two sessions appending to the log keep both sides' lines.
UNION = Path(__file__).resolve().parent.parent / "assets" / "union.attributes"


def git(cwd, *args):
    out = subprocess.run(
        ["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=10
    )
    return out.returncode, out.stdout.strip()


def same(a, b):
    return os.path.normcase(os.path.normpath(str(a))) == os.path.normcase(
        os.path.normpath(str(b))
    )


def checkouts(cwd):
    """(top level, main checkout) in a linked worktree, (top level, None) in a main checkout,
    None outside git or when the main checkout cannot be found."""
    code, out = git(
        cwd,
        "rev-parse",
        "--path-format=absolute",
        "--show-toplevel",
        "--git-dir",
        "--git-common-dir",
    )
    lines = out.splitlines()
    if code or len(lines) != 3:
        return None
    top, git_dir, common = (Path(p) for p in lines)
    if same(git_dir, common):
        return top, None
    if common.name != ".git":  # bare repo or separate git dir
        return None
    return top, common.parent


def workspace_repo(checkout):
    """<checkout>/.agents_workspace when it is a git repo of its own, else None."""
    ws = checkout / WORKSPACE
    if not ws.is_dir():
        return None
    code, top = git(ws, "rev-parse", "--path-format=absolute", "--show-toplevel")
    return ws if code == 0 and same(top, ws) else None


def current_branch(repo):
    """The checked-out branch, "" when detached or on error."""
    code, out = git(repo, "branch", "--show-current")
    return "" if code else out


def create(top, main_ws, branch):
    """Add <top>/.agents_workspace as a worktree of the main workspace repo."""
    path = top / WORKSPACE
    if os.path.lexists(path):
        return
    git(main_ws, "worktree", "prune")
    code, _ = git(main_ws, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}")
    if code == 0:
        git(main_ws, "worktree", "add", "-q", str(path), branch)
    else:
        git(main_ws, "worktree", "add", "-q", "-b", branch, str(path))


def commit(top, branch):
    """Commit every change in <top>/.agents_workspace when it is on its ceh-ws/ branch."""
    path = top / WORKSPACE
    if not path.is_dir():
        return
    code, out = git(path, "status", "--porcelain", "--branch")
    lines = out.splitlines()
    if code or not lines or lines[0][3:].split("...")[0] != branch or len(lines) == 1:
        return
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", f"ceh-ws: {top.name}")


def merging(repo):
    return git(repo, "rev-parse", "-q", "--verify", "MERGE_HEAD")[0] == 0


def merge(main_ws, branch):
    """Merge branch into the main workspace, uncommitted changes there included. False on failure,
    with any merge this started aborted."""
    if merging(main_ws):  # the user's own merge: never touch it
        return False
    code, _ = git(
        main_ws,
        "-c",
        f"core.attributesFile={UNION}",
        "merge",
        "--autostash",  # git refuses a merge over a dirty file, and the log usually is dirty
        "--no-edit",
        "-q",
        branch,
    )
    if code and merging(main_ws):
        git(main_ws, "merge", "--abort")  # also reapplies the autostash
    return code == 0


def catch_up(main_ws, x):
    """Merge every ceh-ws/<x>/ branch not yet in <x>, delete merged ones no worktree holds, and
    return the branches whose merge failed."""
    git(main_ws, "worktree", "prune")
    ref = f"refs/heads/{PREFIX}{x}/"
    fmt = "--format=%(refname:short)"
    _, pending = git(main_ws, "for-each-ref", fmt, "--no-merged=HEAD", ref)
    failed = [b for b in pending.splitlines() if not merge(main_ws, b)]
    _, merged = git(main_ws, "for-each-ref", fmt, "--merged=HEAD", ref)
    for b in merged.splitlines():
        git(
            main_ws, "branch", "-q", "-d", b
        )  # git refuses while a worktree has it checked out
    return failed


def main():
    # Kill switch: CEH_DISABLED_HOOKS lists hook script names to skip.
    disabled = os.environ.get("CEH_DISABLED_HOOKS", "").replace(" ", "").split(",")
    if Path(__file__).stem in disabled:
        return

    event = sys.argv[1] if len(sys.argv) > 1 else ""
    cwd = (json.load(sys.stdin) or {}).get("cwd")
    if not cwd or not os.path.isdir(cwd):
        return
    found = checkouts(cwd)
    if not found:
        return
    top, main_checkout = found
    if (
        not main_checkout and event != "start"
    ):  # Stop fires every turn: one git spawn here
        return
    main_ws = workspace_repo(main_checkout or top)
    x = current_branch(main_ws) if main_ws else ""
    if not x:  # no workspace repo, or detached: no branch to merge back into
        return

    if not main_checkout:
        if event == "start" and (failed := catch_up(main_ws, x)):
            names = ", ".join(failed)
            note = (
                f"The {WORKSPACE} branches {names} did not merge into {x} on their own "
                f"(a conflict, or a merge git refused). Merge each by hand: "
                f"git -C {WORKSPACE} merge <branch>."
            )
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "SessionStart",
                            "additionalContext": note,
                        }
                    }
                )
            )
        return

    branch = f"{PREFIX}{x}/{top.name}"
    if event == "start":
        create(top, main_ws, branch)
    elif event in ("commit", "end"):
        commit(top, branch)
        if event == "end":
            merge(main_ws, branch)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # fail open
        pass
    sys.exit(0)
