#!/usr/bin/env python3
"""SessionStart, PreToolUse (Bash), PostToolUse (EnterWorktree), Stop and SessionEnd hook: give a linked git
worktree its own worktree of the main checkout's .agents_workspace repo, and merge it back.

Claude Code's worktree isolation refuses Edit and Write through a link to the main checkout, so
the worktree gets a real git worktree of the workspace repo instead, at
<worktree>/.agents_workspace, on the branch ceh-ws/<X>/<worktree folder>, where <X> is the
branch the main workspace has checked out.

Arguments, one per event:
  start   in a linked worktree, create its workspace; in a main checkout, catch up: merge every
          ceh-ws/<X>/ branch not yet merged, and report each merge that failed.
  commit  commit the worktree's workspace changes, so a removed worktree loses nothing committed.
          Check pending source PR merges and commit their workspace checkpoints first.
  merge   record a gh pr merge command as pending, without calling gh or changing the command.
  end     start end-worker detached and return, because the SessionEnd budget (1.5 s, which a
          plugin cannot raise) can kill a merge in progress.
  end-worker <cwd>
          in a linked worktree, commit, then merge its branch into <X>; in a main checkout,
          catch up, since Claude Code may report the main checkout as cwd when a session ends.

Reads cwd from the hook payload (end-worker: from argv), never os.getcwd(), and does nothing
without it. Fails open: anything unexpected exits 0. Checkpoint lookup and commit failures print
one systemMessage per session and reason, because a convenience hook must never stop a session.
"""

import datetime as dt
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WORKSPACE = ".agents_workspace"
PREFIX = "ceh-ws/"
# DECISION_LOG.md merge=union: two sessions appending to the log keep both sides' lines.
UNION = Path(__file__).resolve().parent / "union.attributes"
# Words that may stand before a command in its segment without changing which command runs.
SHELL_WORDS = {"if", "then", "elif", "else", "do", "while", "until", "!", "{", "time"}


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


def pending_name(reference):
    if reference.isdigit():
        return f"pr-{reference}"
    return "branch-" + hashlib.sha256(reference.encode()).hexdigest()


def record_merge(top, main_ws, command):
    # less-code: simple shell segments; use a shell parser if nested shell syntax is required.
    parts = re.split(r"""('[^']*'|"(?:\\.|[^"\\])*"|\\.|[;&|()\n]+)""", command)
    segment = ""
    for part in [*parts, ";"]:
        if re.fullmatch(r"[;&|()\n]+", part):
            tokens = shlex.split(segment, comments=True)
            segment = ""
            # `then gh pr merge` and `GH_PAGER= gh pr merge` still run the merge.
            while tokens and (
                tokens[0] in SHELL_WORDS
                or re.fullmatch(r"[A-Za-z_]\w*=.*", tokens[0], re.S)
            ):
                del tokens[0]
            if tokens[:3] == ["gh", "pr", "merge"]:
                tokens = tokens[3:]
                break
        else:
            segment += part
    else:
        return
    if any(
        t == "-R" or t.startswith("-R") or t == "--repo" or t.startswith("--repo=")
        for t in tokens
    ):
        return
    values = {
        "-b",
        "--body",
        "-F",
        "--body-file",
        "-t",
        "--subject",
        "-A",
        "--author-email",
        "--match-head-commit",
    }
    reference = ""
    skip = False
    for token in tokens:
        if skip:
            skip = False
        elif token in values:
            skip = True
        elif not token.startswith("-"):
            reference = token
            break
    reference = reference or current_branch(top)
    url = re.fullmatch(r"https?://[^/]+/[^/]+/[^/]+/pull/(\d+)/?", reference)
    if url:
        reference = url[1]
    if not reference or "\n" in reference or "\r" in reference:
        return
    folder = main_ws / ".git" / "ceh-checkpoint-pending"
    folder.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=folder, prefix=".pending-", delete=False
    ) as stream:
        stream.write(f"{top.as_posix()}\n{reference}\n")
        temporary = Path(stream.name)
    try:
        os.replace(temporary, folder / pending_name(reference))
    finally:
        temporary.unlink(missing_ok=True)


def checkpoint_warning(session, reference, reason, folder):
    key = hashlib.sha1(f"{session}\n{reason}".encode()).hexdigest()[:16]
    marker = Path(tempfile.gettempdir()) / f"ceh-checkpoint-warning-{key}"
    try:
        marker.touch(exist_ok=False)
    except FileExistsError:
        return
    print(
        json.dumps(
            {
                "systemMessage": f"Workspace checkpoint for {reference} is pending: {reason}. Pending folder: {folder}"
            }
        )
    )


