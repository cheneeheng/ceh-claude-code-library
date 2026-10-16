"""scripts: *.sh pass `bash -n` (+ shellcheck if available); *.py pass py_compile.

`bash` and `shellcheck` are used when present and skipped otherwise, so a missing tool never causes
a false failure. CI runs both: GitHub-hosted Ubuntu runners ship them.
"""

from __future__ import annotations

import shutil
import subprocess
import sys

from common import REPO, fail, main, plugin_dirs, rel


def check() -> None:
    have_shellcheck = shutil.which("shellcheck") is not None
    have_bash = shutil.which("bash") is not None

    def run(cmd: list[str]) -> subprocess.CompletedProcess:
        # cwd=REPO + POSIX-relative paths so Git Bash on Windows resolves them.
        return subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)

    for d in plugin_dirs():
        for script in sorted((d / "scripts").glob("*")):
            where = rel(script)
            if script.suffix == ".sh":
                if have_bash:
                    r = run(["bash", "-n", where])
                    if r.returncode != 0:
                        fail(where, f"bash syntax error: {r.stderr.strip()}")
                if have_shellcheck:
                    r = run(["shellcheck", "-S", "error", where])
                    if r.returncode != 0:
                        fail(where, f"shellcheck error:\n{r.stdout.strip()}")
            elif script.suffix == ".py":
                r = run([sys.executable, "-m", "py_compile", where])
                if r.returncode != 0:
                    fail(where, f"py_compile error: {r.stderr.strip()}")


if __name__ == "__main__":
    sys.exit(main(check))
