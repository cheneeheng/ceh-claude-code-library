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
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from common import REPO, check_bash, fail, main, plugin_dirs, rel

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
            '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"ceh-build-plan:implement-from-plan"}}]}}',
        ),
        (
            "slash",
            '{"type":"user","message":{"content":"<command-name>/ceh-build-plan:implement-from-plan</command-name>"}}',
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

    # skill-started-guard: a session in tmp/guarded, and transcripts that started one skill.
    guarded = (tmp / "guarded").as_posix()

    def started(skill: str, how: str = "skill") -> str:
        if how == "skill":
            use = {"type": "tool_use", "name": "Skill", "input": {"skill": skill}}
            line = {"type": "assistant", "message": {"content": [use]}}
        else:
            line = {
                "type": "user",
                "message": {"content": f"<command-name>/{skill}</command-name>"},
            }
        p = tmp / f"tx-{how}-{skill.replace(':', '-')}.jsonl"
        p.write_text(json.dumps(line) + "\n", encoding="utf-8")
        return p.as_posix()

    def guard(plugin: str, tool: str, ti: dict, t: str = tx["none"]) -> dict:
        stdin = {
            "tool_name": tool,
            "tool_input": ti,
            "cwd": guarded,
            "transcript_path": t,
        }
        return {"script": f"{plugin}/skill-started-guard.py", "stdin": stdin}

    gw = "ceh-git-workflow"
    commit = {"command": "git commit -m x"}
    changelog = {
        "file_path": f"{guarded}/CHANGELOG.md",
        "old_string": "a",
        "new_string": "b",
    }
    readme = {"file_path": f"{guarded}/docs/README.md", "content": "x"}
    tst = "ceh-testing"
    test_file = {"file_path": f"{guarded}/tests/test_check.py", "content": "x"}

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
            try:
                log = set((ws / "DECISION_LOG.md").read_text(encoding="utf-8").split())
            except (
                FileNotFoundError
            ):  # the worker's merge replaces the file: not settled yet
                log = set()
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

    # artifact-render-hook and generated-md-guard: plan/v2 YAML in tmp/product/plans.
    good_plan = (
        "schema: plan/v2\ntitle: Count words\nstatus: ready\ncreated: 2026-11-06\n"
        "goal: |\n  A CLI that counts words.\nscope:\n  in:\n    - Count the words in a file\n"
        "  out: []\ndesign:\n  - topic: Stack.\n    decision: |\n      Python stdlib.\n"
        "phases:\n  - name: CLI\n    builds: |\n      The counter.\n    check: |\n"
        "      `python wc.py README.md` prints a number.\n    status: todo\nopen: []\n"
        "record:\n  - date: 2026-11-06\n    event: Planned\n    details: status ready\n"
    )
    no_check = good_plan.replace(
        "    check: |\n      `python wc.py README.md` prints a number.\n", ""
    )
    yamls = {
        "ok": good_plan,
        "broken": no_check,
        "dashed": "---\n# a comment first\n" + no_check,
        "no-schema": good_plan.replace("schema: plan/v2\n", ""),
    }
    for name, text in yamls.items():
        (plans / f"{name}.yaml").write_text(text, encoding="utf-8")
    other_yaml = tmp / "config.yaml"
    other_yaml.write_text("key: value\n", encoding="utf-8")
    generated = plans / "gen.md"
    generated.write_text(
        "---\nschema: plan/v2\ngenerated_from: gen.yaml\n---\n", encoding="utf-8"
    )

    def write(name: str) -> dict:
        return {
            "tool_name": "Write",
            "tool_input": {"file_path": (plans / name).as_posix()},
        }

    def rendered(name: str) -> str | None:
        md = plans / f"{name}.md"
        ok = md.is_file() and "generated_from: ok.yaml" in md.read_text(
            encoding="utf-8"
        )
        return None if ok else f"{md.name} was not rendered"

    def not_rendered(name: str):
        return lambda: (
            f"{name}.md was rendered" if (plans / f"{name}.md").exists() else None
        )

    no_uv = {"PATH": str(tmp / "no-uv")}
    have_uv = shutil.which("uv") is not None

    def artifact_fixtures(plugin: str, full: bool) -> list[dict]:
        """The artifact hooks of one plugin. The copies are byte-identical (checks/artifact_models.py),
        so the full set runs once and each other copy runs a smoke test of each path."""
        rh, mg = f"{plugin}/artifact-render-hook.py", f"{plugin}/generated-md-guard.py"
        # Running artifact.py needs uv: skipped without it, as shellcheck is in checks/scripts.py.
        uv = [
            {"script": rh, "stdin": write("ok.yaml"), "out": "", "after": lambda: rendered("ok")},
            {"script": rh, "stdin": write("broken.yaml"), "out": '"decision": "block"', "after": not_rendered("broken")},
        ] + ([
            {"script": rh, "stdin": write("dashed.yaml"), "out": "phases.0.check"},
            {"script": rh, "stdin": write("no-schema.yaml"), "out": "no 'schema:"},
        ] if full else [])  # fmt: skip
        smoke = [
            {
                "script": rh,
                "stdin": write("broken.yaml"),
                "env": no_uv,
                "out": "uv is not installed",
            },
            {"script": mg, "stdin": edit(generated.as_posix()), "out": "gen.yaml"},
            {"script": mg, "stdin": edit(plan_p), "out": ""},
        ]
        rest = [
            {"script": rh, "stdin": {"tool_name": "Write", "tool_input": {"file_path": other_yaml.as_posix()}}, "env": no_uv, "out": ""},
            {"script": rh, "stdin": write("p.md"), "env": no_uv, "out": ""},
            {"script": rh, "stdin": write("broken.yaml"), "env": no_uv, "repeat": 2, "out": ""},
            {"script": rh, "stdin": write("broken.yaml"), "env": {**no_uv, "CEH_ARTIFACT_CHECK": "off"}, "out": ""},
            {"script": rh, "stdin": write("broken.yaml"), "env": {**no_uv, "CEH_DISABLED_HOOKS": "artifact-render-hook"}, "out": ""},
            {"script": mg, "stdin": edit(generated.as_posix()), "out": "Edit "},
            {"script": mg, "stdin": edit(generated.as_posix()), "env": {"CEH_ARTIFACT_CHECK": "off"}, "out": ""},
            {"script": mg, "stdin": edit(generated.as_posix()), "env": {"CEH_DISABLED_HOOKS": "generated-md-guard"}, "out": ""},
        ] if full else []  # fmt: skip
        return (uv if have_uv else []) + smoke + rest

    # evidence/v2 in ceh-testing: each EVIDENCE.yaml in its own product/ folder, since the hook
    # finds a spine file by its stem.
    na = "{status: not run}"
    good_ev = (
        "schema: evidence/v2\nproduct: Demo\nruns:\n  - date: 2026-11-07\n    sha: abc1234\n"
        "    tree: clean\n    areas:\n"
        "      tests: {status: passed, result: 3 passed, checked_at: abc1234}\n"
        f"      qa: {na}\n      performance: {na}\n      security: {na}\n"
        f"      usability: {na}\n      plan: {na}\n"
        "    open_issues: []\n    claims: []\n    not_run:\n"
        + "".join(
            f"      - {{area: {a}, reason: none, skill: x}}\n"
            for a in ("qa", "performance", "security", "usability", "plan")
        )
    )
    stray = tmp / "notes" / "STRATEGY.yaml"
    stray.parent.mkdir(exist_ok=True)
    stray.write_text("key: value\n", encoding="utf-8")

    def write_at(p) -> dict:
        return {"tool_name": "Write", "tool_input": {"file_path": p.as_posix()}}

    def spine_fixtures(
        plugin: str, stem: str, good: str, bad: str, field: str, marker: str
    ) -> list[dict]:
        """One spine format's hooks in the plugin that owns it: render a valid file, block a bad
        one naming `field`, report a missing schema key, leave plan YAML alone, warn without uv."""
        files = {"ok": good, "bad": bad, "no-schema": good.split("\n", 1)[1]}
        at = {}
        for name, text in files.items():
            folder = tmp / f"{stem}-{name}" / "product"
            folder.mkdir(parents=True, exist_ok=True)
            at[name] = folder / f"{stem}.yaml"
            at[name].write_text(text, encoding="utf-8")

        def rendered() -> str | None:
            md = at["ok"].with_suffix(".md")
            ok = md.is_file() and marker in md.read_text(encoding="utf-8")
            return None if ok else f"{stem}.md was not rendered"

        rh = f"{plugin}/artifact-render-hook.py"
        return ([
            {"script": rh, "stdin": write_at(at["ok"]), "out": "", "after": rendered},
            {"script": rh, "stdin": write_at(at["bad"]), "out": field},
            {"script": rh, "stdin": write_at(at["no-schema"]), "out": "no 'schema:"},
            # A plan plugin holds no model of this format, so the file is not its to check.
            {"script": "ceh-check-build-against-plan/artifact-render-hook.py", "stdin": write_at(at["no-schema"]), "out": ""},
        ] if have_uv else []) + [
            {"script": rh, "stdin": write_at(at["bad"]), "env": no_uv, "out": "uv is not installed"},
            {"script": f"{plugin}/generated-md-guard.py", "stdin": edit(generated.as_posix()), "out": "gen.yaml"},
        ]  # fmt: skip

    good_arch = (
        "schema: architecture/v3\noverview:\n  bullets:\n    - It counts words.\n"
        "  flow: |\n    flowchart LR\n        a --> b\ndiagrams: []\nkey_decisions: []\n"
    )
    good_vision = (
        "schema: vision/v2\nstatus: draft\nupdated: 2026-11-07\nidentity:\n  name: Wordy\n"
        "  sentence: a CLI.\n  is:\n    - {trait: Small, meaning: One file.}\n  is_not: [An editor.]\n"
        "vision: Counted. [assumed]\nscope: {text: Text., test: Does it count, refuses: Spelling.}\n"
        "goals:\n  - {goal: Fast, measure: Under a second.}\nnon_goals: []\n"
        "principles:\n  - {name: Simple, rule: Few flags., ask: Can it go}\n"
        "conflicts:\n  order:\n    - {principle: Simple, protects: ease}\n  example: For example, none.\n"
        "gaps: []\nextra_sections: []\nchanging: A PR.\n"
    )
    good_bp = (
        "schema: business-plan/v3\nstatus: draft\ncreated: 2026-11-07\nupdated: 2026-11-07\n"
        "product: Wordy\nstage: idea\nderived_from: []\npmf_gate: 2\nsections:\n"
        + "".join(
            f"  {k}: {{body: '', subsections: []}}\n"
            for k in (
                "executive_summary", "problem", "target_customer", "value_proposition",
                "solution", "alternatives", "market", "business_model", "go_to_market",
                "traction", "financials", "risks", "milestones",
            )
        )
    )  # fmt: skip

    def report_fixtures(
        plugin: str,
        stem: str,
        good: str,
        bad: str,
        field: str,
        marker: str,
        tag: str = "",
    ) -> list[dict]:
        """One report format's render hook: render a valid file, block a bad one naming `field`,
        and skip one with no schema key, since a report is found by its key, not its place. Each
        file is `<stem>.yaml` in its own folder, `report-<tag or stem>/<ok|bad|none>/`."""
        at = {}
        for name, text in {
            "ok": good,
            "bad": bad,
            "none": good.split("\n", 1)[1],
        }.items():
            folder = tmp / f"report-{tag or stem}" / name
            folder.mkdir(parents=True, exist_ok=True)
            at[name] = folder / f"{stem}.yaml"
            at[name].write_text(text, encoding="utf-8")

        def rendered() -> str | None:
            md = at["ok"].with_suffix(".md")
            ok = md.is_file() and marker in md.read_text(encoding="utf-8")
            return None if ok else f"{md.name} was not rendered"

        rh = f"{plugin}/artifact-render-hook.py"
        return [
            {"script": rh, "stdin": write_at(at["ok"]), "out": "", "after": rendered},
            {"script": rh, "stdin": write_at(at["bad"]), "out": field},
            {"script": rh, "stdin": write_at(at["none"]), "out": ""},
        ] if have_uv else []  # fmt: skip

    good_qa = (
        "schema: qa-report/v2\napp: Wordy\ncommit: abc1234\nmode: report\ndate: 2026-11-10 12:04\n"
        "launched_with: {command: wordy, entry: CLI}\ncharters:\n"
        "  - {charter: Explore counting with inputs to find crashes, actions_used: 20, bugs: []}\n"
        "bugs: []\nusability_notes: []\nnot_explored: []\n"
    )
    good_perf = (
        "schema: perf-report/v2\nmetric: search\ncommit: abc1234\ncommand: wordy search\n"
        "machine: laptop\ninput: 10k docs\nunit: ms\nspread: range\nattempts:\n"
        "  - {attempt: baseline, change: abc1234, median: 120, low: 110, high: 130,"
        " within_noise: false, kept: false}\n"
    )
    good_sec = (
        "schema: security-audit/v2\nrepo: wordy\ncommit: abc1234\ndate: 2026-11-10\n"
        "attack_surface: |\n  One CLI entry point.\nfindings:\n"
        "  - {severity: high, confidence: confirmed, category: Injection, attacker: local user,"
        " location: 'wordy.py:12', attack: Shell from a file name, fix: Pass a list}\n"
        "possible: []\nnot_checked: []\n"
    )
    sec = "ceh-security-audit"
    security_fixtures = [
        *report_fixtures(sec, "SECURITY_AUDIT", good_sec, good_sec.replace("severity: high", "severity: severe"), "findings.0.severity", "# Security audit: wordy"),
        # report_fixtures writes its files with or without uv.
        {"script": f"{sec}/artifact-render-hook.py", "stdin": write_at(tmp / "report-SECURITY_AUDIT" / "bad" / "SECURITY_AUDIT.yaml"), "env": no_uv, "out": "uv is not installed"},
        # ceh-security-audit holds no plan model, so a plan YAML is not its to check.
        {"script": f"{sec}/artifact-render-hook.py", "stdin": write("broken.yaml"), "env": no_uv, "out": ""},
        {"script": f"{sec}/generated-md-guard.py", "stdin": edit(generated.as_posix()), "out": "gen.yaml"},
    ]  # fmt: skip
    # The three usability audits. Two share the name UX_AUDIT.yaml, and a missing commit is
    # blocked under each schema.
    good_fr = (
        "schema: first-run-audit/v2\ntarget: wordy\nrun: 7\ndate: 2026-11-10\ncommit: abc1234\n"
        "goal: Count words\nmilestones:\n  - {name: M1, budget: 5}\naudience: A terminal user.\n"
        "frozen_set: The README.\nwalkers: {run: [Novice], skipped: [], mode: serially}\n"
        "gate: {score: 4, out_of: 5, na: 0}\nresults: []\nminutes: 5\nfindings: []\n"
        "hypotheses: []\nnot_covered: []\n"
    )
    good_ia = (
        "schema: interface-audit/v2\ntarget: wordy\nsurface: CLI\nrun: 7\ndate: 2026-11-10\n"
        "commit: abc1234\ngoals:\n  - {goal: Count words, budget: 5}\naudience: A terminal user.\n"
        "allowlist: The help text.\nwalkers: {run: [Novice], skipped: []}\n"
        "gate: {score: 4, out_of: 4, na: 1}\nfive_questions: []\nfindings: []\nhypotheses: []\n"
        "delegated: []\nnot_covered: []\n"
    )
    good_em = (
        "schema: error-messages-audit/v2\ntarget: wordy\nrun: 7\ndate: 2026-11-10\n"
        "commit: abc1234\nharvested: 2\nalready_complete: 1\nrows: []\nsystemic: []\n"
    )
    ux = "ceh-usability-audit"

    def no_commit(text: str) -> str:
        return text.replace("commit: abc1234\n", "")

    usability_fixtures = [
        *report_fixtures(ux, "UX_AUDIT", good_fr, no_commit(good_fr), "commit", "**Gate:** 4/5", "first-run"),
        *report_fixtures(ux, "UX_AUDIT", good_ia, no_commit(good_ia), "commit", "**Gate:** 4/4, 1 N/A", "interface"),
        *report_fixtures(ux, "ERROR_MESSAGES", good_em, good_em.replace("already_complete: 1", "already_complete: 3"), "already_complete", "run 007"),
        {"script": f"{ux}/artifact-render-hook.py", "stdin": write_at(tmp / "report-first-run" / "bad" / "UX_AUDIT.yaml"), "env": no_uv, "out": "uv is not installed"},
        {"script": f"{ux}/artifact-render-hook.py", "stdin": write("broken.yaml"), "env": no_uv, "out": ""},
        {"script": f"{ux}/generated-md-guard.py", "stdin": edit(generated.as_posix()), "out": "gen.yaml"},
    ]  # fmt: skip
    # The fix record: ceh-coding-conduct writes it and ceh-testing completes it, so both check it.
    good_fix = (
        "schema: fix-record/v2\nstatus: diagnosed\ndate: 2026-11-10\ntitle: Count drops the last word\n"
        "symptom: {command: wordy count a.txt, output: 2 words instead of 3}\ndiagnosis:\n  rows:\n"
        "    - {hypothesis: The split drops a trailing token, refuted_by: Three words with a newline count 3,"
        " result: confirmed, output: counts 2}\n"
        "cause: {location: 'wordy.py:12', chain: The loop stops one short.}\nprediction: []\n"
        "tests: []\nunverified: none\n"
    )
    cc = "ceh-coding-conduct"
    no_confirmed = good_fix.replace("result: confirmed", "result: standing")
    fix_record_fixtures = [
        *report_fixtures(cc, "count-drops-last-word", good_fix, no_confirmed, "diagnosis.rows", "# Count drops the last word", "fix-cc"),
        *report_fixtures("ceh-testing", "count-drops-last-word", good_fix, no_confirmed, "diagnosis.rows", "# Count drops the last word", "fix-testing"),
        {"script": f"{cc}/artifact-render-hook.py", "stdin": write_at(tmp / "report-fix-cc" / "bad" / "count-drops-last-word.yaml"), "env": no_uv, "out": "uv is not installed"},
        # ceh-coding-conduct holds no plan model, so a plan YAML is not its to check.
        {"script": f"{cc}/artifact-render-hook.py", "stdin": write("broken.yaml"), "env": no_uv, "out": ""},
        {"script": f"{cc}/generated-md-guard.py", "stdin": edit(generated.as_posix()), "out": "gen.yaml"},
    ]  # fmt: skip
    # The session handoff: hand-off-session writes and loads it, whats-next reads it.
    good_handoff = (
        'schema: handoff/v2\nsaved: "2026-11-10 12:00"\nsession: abcd1234\n'
        "header:\n  - '**Window:** 5h at 92%, resets at 14:00'\nrepo: '/work/wordy'\nbranch: main\n"
        "fields: []\ngoal: [Count words]\ndone: []\nin_flight: []\nopen: [Run the tests]\n"
        "decisions_pending: []\nresume_with: git checkout main\n"
    )
    es = "ceh-every-session"
    handoff_fixtures = [
        *report_fixtures(es, "20261110-120000-7c9e6679-7425-40de-944b-e07fc1f90ae7-handoff", good_handoff, good_handoff.replace("open: [Run the tests]", "open: []"), "open", "# Handoff — 2026-11-10 12:00", "handoff"),
        {"script": f"{es}/artifact-render-hook.py", "stdin": write_at(tmp / "report-handoff" / "bad" / "20261110-120000-7c9e6679-7425-40de-944b-e07fc1f90ae7-handoff.yaml"), "env": no_uv, "out": "uv is not installed"},
    ]  # fmt: skip
    # The workflow spec: interview-workflow-task writes it, build-agentic-workflow reads and amends it.
    good_spec = (
        "schema: workflow-spec/v2\nname: ship-digest\ndate: 2026-11-10\n"
        "moment: {state: answered, answer: Right after a release tag is pushed}\n"
        "procedure: {state: answered, steps: [{n: 1, step: Collect PRs}, {n: 2, step: Draft the digest}]}\n"
        "proof: {state: answered, steps: [{n: 1, before: The tag exists, by: command, check: git tag lists it},"
        " {n: 2, before: prs.json exists, by: file, check: digest.md names every PR}]}\n"
        "data_flow: {state: answered, starts_from: The tag name, steps: [{n: 1, reads: [], leaves: [prs.json]},"
        " {n: 2, reads: [{artifact: prs.json, from: 1}], leaves: [digest.md]}]}\n"
        "tooling: {state: unanswered, question: 'Which token reads the PRs?'}\n"
        "done: {state: answered, answer: [digest.md exists for the tag]}\n"
        "interruption: {state: answered, answer: one sitting}\n"
        "rerun_unsafe: {state: answered, steps: []}\n"
        "irreversible: {state: declined, words: not sure, assumption: every outside step is irreversible}\n"
    )
    wb = "ceh-workflow-builder"
    workflow_spec_fixtures = [
        *report_fixtures(wb, "ship-digest-workflow-spec", good_spec, good_spec.replace("from: 1}", "from: 2}"), "data_flow", "## 9. Irreversible steps", "workflow-spec"),
        {"script": f"{wb}/artifact-render-hook.py", "stdin": write_at(tmp / "report-workflow-spec" / "bad" / "ship-digest-workflow-spec.yaml"), "env": no_uv, "out": "uv is not installed"},
        # ceh-workflow-builder holds no plan model, so a plan YAML is not its to check.
        {"script": f"{wb}/artifact-render-hook.py", "stdin": write("broken.yaml"), "env": no_uv, "out": ""},
        {"script": f"{wb}/generated-md-guard.py", "stdin": edit(generated.as_posix()), "out": "gen.yaml"},
    ]  # fmt: skip
    # The run state: run-agentic-workflow writes it after every stage change and reads it to resume.
    good_run = (
        'schema: run-state/v2\nflow: prepublish\nrun_id: "20261003-0930"\n'
        "config: .claude/skills/prepublish-flow/flow.yaml\nmode: headless\n"
        "inputs: [{name: repo, value: '.'}]\nstages:\n"
        "  - {id: audit, state: done, artifacts: [findings.md], note: 'fallback: agent'}\n"
        "  - {id: publish, state: awaiting-approval, artifacts: []}\n"
        "approvals: []\nstatus: awaiting-approval publish\n"
    )
    wr = "ceh-workflow-runner"
    # A run id in the newer form, start time and session id, is accepted beside the older one.
    new_run = tmp / "report-run-state-new" / "run-state.yaml"
    new_run.parent.mkdir()
    new_run.write_text(
        good_run.replace(
            "20261003-0930", "20261003-093000-7c9e6679-7425-40de-944b-e07fc1f90ae7"
        ),
        encoding="utf-8",
    )
    run_state_fixtures = ([
        {"script": f"{wr}/artifact-render-hook.py", "stdin": write_at(new_run), "out": ""},
    ] if have_uv else []) + [
        *report_fixtures(wr, "run-state", good_run, good_run.replace("status: awaiting-approval publish", "status: done"), "status: done while a stage is not done", "FLOW STATUS: awaiting-approval publish", "run-state"),
        {"script": f"{wr}/artifact-render-hook.py", "stdin": write_at(tmp / "report-run-state" / "bad" / "run-state.yaml"), "env": no_uv, "out": "uv is not installed"},
        # ceh-workflow-runner holds no plan model, so a plan YAML is not its to check.
        {"script": f"{wr}/artifact-render-hook.py", "stdin": write("broken.yaml"), "env": no_uv, "out": ""},
        {"script": f"{wr}/generated-md-guard.py", "stdin": edit(generated.as_posix()), "out": "gen.yaml"},
    ]  # fmt: skip
    # The competitor report: analyze-competitor writes it, compare-competitors reads it.
    good_cr = (
        "schema: competitor-report/v2\ncompetitor: Acme\nsource: https://github.com/acme/kit\n"
        "analysed: 2026-11-11\nsummary: A kit that gates changes.\nverdict: Take the gate.\n"
        "fields: {read: shallow clone, author: Acme, version: 1.0.0, version_from: package.json,"
        " license: MIT, size: 2 skills, size_command: ls skills}\n"
        "take:\n  adopt_now:\n    - {idea: Gate, lands_in: ceh-git-workflow:pull-request, why: Stops a bad merge.,"
        " covers: [gate]}\n  build: []\n  skip: []\n"
        "how_it_works: [Init, Gate, Merge]\noh_wow: []\n"
        "inventory:\n  groups:\n    - {group: Skills, count: 2, items: 'gate, review'}\n"
        "coverage:\n  - group: Skills\n    rows:\n"
        "      - {component: gate, evidence: skills/gate, what: Gates a merge, rating: Partial,"
        " ours: ceh-git-workflow:pull-request}\n"
        "      - {component: review, evidence: skills/review, what: Reviews, rating: Covered,"
        " ours: ceh-git-workflow:code-review}\n"
    )
    ca = "ceh-competitor-analysis"
    competitor_report_fixtures = [
        *report_fixtures(ca, "acme", good_cr, good_cr.replace("covers: [gate]", "covers: []"), "no take row covers", "**Tally (2 components):** 1 covered, 1 partial, 0 gaps, 0 N/A.", "competitor-report"),
        {"script": f"{ca}/artifact-render-hook.py", "stdin": write_at(tmp / "report-competitor-report" / "bad" / "acme.yaml"), "env": no_uv, "out": "uv is not installed"},
        # ceh-competitor-analysis holds no plan model, so a plan YAML is not its to check.
        {"script": f"{ca}/artifact-render-hook.py", "stdin": write("broken.yaml"), "env": no_uv, "out": ""},
        {"script": f"{ca}/generated-md-guard.py", "stdin": edit(generated.as_posix()), "out": "gen.yaml"},
    ]  # fmt: skip
    # The glossary: maintain-glossary writes it, record-project-decisions reads it. It is found by
    # its schema key, or at the session root or docs/ beside its GLOSSARY.md, so a schema-less one
    # there is reported and any other GLOSSARY.yaml is left alone. Paths are given relative to the
    # payload cwd, which differs from the fixture's process cwd (the repo).
    good_gl = (
        "schema: glossary/v2\nentries:\n"
        "  - {term: Stage, definition: One step of a workflow., avoid: [step], not_confused_with: []}\n"
        "  - {term: Artifact, definition: A file a stage writes., avoid: [], not_confused_with: [Stage]}\n"
        "open: []\n"
    )
    gl = tmp / "glossary"
    gl_files = {
        "ok/GLOSSARY": good_gl,
        "bad/GLOSSARY": good_gl.replace("avoid: [step]", "avoid: [stage]"),
        "root/GLOSSARY": "key: value\n",
        "root/docs/GLOSSARY": "key: value\n",
        "root/sub/GLOSSARY": "key: value\n",
        "root/docs/other": "key: value\n",
        "alone/GLOSSARY": "key: value\n",
    }
    for name, text in gl_files.items():
        (gl / name).parent.mkdir(parents=True, exist_ok=True)
        (gl / f"{name}.yaml").write_text(text, encoding="utf-8")
        if name != "alone/GLOSSARY":
            (gl / f"{name}.md").write_text("# Glossary\n", encoding="utf-8")
    gl_generated = gl / "gen" / "GLOSSARY.md"
    gl_generated.parent.mkdir()
    gl_generated.write_text(
        "---\nschema: glossary/v2\ngenerated_from: GLOSSARY.yaml\n---\n",
        encoding="utf-8",
    )

    def write_rel(cwd: Path, path: str) -> dict:
        return {
            "tool_name": "Write",
            "tool_input": {"file_path": path},
            "cwd": str(cwd),
        }

    def gl_rendered(where: str):
        def after() -> str | None:
            text = (gl / where / "GLOSSARY.md").read_text(encoding="utf-8")
            ok = "generated_from: GLOSSARY.yaml" in text and text.index(
                "**Artifact**"
            ) < text.index("**Stage**")
            return None if ok else f"{where}/GLOSSARY.md was not rendered in order"

        return after

    ce, rh_ce = (
        "ceh-codebase-explanation",
        "ceh-codebase-explanation/artifact-render-hook.py",
    )
    glossary_fixtures = ([
        {"script": rh_ce, "stdin": write_rel(gl / "ok", "GLOSSARY.yaml"), "out": "", "after": gl_rendered("ok")},
        {"script": rh_ce, "stdin": write_at(gl / "bad" / "GLOSSARY.yaml"), "out": "entries.0"},
        {"script": rh_ce, "stdin": write_rel(gl / "root", "GLOSSARY.yaml"), "out": "no 'schema:"},
        {"script": rh_ce, "stdin": write_rel(gl / "root", "docs/GLOSSARY.yaml"), "out": "no 'schema:"},
        # record-project-decisions carries the model, so ceh-every-session's hook checks it too.
        {"script": f"{es}/artifact-render-hook.py", "stdin": write_rel(gl / "ok", "GLOSSARY.yaml"), "out": ""},
    ] if have_uv else []) + [
        # A matched file without uv warns, so an empty output shows each of these was skipped.
        {"script": rh_ce, "stdin": write_rel(gl / "root", "docs/GLOSSARY.yaml"), "env": no_uv, "out": "uv is not installed"},
        {"script": rh_ce, "stdin": write_rel(gl / "alone", "GLOSSARY.yaml"), "env": no_uv, "out": ""},
        {"script": rh_ce, "stdin": write_rel(gl / "root", "docs/other.yaml"), "env": no_uv, "out": ""},
        {"script": rh_ce, "stdin": write_rel(gl / "root", "sub/GLOSSARY.yaml"), "env": no_uv, "out": ""},
        {"script": rh_ce, "stdin": write_at(gl / "root" / "sub" / "GLOSSARY.yaml"), "env": no_uv, "out": ""},
        {"script": f"{ce}/generated-md-guard.py", "stdin": edit(gl_generated.as_posix()), "out": "GLOSSARY.yaml"},
    ]  # fmt: skip
    # The blog voice profile: draft-post writes it, edit-post reads it. It is found by its schema
    # key, or at .agents_workspace/product/blog-voice.yaml under the payload cwd with no Markdown
    # needed. ceh-blog-and-seo also carries the evidence model, so its hook renders EVIDENCE.yaml
    # too.
    good_bv = (
        "schema: blog-voice/v2\nblog: content/posts\nposts_read: 3\ndate: 2026-11-12\n"
        "rhythm:\n  - point: Short, then long\n    quote: |\n      It broke.\n      Then it broke again.\n"
        "    source: content/posts/one.md\n"
        "register:\n  - {point: Casual, quote: Honestly., source: null}\n"
        "recurring_words: []\nnever_used: []\nopenings_closings: []\n"
    )
    bv = tmp / "blog-voice"
    bv_ws = Path(".agents_workspace") / "product"
    bv_files = {
        f"ok/{bv_ws.as_posix()}/blog-voice.yaml": good_bv,
        f"bad/{bv_ws.as_posix()}/blog-voice.yaml": good_bv.replace(
            "quote: Honestly.", "quote: '   '"
        ),
        f"none/{bv_ws.as_posix()}/blog-voice.yaml": "key: value\n",
        f"none/{bv_ws.as_posix()}/other.yaml": "key: value\n",
        "none/blog-voice.yaml": "key: value\n",
        "ev/product/EVIDENCE.yaml": good_ev,
    }
    for name, text in bv_files.items():
        (bv / name).parent.mkdir(parents=True, exist_ok=True)
        (bv / name).write_text(text, encoding="utf-8")
    bv_generated = bv / "gen" / "blog-voice.md"
    bv_generated.parent.mkdir()
    bv_generated.write_text(
        "---\nschema: blog-voice/v2\ngenerated_from: blog-voice.yaml\n---\n",
        encoding="utf-8",
    )

    def bv_rendered() -> str | None:
        md = bv / "ok" / bv_ws / "blog-voice.md"
        text = md.read_text(encoding="utf-8") if md.is_file() else ""
        ok = (
            "## Recurring words and phrases\n\nNone established." in text
            and "  Then it broke again." in text
        )
        return None if ok else "blog-voice.md was not rendered"

    def ev_rendered() -> str | None:
        md = bv / "ev" / "product" / "EVIDENCE.md"
        ok = md.is_file() and "| Tests | passed |" in md.read_text(encoding="utf-8")
        return None if ok else "EVIDENCE.md was not rendered by ceh-blog-and-seo's hook"

    rh_bl = "ceh-blog-and-seo/artifact-render-hook.py"
    blog_voice_fixtures = ([
        {"script": rh_bl, "stdin": write_rel(bv / "ok", f"{bv_ws.as_posix()}/blog-voice.yaml"), "out": "", "after": bv_rendered},
        {"script": rh_bl, "stdin": write_at(bv / "bad" / bv_ws / "blog-voice.yaml"), "out": "register.0.quote"},
        {"script": rh_bl, "stdin": write_rel(bv / "none", f"{bv_ws.as_posix()}/blog-voice.yaml"), "out": "no 'schema:"},
        {"script": rh_bl, "stdin": write_rel(bv / "none", (bv / "none" / bv_ws / "blog-voice.yaml").as_posix()), "out": "no 'schema:"},
        {"script": rh_bl, "stdin": write_at(bv / "ev" / "product" / "EVIDENCE.yaml"), "out": "", "after": ev_rendered},
    ] if have_uv else []) + [
        {"script": rh_bl, "stdin": write_rel(bv / "none", f"{bv_ws.as_posix()}/blog-voice.yaml"), "env": no_uv, "out": "uv is not installed"},
        {"script": rh_bl, "stdin": write_rel(bv / "none", f"{bv_ws.as_posix()}/other.yaml"), "env": no_uv, "out": ""},
        {"script": rh_bl, "stdin": write_rel(bv / "none", "blog-voice.yaml"), "env": no_uv, "out": ""},
        {"script": rh_bl, "stdin": write_at(bv / "none" / bv_ws / "blog-voice.yaml"), "env": no_uv, "out": ""},
        {"script": "ceh-blog-and-seo/generated-md-guard.py", "stdin": edit(bv_generated.as_posix()), "out": "blog-voice.yaml"},
    ]  # fmt: skip
    # The repeat-mistake report: prevent-repeat-mistake writes and reads it. It is found by its
    # schema key, or by its dated name in product/retros/ or .agents_workspace/product/retros/
    # under the payload cwd. A labelled name and the dated name anywhere else are left alone.
    good_rm = (
        "schema: repeat-mistake/v2\ndate: 2026-11-12\nother_file: null\nfixes:\n"
        "  - id: 1\n    mistake: Dates written as 10/09/2026\n    evidence: 'roadmap.md:14'\n"
        '    rung: 3\n    fix: A date hook\n    proof: "yes"\n    status: awaiting approval\n'
        "    why_rung: A pattern match catches it.\n    draft: |\n      ```python\n      deny()\n      ```\n"
    )
    rm = tmp / "repeat-mistake"
    day = "2026-11-12-repeat-mistake"
    # The newer name form, start time and session id first, and the same with a label.
    stamped = "20261112-103000-7c9e6679-7425-40de-944b-e07fc1f90ae7-repeat-mistake"
    stamped_label = (
        "20261112-103000-7c9e6679-7425-40de-944b-e07fc1f90ae7-cockpit-repeat-mistake"
    )
    rm_files = {
        f"none/product/retros/{stamped}.yaml": "key: value\n",
        f"none/product/retros/{stamped_label}.yaml": "key: value\n",
        f"ok/product/retros/{day}.yaml": good_rm,
        f"bad/product/retros/{day}.yaml": good_rm.replace(
            "status: awaiting approval", "status: done"
        ),
        f"none/product/retros/{day}.yaml": "key: value\n",
        f"none/.agents_workspace/product/retros/{day}.yaml": "key: value\n",
        "none/product/retros/notes.yaml": "key: value\n",
        "none/product/retros/2026-11-12-cockpit-repeat-mistake.yaml": "key: value\n",
        f"none/{day}.yaml": "key: value\n",
    }
    for name, text in rm_files.items():
        (rm / name).parent.mkdir(parents=True, exist_ok=True)
        (rm / name).write_text(text, encoding="utf-8")
    rm_generated = rm / "gen" / f"{day}.md"
    rm_generated.parent.mkdir()
    rm_generated.write_text(
        f"---\nschema: repeat-mistake/v2\ngenerated_from: {day}.yaml\n---\n",
        encoding="utf-8",
    )

    def rm_rendered() -> str | None:
        md = rm / "ok" / "product" / "retros" / f"{day}.md"
        text = md.read_text(encoding="utf-8") if md.is_file() else ""
        ok = "### 1: Dates written as 10/09/2026\n\n```python\ndeny()\n```" in text
        return None if ok else f"{day}.md was not rendered"

    rh_es = f"{es}/artifact-render-hook.py"
    local = (
        rm / "none" / ".agents_workspace" / "product" / "retros" / f"{day}.yaml"
    ).as_posix()
    repeat_mistake_fixtures = ([
        {"script": rh_es, "stdin": write_rel(rm / "ok", f"product/retros/{day}.yaml"), "out": "", "after": rm_rendered},
        {"script": rh_es, "stdin": write_at(rm / "bad" / "product" / "retros" / f"{day}.yaml"), "out": "fixes.0.status"},
        {"script": rh_es, "stdin": write_rel(rm / "none", f"product/retros/{day}.yaml"), "out": "no 'schema:"},
        {"script": rh_es, "stdin": write_rel(rm / "none", local), "out": "no 'schema:"},
    ] if have_uv else []) + [
        {"script": rh_es, "stdin": write_rel(rm / "none", f".agents_workspace/product/retros/{day}.yaml"), "env": no_uv, "out": "uv is not installed"},
        {"script": rh_es, "stdin": write_rel(rm / "none", f"product/retros/{stamped}.yaml"), "env": no_uv, "out": "uv is not installed"},
        {"script": rh_es, "stdin": write_rel(rm / "none", f"product/retros/{stamped_label}.yaml"), "env": no_uv, "out": ""},
        {"script": rh_es, "stdin": write_rel(rm / "none", "product/retros/notes.yaml"), "env": no_uv, "out": ""},
        {"script": rh_es, "stdin": write_rel(rm / "none", "product/retros/2026-11-12-cockpit-repeat-mistake.yaml"), "env": no_uv, "out": ""},
        {"script": rh_es, "stdin": write_rel(rm / "none", f"{day}.yaml"), "env": no_uv, "out": ""},
        {"script": rh_es, "stdin": write_at(rm / "none" / "product" / "retros" / f"{day}.yaml"), "env": no_uv, "out": ""},
        {"script": f"{es}/generated-md-guard.py", "stdin": edit(rm_generated.as_posix()), "out": f"{day}.yaml"},
    ]  # fmt: skip
    evidence_fixtures = [
        *glossary_fixtures,
        *blog_voice_fixtures,
        *repeat_mistake_fixtures,
        *spine_fixtures(
            "ceh-testing", "EVIDENCE", good_ev,
            good_ev.replace("status: passed", "status: passing"),
            "runs.0.areas.tests.status", "| Tests | passed |",
        ),
        *spine_fixtures(
            "ceh-codebase-explanation", "ARCHITECTURE", good_arch,
            good_arch.replace("  bullets:\n    - It counts words.\n", "  bullets: []\n"),
            "overview.bullets", "## 01. Overview",
        ),
        *spine_fixtures(
            "ceh-product-direction", "VISION", good_vision,
            good_vision.replace("status: draft", "status: adopted"),
            "status adopted allows no [assumed]", "## Identity",
        ),
        *spine_fixtures(
            "ceh-product-direction", "BUSINESS_PLAN", good_bp,
            good_bp.replace("pmf_gate: 2", "pmf_gate: 9"),
            "pmf_gate", "## §01 Executive Summary",
        ),
        *report_fixtures("ceh-testing", "QA_REPORT", good_qa, good_qa.replace("bugs: []", "bugs: [B3]", 1), "charters.0.bugs", "# QA report: Wordy"),
        *report_fixtures("ceh-testing", "search", good_perf, good_perf.replace("low: 110", "low: 125"), "attempts.0", "# Performance: search"),
        *security_fixtures,
        *usability_fixtures,
        *fix_record_fixtures,
        *handoff_fixtures,
        *workflow_spec_fixtures,
        *run_state_fixtures,
        *competitor_report_fixtures,
        # ceh-testing holds no plan model, so a plan YAML is not its to check.
        *([{"script": "ceh-testing/artifact-render-hook.py", "stdin": write("broken.yaml"), "out": ""}] if have_uv else []),
        {"script": "ceh-testing/artifact-render-hook.py", "stdin": write_at(stray), "env": no_uv, "out": ""},
    ]  # fmt: skip

    # build-record-guard on a plan/v2 YAML: a new `event: Built Phase` entry needs the skill.
    built_entry = (
        "  - date: 2026-10-26\n    event: Built Phase\n    phase: 1\n    details: x\n"
    )
    yaml_plan = (plans / "ok.yaml").as_posix()

    def record_yaml(t: str = "none") -> dict:
        ti = {
            "file_path": yaml_plan,
            "old_string": "record:\n",
            "new_string": "record:\n" + built_entry,
        }
        return {"tool_name": "Edit", "tool_input": ti, "transcript_path": tx[t]}

    return [
        # artifact-render-hook: block an invalid plan YAML, render a valid one, skip other files,
        # and warn once when uv is missing. generated-md-guard: deny an edit to a generated .md,
        # naming its YAML.
        *artifact_fixtures("ceh-build-plan", True),
        *artifact_fixtures("ceh-check-build-against-plan", False),
        # ceh-every-session holds the plan model for whats-next, so its hook checks plans too.
        *artifact_fixtures("ceh-every-session", False),
        *evidence_fixtures,
        {"script": "build-record-guard.py", "stdin": record_yaml(), "out": "implement-from-plan"},
        {"script": "build-record-guard.py", "stdin": record_yaml("skill"), "out": ""},
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
        {"script": "ask-user-question-guard.py", "stdin": {"tool_name": "AskUserQuestion", "tool_input": {}}, "out": "no user is present"},
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
        # skill-started-guard (ceh-git-workflow): commit, CHANGELOG.md and README.md need their skill started.
        {**guard(gw, "Bash", commit), "out": "ceh-git-workflow:commit"},
        {**guard(gw, "Bash", commit, started("ceh-git-workflow:commit")), "out": ""},
        {**guard(gw, "Bash", commit, started("ceh-git-workflow:commit", "slash")), "out": ""},
        {**guard(gw, "Bash", {"command": "cd x && git -C y commit -m z"}), "out": "ceh-git-workflow:commit"},
        {**guard(gw, "Bash", {"command": "git status"}), "out": ""},
        {**guard(gw, "Bash", {"command": 'grep "git commit" f'}), "out": ""},
        {**guard(gw, "Edit", changelog), "out": "ceh-git-workflow:update-changelog"},
        {**guard(gw, "Edit", changelog, started("ceh-git-workflow:update-changelog")), "out": ""},
        {**guard(gw, "Edit", changelog, started("ceh-git-workflow:release")), "out": ""},
        {**guard(gw, "Write", readme), "out": "ceh-git-workflow:update-readme"},
        {**guard(gw, "Write", readme, started("ceh-git-workflow:update-readme")), "out": ""},
        {**guard(gw, "Write", {**readme, "file_path": (tmp / "elsewhere" / "README.md").as_posix()}), "out": ""},
        {**guard(gw, "Bash", commit), "env": {"CEH_SKILL_STARTED_GUARD": "off"}, "out": ""},
        {**guard(gw, "Bash", commit), "env": {"CEH_DISABLED_HOOKS": "skill-started-guard"}, "out": ""},
        # skill-started-guard (ceh-testing): a test file needs a testing skill started.
        {**guard(tst, "Write", test_file), "out": "ceh-testing:write-test-first"},
        {**guard(tst, "Edit", {**test_file, "file_path": f"{guarded}/web/a.spec.ts"}), "out": "ceh-testing:write-test-first"},
        *[{**guard(tst, "Write", test_file, started(s)), "out": ""} for s in (
            "ceh-testing:write-test-first", "ceh-testing:test-a-bug-fix", "ceh-testing:verify-behavior-preserved",
            "ceh-python-library:write-pytest-library-tests", "ceh-python-service:write-pytest-service-tests",
            "ceh-web-frontend:write-vitest-playwright-tests")],
        {**guard(tst, "Write", {**test_file, "file_path": f"{guarded}/src/check.py"}), "out": ""},
        {**guard(tst, "Write", {**test_file, "file_path": (tmp / "elsewhere" / "test_x.py").as_posix()}), "out": ""},
        {**guard(tst, "Write", test_file), "env": {"CEH_SKILL_STARTED_GUARD": "off"}, "out": ""},
        {**guard(tst, "Write", test_file), "env": {"CEH_DISABLED_HOOKS": "skill-started-guard"}, "out": ""},
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


def run_batch(batch: int, batches: int, bash: str | None) -> list[tuple[int, str, str]]:
    problems = []
    i = -1

    def fail(where: str, message: str) -> None:
        problems.append((i, where, message))

    # Keyed by <plugin>/<script>, and by the bare name while only one plugin ships it (else None).
    scripts: dict[str, Path | None] = {}
    for d in plugin_dirs():
        hooks = d / "hooks" / "hooks.json"
        if hooks.is_file():
            for name in HOOK_SCRIPT_PAT.findall(hooks.read_text(encoding="utf-8")):
                path = d / "scripts" / name
                scripts[f"{d.name}/{name}"] = path
                scripts[name] = path if scripts.get(name, path) == path else None

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
        groups = {
            name: n % batches
            for n, name in enumerate(
                dict.fromkeys(f["script"].split("/", 1)[0] for f in fixtures)
            )
        }

        # CI installs uv, so a skip there would hide the artifact fixtures: fail instead.
        if batch == 0 and os.environ.get("CI") and not shutil.which("uv"):
            fail(
                ".github/workflows/validate.yml",
                "uv is not installed, the artifact fixtures did not run",
            )
        if batch == 0:
            covered = {scripts.get(f["script"]) for f in fixtures}
            for path in sorted({p for p in scripts.values() if p} - covered):
                fail(
                    rel(path),
                    "hook script has no fixture in checks/hooks.py hook_fixtures()",
                )

        for i, f in enumerate(fixtures):
            if groups[f["script"].split("/", 1)[0]] != batch:
                continue
            script = scripts.get(f["script"])
            where = f"hook fixture {i} ({f['script']})"
            if script is None:
                fail(
                    where,
                    "several plugins ship this script, name it <plugin>/<script>"
                    if f["script"] in scripts
                    else "no hooks.json runs this script",
                )
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
    return problems


def check() -> None:
    bash = check_bash()
    batches = min(4, os.cpu_count() or 1)
    # less-code: rebuild private fixture trees; share setup only if its cost becomes dominant.
    with ThreadPoolExecutor(max_workers=batches) as pool:
        results = list(
            pool.map(lambda batch: run_batch(batch, batches, bash), range(batches))
        )
    for _, where, message in sorted(
        (problem for batch in results for problem in batch),
        key=lambda problem: problem[0],
    ):
        fail(where, message)


if __name__ == "__main__":
    sys.exit(main(check))