def checkpoints(top, main_ws, x, folder, session, linked):
    repo = workspace_repo(top) if linked else main_ws
    if not repo or (linked and current_branch(repo) != f"{PREFIX}{x}/{top.name}"):
        return
    code, directory = git(repo, "rev-parse", "--absolute-git-dir")
    if code or any(
        (Path(directory) / name).exists()
        for name in ("MERGE_HEAD", "MERGE_AUTOSTASH", "index.lock")
    ):
        return
    deadline = time.monotonic() + 12
    gh = shutil.which("gh")
    claims = []
    merged = {}
    merged_claims = []
    try:
        for entry in sorted(folder.iterdir()):
            if not entry.name.startswith(("pr-", "branch-")):
                continue
            try:
                stamp = entry.stat().st_mtime
                if time.time() - stamp > 14 * 86400:
                    entry.unlink(missing_ok=True)
                    continue
                owner, reference = entry.read_text(encoding="utf-8").splitlines()
                if entry.name != pending_name(reference):
                    continue  # A live claim belongs to another Stop. Crashed claims expire above.
                if not same(owner, top):
                    if linked or Path(owner).exists():
                        continue
                    code, unmerged = git(
                        main_ws,
                        "for-each-ref",
                        "--no-merged=HEAD",
                        f"refs/heads/{PREFIX}{x}/{Path(owner).name}",
                    )
                    if code or unmerged:
                        continue
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                claim = entry.with_name(
                    f"{entry.name}.{re.sub(r'[^A-Za-z0-9_-]', '_', session)}"
                )
                os.replace(entry, claim)
            except FileNotFoundError:
                continue  # Another Stop claimed or removed this entry first.
            claims.append((entry, claim))
            try:
                if not gh:
                    raise ValueError("gh is not available")
                result = subprocess.run(
                    [
                        gh,
                        "pr",
                        "view",
                        reference,
                        "--json",
                        "state,number,url,mergeCommit,mergedAt",
                    ],
                    cwd=top,
                    capture_output=True,
                    text=True,
                    timeout=remaining,
                )
                if result.returncode:
                    raise ValueError("gh pr view failed")
                data = json.loads(result.stdout)
                if not isinstance(data, dict):
                    raise ValueError("gh returned no PR object")
                state = data["state"]
                if state == "CLOSED":
                    claim.unlink()
                elif state == "MERGED":
                    timestamp = data["mergedAt"]
                    if not isinstance(timestamp, str):
                        raise ValueError("gh returned no merge time")
                    when = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    if when.tzinfo is None:
                        raise ValueError("gh returned a merge time without a timezone")
                    if when.timestamp() < stamp - 60:
                        claim.unlink()
                        continue
                    number, url, oid = (
                        data["number"],
                        data["url"],
                        data["mergeCommit"]["oid"],
                    )
                    if (
                        type(number) is not int
                        or number < 1
                        or not isinstance(url, str)
                        or not url
                        or not isinstance(oid, str)
                        or not oid
                    ):
                        raise ValueError("gh returned incomplete merge details")
                    body = f"{url} merged as {oid}"
                    code, existing = git(
                        repo,
                        "log",
                        "--all",
                        "-1",
                        "--format=%H",
                        "--fixed-strings",
                        f"--grep={body}",
                    )
                    if code:
                        checkpoint_warning(
                            session,
                            reference,
                            "git checkpoint history lookup failed",
                            folder,
                        )
                        continue
                    if existing:
                        claim.unlink()
                        continue
                    merged[number] = body
                    merged_claims.append(claim)
                elif state != "OPEN":
                    raise ValueError("gh returned an unknown PR state")
            except (
                OSError,
                subprocess.TimeoutExpired,
                ValueError,
                KeyError,
                TypeError,
            ):
                checkpoint_warning(
                    session,
                    reference,
                    "gh is not available"
                    if not gh
                    else "gh pr view failed or returned invalid merge details",
                    folder,
                )
        if merged:
            numbers = sorted(merged)
            subject = (
                f"chore(workspace): checkpoint source pr #{numbers[0]}"
                if len(numbers) == 1
                else "chore(workspace): checkpoint source prs "
                + ", ".join(f"#{n}" for n in numbers)
            )
            if len(subject) > 72:
                subject = f"chore(workspace): checkpoint {len(numbers)} source prs"
            try:
                failed = (
                    git(repo, "add", "-A")[0]
                    or git(
                        repo,
                        "commit",
                        "-q",
                        "--allow-empty",
                        "-m",
                        subject,
                        "-m",
                        "\n".join(merged[n] for n in numbers),
                    )[0]
                )
            except (OSError, subprocess.TimeoutExpired):
                failed = True
            if failed:
                checkpoint_warning(
                    session,
                    ", ".join(f"#{n}" for n in numbers),
                    "git checkpoint commit failed",
                    folder,
                )
            else:
                for claim in merged_claims:
                    claim.unlink()
    finally:
        for entry, claim in claims:
            if claim.exists():
                try:
                    os.link(
                        claim, entry
                    )  # Preserve a newer merge event at entry, if one arrived.
                except FileExistsError:
                    pass
                claim.unlink()


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
    git(path, "commit", "-q", "-m", f"chore(workspace): sync worktree {top.name}"[:72])


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
    # A concurrent end-worker may have merged a branch whose merge lost the index lock here.
    _, still = git(main_ws, "for-each-ref", fmt, "--no-merged=HEAD", ref)
    failed = [b for b in failed if b in still.splitlines()]
    _, merged = git(main_ws, "for-each-ref", fmt, "--merged=HEAD", ref)
    for b in merged.splitlines():
        git(
            main_ws, "branch", "-q", "-d", b
        )  # git refuses while a worktree has it checked out
    return failed


