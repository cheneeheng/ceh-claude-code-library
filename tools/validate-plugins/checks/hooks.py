"""hooks: every script a hooks.json runs has fixtures here. Each fixture pipes a hand-built payload
into the script and checks its exit code and output. No model call."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from common import REPO, fail, main, plugin_dirs, rel

HOOK_SCRIPT_PAT = re.compile(r"/scripts/([\w.-]+)")


def hook_fixtures(tmp: Path) -> list[dict]:
    """Build the files the fixtures read, then return one dict per fixture.

    Keys: script, stdin (dict), env, args, repeat (runs on one session; the last is checked),
    code (exit code), out (substring of stdout; "" means stdout must be empty), err (substring
    of stderr), before (called just before the script), after (called just after it; returns an
    error message or None). Fixtures run in list order, so a sequence can share one tmp repo.
    """
    big, small = tmp / "big.txt", tmp / "small.txt"
    big.write_text("x\n" * 400, encoding="utf-8")
    small.write_text("x\n" * 5, encoding="utf-8")
    big_p, small_p = big.as_posix(), small.as_posix()

    repos = {}
    for branch in ("main", "feat/x"):
        repo = tmp / branch.replace("/", "-")
        repo.mkdir()
        git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run([*git, "init", "-q", "-b", branch], check=True)
        subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "x"], check=True)
        repos[branch] = (repo / "f.txt").as_posix()

    now_ms = time.time() * 1000
    for name, pct in (("home-95", 95), ("home-50", 50)):
        sl = tmp / name / ".claude" / "statusline" / "p"
        sl.mkdir(parents=True)
        record = {
            "ts": now_ms,
            "data": {"rate_limits": {"five_hour": {"used_percentage": pct}}},
        }
        (sl / "s.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")
    (tmp / "home-empty").mkdir()

    def home(name: str) -> dict:
        h = str(tmp / name)
        return {"HOME": h, "USERPROFILE": h}

    def edit(path: str, cwd: str | None = None) -> dict:
        # The session's cwd defaults to the file's own repo.
        cwd = cwd or str(Path(path).parent)
        return {"tool_name": "Edit", "tool_input": {"file_path": path}, "cwd": cwd}

    def read(path: str, **extra) -> dict:
        return {"tool_name": "Read", "tool_input": {"file_path": path, **extra}}

    def bash(cmd: str) -> dict:
        return {"tool_name": "Bash", "tool_input": {"command": cmd}}

    bulk = {"BULK_READER_MIN_LINES": "350"}
    any_tool = {"tool_name": "Read", "tool_input": {}, "transcript_path": "t.jsonl"}

    # build-record-guard: a plan file, and transcripts with and without implement-from-plan started.
    built = "- 2026-10-26 Built Phase 1: check, 1 passed\n"
    plans = tmp / "product" / "plans"
    plans.mkdir(parents=True)
    plan = plans / "p.md"
    plan.write_text("## Record\n\n" + built, encoding="utf-8")
    plan_p = plan.as_posix()
    tx = {}
    for name, line in (
        ("none", '{"type":"user","message":{"content":"implement-from-plan, later"}}'),
        (
            "skill",
            '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"ceh-build-from-plan:implement-from-plan"}}]}}',
        ),
        (
            "slash",
            '{"type":"user","message":{"content":"<command-name>/ceh-build-from-plan:implement-from-plan</command-name>"}}',
        ),
    ):
        (tmp / f"tx-{name}.jsonl").write_text(line + "\n", encoding="utf-8")
        tx[name] = (tmp / f"tx-{name}.jsonl").as_posix()

    def record(tool: str, ti: dict, t: str = "none") -> dict:
        return {
            "tool_name": tool,
            "tool_input": {"file_path": plan_p, **ti},
            "transcript_path": tx[t],
        }

    add_built = {"old_string": "## Record\n", "new_string": "## Record\n" + built}

    # sync-agents-workspace: a project whose workspace repo is on branch ws, and a linked worktree.
    proj, wt = tmp / "proj", tmp / "wt"
    ws, wt_ws = proj / ".agents_workspace", wt / ".agents_workspace"
    who = {
        f"GIT_{r}_{k}": v
        for r in ("AUTHOR", "COMMITTER")
        for k, v in (("NAME", "t"), ("EMAIL", "t@t"))
    }

    def g(cwd: Path, *args: str) -> str:
        r = subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                           capture_output=True, text=True)  # fmt: skip
        return r.stdout.strip()

    proj.mkdir()
    (proj / ".gitignore").write_text(".agents_workspace\n", encoding="utf-8")
    for d, branch in ((proj, "main"), (ws, "ws")):
        d.mkdir(exist_ok=True)
        if d == ws:
            (ws / "DECISION_LOG.md").write_text("# Log\n", encoding="utf-8")
        g(d, "init", "-q", "-b", branch)
        g(d, "add", ".")
        g(d, "commit", "-q", "-m", "x")
    g(proj, "worktree", "add", "-q", "-b", "feat", str(wt))

    def sync(event: str, cwd: Path | None, **extra) -> dict:
        stdin = {"cwd": str(cwd)} if cwd else {}
        return {
            "script": "sync-agents-workspace.py",
            "args": [event],
            "stdin": stdin,
            "env": who,
            **extra,
        }

    def on_ws_branch() -> str | None:
        got = g(wt_ws, "branch", "--show-current") if wt_ws.is_dir() else "no folder"
        return (
            None
            if got == "ceh-ws/ws/wt"
            else f"wt/.agents_workspace: expected ceh-ws/ws/wt, got {got!r}"
        )

    def append(repo: Path, line: str) -> None:
        with open(repo / "DECISION_LOG.md", "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def main_appends() -> None:
        # The main checkout commits m1 and leaves m2 uncommitted, as a live session would.
        append(ws, "m1")
        g(ws, "commit", "-q", "-am", "m1")
        append(ws, "m2")

    def merging(repo: Path) -> bool:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "-q", "--verify", "MERGE_HEAD"],
                              capture_output=True).returncode == 0  # fmt: skip

    def settled(*lines: str) -> str | None:
        """Wait up to 20 s for the detached end worker: every line in the main log, and the
        main workspace idle (no merge, no autostash held, no index lock)."""
        deadline = time.time() + 20
        while True:
            log = set((ws / "DECISION_LOG.md").read_text(encoding="utf-8").split())
            busy = [
                f
                for f in ("MERGE_HEAD", "MERGE_AUTOSTASH", "index.lock")
                if (ws / ".git" / f).exists()
            ]
            if set(lines) <= log and not busy:
                return None
            if time.time() > deadline:
                return f"after 20 s, main log {sorted(log)}, still present: {busy}"
            time.sleep(0.2)

    def merged_with_dirty_log() -> str | None:
        if problem := settled("w1", "m1", "m2"):
            return problem
        if "DECISION_LOG.md" not in g(ws, "status", "--porcelain"):
            return "m2 should stay uncommitted"
        return None

    wt2 = tmp / "wt2"

    def commit_v1() -> None:
        append(wt2 / ".agents_workspace", "v1")
        g(wt2 / ".agents_workspace", "commit", "-q", "-am", "v1")

    def caught_up_at_end() -> str | None:
        if problem := settled("v1", "m2"):
            return problem
        return (
            None
            if (ws / "notes.txt").read_text(encoding="utf-8") == "m"
            else "notes.txt changed"
        )

    def both_edit_notes() -> None:
        for repo, text in ((wt_ws, "w"), (ws, "m")):
            (repo / "notes.txt").write_text(text, encoding="utf-8")
            g(repo, "add", "notes.txt")
            g(repo, "commit", "-q", "-m", "notes")

    def conflict_aborted() -> str | None:
        if merging(ws) or (ws / "notes.txt").read_text(encoding="utf-8") != "m":
            return (
                "a failed merge should be aborted, leaving the main notes.txt as it was"
            )
        return (
            None
            if "m2" in (ws / "DECISION_LOG.md").read_text(encoding="utf-8")
            else "m2 lost"
        )

    return [
        # branch-guard: deny on the session repo's default branch, allow elsewhere, in another
        # repo, or when switched off.
        {"script": "branch-guard.py", "stdin": edit(repos["main"]), "out": "On the default branch"},
        {"script": "branch-guard.py", "stdin": edit(repos["feat/x"]), "out": ""},
        {"script": "branch-guard.py", "stdin": edit(repos["main"], str(tmp / "feat-x")), "out": ""},
        {"script": "branch-guard.py", "stdin": edit(repos["main"], str(tmp)), "out": ""},
        {"script": "branch-guard.py", "stdin": edit(repos["main"]), "env": {"CEH_BRANCH_GUARD": "off"}, "out": ""},
        {"script": "branch-guard.py", "stdin": edit(repos["main"]), "env": {"CEH_DISABLED_HOOKS": "x, branch-guard"}, "out": ""},
        {"script": "branch-guard.py", "stdin": edit(repos["main"]), "repeat": 4, "out": "denial 4"},
        # bulk-read-guard: whole reads of a large file only, and only when opted in.
        {"script": "bulk-read-guard.py", "stdin": read(big_p), "env": bulk, "out": "Blocked:"},
        {"script": "bulk-read-guard.py", "stdin": read(big_p, limit=20), "env": bulk, "out": ""},
        {"script": "bulk-read-guard.py", "stdin": read(small_p), "env": bulk, "out": ""},
        {"script": "bulk-read-guard.py", "stdin": read(big_p), "out": ""},
        {"script": "bulk-read-guard.py", "stdin": read(big_p), "env": {**bulk, "CEH_DISABLED_HOOKS": "bulk-read-guard"}, "out": ""},
        {"script": "bulk-read-guard.py", "stdin": read(big_p), "env": bulk, "repeat": 4, "out": "denial 4"},
        # bulk-read-bash-guard: dumps are denied, narrowed commands pass.
        {"script": "bulk-read-bash-guard.py", "stdin": bash(f"cat {big_p}"), "env": bulk, "out": "Blocked:"},
        {"script": "bulk-read-bash-guard.py", "stdin": bash(f"cat {big_p} | grep x"), "env": bulk, "out": ""},
        {"script": "bulk-read-bash-guard.py", "stdin": bash(f"head -n 5 {big_p}"), "env": bulk, "out": ""},
        {"script": "bulk-read-bash-guard.py", "stdin": bash(f"tail -n +2 {big_p}"), "env": bulk, "out": "Blocked:"},
        {"script": "bulk-read-bash-guard.py", "stdin": bash(f"cat {big_p}"), "env": bulk, "repeat": 4, "out": "denial 4"},
        # usage-limit-watch: warn with no sensor, block over the threshold, quiet under it.
        {"script": "usage-limit-watch.py", "stdin": any_tool, "env": home("home-empty"), "code": 1, "err": "INACTIVE"},
        {"script": "usage-limit-watch.py", "stdin": any_tool, "env": home("home-95"), "code": 2, "err": "usage-limit-handoff"},
        {"script": "usage-limit-watch.py", "stdin": any_tool, "env": home("home-50"), "out": ""},
        {"script": "usage-limit-watch.py", "stdin": any_tool, "env": {**home("home-empty"), "CEH_DISABLED_HOOKS": "usage-limit-watch"}, "out": ""},
        # ask-user-question-guard: deny the dialog, pass other tools and when switched off.
        {"script": "ask-user-question-guard.py", "stdin": {"tool_name": "AskUserQuestion", "tool_input": {}}, "out": "decision block"},
        {"script": "ask-user-question-guard.py", "stdin": read(small_p), "out": ""},
        # build-record-guard: a new Built Phase line needs implement-from-plan started this session.
        {"script": "build-record-guard.py", "stdin": record("Edit", add_built), "out": "implement-from-plan"},
        {"script": "build-record-guard.py", "stdin": record("Edit", add_built, "skill"), "out": ""},
        {"script": "build-record-guard.py", "stdin": record("Edit", add_built, "slash"), "out": ""},
        {"script": "build-record-guard.py", "stdin": record("Edit", {"old_string": "a", "new_string": "- 2026-10-26 PR: #1 x"}), "out": ""},
        {"script": "build-record-guard.py", "stdin": {**record("Edit", add_built), "tool_input": {"file_path": small_p, **add_built}}, "out": ""},
        {"script": "build-record-guard.py", "stdin": record("Write", {"content": "## Record\n\n" + built + "- x\n"}), "out": ""},
        {"script": "build-record-guard.py", "stdin": record("MultiEdit", {"edits": [{"old_string": built, "new_string": built + "- x\n"}]}), "out": ""},
        {"script": "build-record-guard.py", "stdin": record("Edit", add_built), "env": {"CEH_BUILD_RECORD_GUARD": "off"}, "out": ""},
        {"script": "build-record-guard.py", "stdin": record("Edit", add_built), "env": {"CEH_DISABLED_HOOKS": "build-record-guard"}, "out": ""},
        {"script": "ask-user-question-guard.py", "stdin": {"tool_name": "AskUserQuestion", "tool_input": {}}, "env": {"CEH_DISABLED_HOOKS": "ask-user-question-guard"}, "out": ""},
        # sync-agents-workspace: one sequence on the tmp project above, in this order.
        {**sync("start", wt), "env": {**who, "CEH_DISABLED_HOOKS": "sync-agents-workspace"}, "out": "",
         "after": lambda: "created despite the kill switch" if os.path.lexists(wt_ws) else None},
        {**sync("start", wt), "out": "", "after": on_ws_branch},
        {**sync("commit", wt), "out": "", "before": lambda: append(wt_ws, "w1"),
         "after": lambda: None if g(wt_ws, "log", "-1", "--format=%s") == "ceh-ws: wt" else "no ceh-ws commit"},
        {**sync("end", wt), "out": "", "before": main_appends, "after": merged_with_dirty_log},
        {**sync("start", proj), "out": "ceh-ws/ws/wt", "before": both_edit_notes, "after": conflict_aborted},
        {**sync("start", wt), "out": "", "before": lambda: shutil.rmtree(wt_ws), "after": on_ws_branch},
        # EnterWorktree mid-session: PostToolUse runs start with the worktree as cwd.
        {**sync("start", wt2), "stdin": {"tool_name": "EnterWorktree", "tool_input": {}, "cwd": str(wt2)}, "out": "",
         "before": lambda: g(proj, "worktree", "add", "-q", "-b", "feat2", str(wt2)),
         "after": lambda: None if g(wt2 / ".agents_workspace", "branch", "--show-current") == "ceh-ws/ws/wt2" else "no wt2 workspace"},
        # A session that ends in the main checkout catches up: wt2 merges, wt's conflict aborts.
        {**sync("end", proj), "out": "", "before": commit_v1, "after": caught_up_at_end},
        {**sync("start", None), "out": ""},
        # Context injectors: valid JSON naming their skill, silent when switched off.
        {"script": "load-contract.sh", "stdin": {}, "out": "ceh-coding-conduct:agent-coding-contract"},
        {"script": "load-contract.sh", "stdin": {}, "args": ["SubagentStart"], "out": '"hookEventName": "SubagentStart"'},
        {"script": "load-contract.sh", "stdin": {}, "env": {"CEH_DISABLED_HOOKS": "load-contract"}, "out": ""},
        {"script": "inject-less-code-reminder.sh", "stdin": {}, "out": "WRITE LESS CODE"},
        {"script": "inject-less-code-reminder.sh", "stdin": {}, "env": {"CEH_DISABLED_HOOKS": "inject-less-code-reminder"}, "out": ""},
    ]  # fmt: skip


def check() -> None:
    scripts: dict[str, Path] = {}
    for d in plugin_dirs():
        hooks = d / "hooks" / "hooks.json"
        if hooks.is_file():
            for name in HOOK_SCRIPT_PAT.findall(hooks.read_text(encoding="utf-8")):
                scripts[name] = d / "scripts" / name

    # The full path, not "bash": Windows CreateProcess searches System32 first and finds WSL's
    # bash.exe, which does not pass the fixture's environment variables through.
    bash = shutil.which("bash")
    # The developer's own CEH_* and BULK_READER_* settings must not change a fixture's result.
    base_env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("CEH_", "BULK_READER_"))
    }
    # A detached hook worker may still hold a file when the fixtures end, and Windows refuses to
    # delete it: report the fixture, not a cleanup traceback.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        tmp = Path(tmp_dir)
        state = tmp / "state"  # denial counters and warn-once markers land here
        state.mkdir()
        base_env.update({"TMP": str(state), "TEMP": str(state), "TMPDIR": str(state)})
        fixtures = hook_fixtures(tmp)

        for name in sorted(set(scripts) - {f["script"] for f in fixtures}):
            fail(
                rel(scripts[name]),
                "hook script has no fixture in checks/hooks.py hook_fixtures()",
            )

        for i, f in enumerate(fixtures):
            script = scripts.get(f["script"])
            where = f"hook fixture {i} ({f['script']})"
            if script is None:
                fail(where, "no hooks.json runs this script")
                continue
            if script.suffix == ".sh" and not bash:
                continue
            # -I -S as in hooks.json, so a script that needs site-packages fails here too.
            cmd = [sys.executable, "-I", "-S"] if script.suffix == ".py" else [bash]
            stdin = json.dumps({"session_id": f"fixture-{i}", **f["stdin"]})
            env = {**base_env, **f.get("env", {})}
            if "before" in f:
                f["before"]()
            for _ in range(f.get("repeat", 1)):
                r = subprocess.run(
                    # cwd=REPO + POSIX-relative path so Git Bash on Windows resolves it.
                    [*cmd, rel(script), *f.get("args", [])],
                    cwd=REPO,
                    input=stdin,
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=30,
                )
            if r.returncode != f.get("code", 0):
                fail(
                    where,
                    f"exit {r.returncode}, expected {f.get('code', 0)}: {r.stderr.strip()}",
                )
            if f.get("out") == "" and r.stdout.strip():
                fail(where, f"expected no output, got: {r.stdout.strip()[:200]}")
            elif f.get("out") and f["out"] not in r.stdout:
                fail(where, f"stdout lacks {f['out']!r}: {r.stdout.strip()[:200]}")
            if f.get("err") and f["err"] not in r.stderr:
                fail(where, f"stderr lacks {f['err']!r}: {r.stderr.strip()[:200]}")
            if "after" in f and (problem := f["after"]()):
                fail(where, problem)
            if r.stdout.strip():
                try:
                    json.loads(r.stdout)
                except ValueError:
                    fail(where, f"stdout is not valid JSON: {r.stdout.strip()[:200]}")


if __name__ == "__main__":
    sys.exit(main(check))
