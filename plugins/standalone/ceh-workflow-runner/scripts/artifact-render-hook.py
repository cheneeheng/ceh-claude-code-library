#!/usr/bin/env python3
"""PostToolUse hook: check a YAML artifact the agent just wrote, and render its Markdown.

Matches Edit|Write|MultiEdit. It acts on a `.yaml` whose `schema: <name>/v<N>` names a model in
this plugin, and on a `.yaml` in the place a format lives (`place_format`) when this plugin holds
that format's model, so a spine file or glossary missing its schema key is reported, not skipped.
A relative `file_path` is resolved against the payload's `cwd`. It runs `scripts/artifact.py render` through uv. Errors go back to the agent as a block
reason. The tool has already run, so the file stays on disk until the agent fixes it, and the
Markdown is not regenerated. When the check cannot run (no uv, a failed install, an unknown
version), the agent is told once per session and reason, never left with a silent pass.
CEH_ARTIFACT_CHECK=off disables it.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts" / "artifact.py"
SCHEMA = re.compile(r"""^schema:\s*["']?([a-z0-9]+(?:-[a-z0-9]+)*)/v\d+""", re.M)
UV_HELP = "Install uv (https://docs.astral.sh/uv/) so the check can run."
# Spine file stems and their formats, matched in a `product` or `business` folder or beside a
# `.md` of the same stem, so an unrelated STRATEGY.yaml elsewhere is left alone.
SPINE = {
    "EVIDENCE": "evidence",
    "ARCHITECTURE": "architecture",
    "VISION": "vision",
    "STRATEGY": "strategy",
    "BUSINESS_PLAN": "business-plan",
}


def model_names() -> set[str]:
    return {p.name[: -len("-model.py")] for p in ROOT.glob("**/references/*-model.py")}


def place_format(file: Path, root: Path) -> str | None:
    """The format a file's place says it holds, or None. `root` is the session's cwd."""
    if file.parent.name == "plans" and file.parent.parent.name == "product":
        return "plan"
    # Only at the root or in docs/, and only beside its GLOSSARY.md, so a project's unrelated
    # GLOSSARY.yaml (i18n data, say) is left alone.
    if file.name == "GLOSSARY.yaml":
        home = file.parent in (root, root / "docs")
        return "glossary" if home and file.with_suffix(".md").exists() else None
    name = SPINE.get(file.stem)
    near = (
        file.parent.name in ("product", "business") or file.with_suffix(".md").exists()
    )
    return name if name and near else None


def warn_once(session: str, path: str, why: str) -> None:
    # One marker per session and reason, so a missing uv is said once, not on every write.
    key = hashlib.sha1(f"{session}\n{why}".encode()).hexdigest()[:16]
    marker = Path(tempfile.gettempdir()) / f"ceh-artifact-check-{key}"
    if marker.exists():
        return
    marker.touch()
    note = f"{path} was not checked against its format: {why}"
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": note,
        }
    }
    print(json.dumps(out))


def main() -> None:
    disabled = os.environ.get("CEH_DISABLED_HOOKS", "").replace(" ", "").split(",")
    if Path(__file__).stem in disabled:
        return
    if os.environ.get("CEH_ARTIFACT_CHECK", "").strip().lower() == "off":
        return

    payload = json.load(sys.stdin)
    path = payload.get("tool_input", {}).get("file_path", "")
    # A relative path is the session's, not this process's: resolve it against the payload cwd.
    root = Path(payload.get("cwd") or os.getcwd()).resolve()
    file = (root / path).resolve() if path else Path()
    path = str(file)
    if file.suffix != ".yaml" or not file.is_file():
        return
    m = SCHEMA.search(file.read_text(encoding="utf-8"))
    names = model_names()
    if not (m and m.group(1) in names) and place_format(file, root) not in names:
        return

    session = str(payload.get("session_id", ""))
    uv = shutil.which("uv")
    if not uv:
        warn_once(session, path, f"uv is not installed. {UV_HELP}")
        return
    try:
        r = subprocess.run(
            [uv, "run", "--quiet", "--script", str(CLI), "render", path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=110,
        )
    except subprocess.TimeoutExpired:
        warn_once(
            session, path, "the check timed out, likely while uv installed pydantic."
        )
        return
    out = (r.stdout + r.stderr).strip()
    if r.returncode == 1:
        reason = f"{out}\nFix {path}. The Markdown was not regenerated."
        print(json.dumps({"decision": "block", "reason": reason}))
    elif r.returncode != 0:
        warn_once(session, path, f"artifact.py exited {r.returncode}: {out[-500:]}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # a broken hook says so, never passes silently
        warn_once("", "the artifact", f"the hook failed: {type(e).__name__}: {e}")
    sys.exit(0)
