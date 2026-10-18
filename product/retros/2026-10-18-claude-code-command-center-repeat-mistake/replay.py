"""Replay this session's two skipped-skill mistakes against the draft gate hooks."""

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
T = Path.home() / (
    ".claude/projects/C--Users-Chen-WorkLocal-00-Project-claude-code-command-center/"
    "a2035f28-1913-41f9-8f99-d59a0cc27bfe.jsonl"
)
BG = HERE / "draft/ceh-git-workflow/scripts/branch-skill-gate.py"
FG = HERE / "draft/ceh-testing/scripts/bug-fix-skill-gate.py"
REPO = r"C:\Users\Chen\WorkLocal\00_Project\claude-code-command-center"
lines = T.read_text(encoding="utf-8").splitlines(keepends=True)


def cut_before(marker, name, extra_skill=None):
    """Transcript up to the first line containing `marker`, optionally plus a Skill call."""
    n = next(i for i, line in enumerate(lines) if marker in line)
    body = lines[:n]
    if extra_skill:
        call = {"type": "tool_use", "name": "Skill", "input": {"skill": extra_skill}}
        body.append(json.dumps({"message": {"content": [call]}}) + "\n")
    path = HERE / name
    path.write_text("".join(body), encoding="utf-8")
    return str(path)


def run(hook, tool_input, transcript):
    payload = json.dumps({"tool_input": tool_input, "transcript_path": transcript})
    out = subprocess.run(
        [sys.executable, "-I", "-S", str(hook)],
        input=payload,
        capture_output=True,
        text=True,
    ).stdout
    return "deny" if '"deny"' in out else "allow"


checks = []
branch_cmd = "git checkout -b fix/usage-insights-projection-range-note"
cut_b = cut_before(branch_cmd, "cut-branch.jsonl")
ok_b = cut_before(branch_cmd, "ok-branch.jsonl", "ceh-git-workflow:branch")
checks += [
    (
        "branch: real mistake",
        run(BG, {"command": f"cd /c/x && {branch_cmd}"}, cut_b),
        "deny",
    ),
    ("branch: skill loaded", run(BG, {"command": branch_cmd}, ok_b), "allow"),
    (
        "branch: full transcript, skill only named in text",
        run(BG, {"command": branch_cmd}, str(T)),
        "deny",
    ),
]
for cmd, want in [
    ("git switch -c feat/x", "deny"),
    ("git branch fix/y", "deny"),
    ("git worktree add ../w -b feat/z", "deny"),
    ("git branch -d old", "allow"),
    ("git checkout main", "allow"),
    ("git branch --show-current", "allow"),
    ("git status", "allow"),
    ("git branch\necho done", "allow"),
]:
    checks.append((f"branch: {cmd}", run(BG, {"command": cmd}, cut_b), want))

test_file = REPO + r"\apps\usage-insights\web\src\layout\defaultLayout.test.tsx"
plan = REPO + r"\apps\usage-insights\product\plans\usage-insights.md"
marker = '"name":"Edit","input":{"file_path":"' + test_file.replace("\\", "\\\\")
cut_e = cut_before(marker, "cut-edit.jsonl")
ok_e = cut_before(marker, "ok-edit.jsonl", "ceh-testing:test-a-bug-fix")
no_note = HERE / "nonote.jsonl"
no_note.write_text("".join(lines[:3]), encoding="utf-8")
checks += [
    ("fix: real mistake", run(FG, {"file_path": test_file}, cut_e), "deny"),
    ("fix: skill loaded", run(FG, {"file_path": test_file}, ok_e), "allow"),
    ("fix: edit under product/ exempt", run(FG, {"file_path": plan}, cut_e), "allow"),
    (
        "fix: no fix note in session",
        run(FG, {"file_path": test_file}, str(no_note)),
        "allow",
    ),
]

for name, got, want in checks:
    print(f"{'PASS' if got == want else 'FAIL'}  {name}: {got} (want {want})")
sys.exit(any(got != want for _, got, want in checks))