def detach(cwd, run_in):
    """Start `end-worker <cwd>` in its own process group, so it outlives the hook."""
    args = [sys.executable, "-I", "-S", os.path.abspath(__file__), "end-worker", cwd]
    # The worker runs in the main checkout, so it never holds the worktree folder open.
    io = dict(
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(run_in),
    )
    if os.name != "nt":
        subprocess.Popen(args, start_new_session=True, **io)
        return
    # CREATE_NO_WINDOW, not DETACHED_PROCESS: its git.exe children share one hidden console
    # instead of flashing a window each.
    flags = subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP
    try:
        subprocess.Popen(
            args, creationflags=flags | subprocess.CREATE_BREAKAWAY_FROM_JOB, **io
        )
    except (
        OSError
    ):  # the job forbids breakaway; the next session start's catch-up still merges
        subprocess.Popen(args, creationflags=flags, **io)


def main():
    # Kill switch: CEH_DISABLED_HOOKS lists hook script names to skip.
    disabled = os.environ.get("CEH_DISABLED_HOOKS", "").replace(" ", "").split(",")
    if Path(__file__).stem in disabled:
        return

    event = sys.argv[1] if len(sys.argv) > 1 else ""
    if event == "end-worker":
        cwd = sys.argv[2] if len(sys.argv) > 2 else ""
        payload = {}
    else:
        payload = json.load(sys.stdin) or {}
        cwd = payload.get("cwd")
    command = payload.get("tool_input", {}).get("command", "")
    if event == "merge" and not re.search(r"\bgh\s+pr\s+merge\b", command):
        return  # Runs before every Bash call: no git process without a merge.
    if not cwd or not os.path.isdir(cwd):
        return
    found = checkouts(cwd)
    if not found:
        return
    top, main_checkout = found
    if event == "end":
        detach(cwd, main_checkout or top)
        return
    pending = (main_checkout or top) / WORKSPACE / ".git" / "ceh-checkpoint-pending"
    if (
        not main_checkout
        and event == "commit"
        and (not pending.is_dir() or not any(pending.iterdir()))
    ):
        return  # Stop in a main checkout normally needs only one git spawn.
    main_ws = workspace_repo(main_checkout or top)
    x = current_branch(main_ws) if main_ws else ""
    if not x:  # no workspace repo, or detached: no branch to merge back into
        return

    if event == "merge":
        record_merge(top, main_ws, command)
        return

    if not main_checkout:
        if event == "commit":
            checkpoints(
                top,
                main_ws,
                x,
                pending,
                str(payload.get("session_id") or os.getpid()),
                False,
            )
        elif event == "end-worker":
            catch_up(
                main_ws, x
            )  # SessionEnd output is discarded: the next start reports failures
        elif event == "start" and (failed := catch_up(main_ws, x)):
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
    elif event in ("commit", "end-worker"):
        if event == "commit" and pending.is_dir():
            checkpoints(
                top,
                main_ws,
                x,
                pending,
                str(payload.get("session_id") or os.getpid()),
                True,
            )
        commit(top, branch)
        if event == "end-worker":
            merge(main_ws, branch)


if __name__ == "__main__":
    try:
        main()
    except Exception:  # fail open
        pass
    sys.exit(0)
