import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "checks"))

import common
import validate


class BashTests(unittest.TestCase):
    def test_custom_git_install_wins_over_wsl(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git = root / "cmd" / "git.exe"
            git.parent.mkdir()
            git.touch()
            bash = root / "bin" / "bash.exe"
            bash.parent.mkdir()
            bash.touch()
            with (
                patch.object(sys, "platform", "win32"),
                patch.object(common.shutil, "which", return_value=str(git)) as which,
            ):
                self.assertEqual(common.find_bash(), str(bash))
                which.assert_called_once_with("git")

    def test_windows_without_git_bash_never_uses_wsl(self):
        with (
            patch.object(sys, "platform", "win32"),
            patch.object(common.shutil, "which", return_value=None) as which,
        ):
            self.assertIsNone(common.find_bash())
            which.assert_called_once_with("git")

    def test_non_windows_uses_path(self):
        with (
            patch.object(sys, "platform", "linux"),
            patch.object(common.shutil, "which", return_value="/bin/bash") as which,
        ):
            self.assertEqual(common.find_bash(), "/bin/bash")
            which.assert_called_once_with("bash")

    def test_git_without_bash_is_unavailable(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(sys, "platform", "win32"),
            patch.object(
                common.shutil, "which", return_value=str(Path(tmp) / "cmd/git.exe")
            ),
        ):
            self.assertIsNone(common.find_bash())

    def test_missing_bash_skips_locally_and_fails_in_ci(self):
        for ci in (False, True):
            with (
                self.subTest(ci=ci),
                patch.object(common, "find_bash", return_value=None),
                patch.dict(os.environ, {"CI": "1"} if ci else {}, clear=True),
                contextlib.redirect_stderr(io.StringIO()) as err,
            ):
                errors = common.run_check(common.check_bash)
                self.assertEqual(bool(errors), ci)
                if not ci:
                    self.assertIn("skipped", err.getvalue())
        common.errors.clear()

    def test_real_disabled_hooks_are_silent(self):
        bash = common.find_bash()
        if not bash:
            self.skipTest("Bash unavailable")
        env = {k: v for k, v in os.environ.items() if not k.startswith("CEH_")}
        for name in ("load-contract", "inject-less-code-reminder"):
            script = f"plugins/standalone/ceh-coding-conduct/scripts/{name}.sh"
            for disabled in ("", name):
                with self.subTest(hook=name, disabled=disabled):
                    r = subprocess.run(
                        [bash, script],
                        cwd=common.REPO,
                        input="{}",
                        text=True,
                        capture_output=True,
                        env={**env, "CEH_DISABLED_HOOKS": disabled},
                        timeout=30,
                    )
                    self.assertEqual(r.returncode, 0, r.stderr)
                    self.assertEqual(bool(r.stdout.strip()), not bool(disabled))


class ProcessTests(unittest.TestCase):
    def test_spawned_groups_keep_errors_separate_and_ordered(self):
        from concurrent.futures import ProcessPoolExecutor
        import multiprocessing

        with tempfile.TemporaryDirectory() as tmp:
            for name in ("first", "second"):
                (Path(tmp) / f"fixture_{name}.py").write_text(
                    f"from common import fail\ndef check():\n    fail('{name}', 'problem')\n",
                    encoding="utf-8",
                )
            sys.path.insert(0, tmp)
            try:
                with ProcessPoolExecutor(
                    max_workers=1, mp_context=multiprocessing.get_context("spawn")
                ) as pool:
                    results = list(
                        pool.map(
                            validate.run_group, ["fixture_first", "fixture_second"]
                        )
                    )
                self.assertEqual(results, [["first: problem"], ["second: problem"]])
                self.assertEqual(common.errors, [])
            finally:
                sys.path.remove(tmp)

    def test_main_keeps_report_order_and_failure_exit(self):
        with (
            patch.object(validate, "CHECKS", ["skill_refs", "keys"]),
            patch.object(validate, "ProcessPoolExecutor") as pool,
            contextlib.redirect_stdout(io.StringIO()) as out,
        ):
            pool.return_value.__enter__.return_value.map.return_value = [
                ["first failure"],
                ["second failure"],
            ]
            self.assertEqual(validate.main(), 1)
            self.assertLess(
                out.getvalue().index("[skill-refs]"), out.getvalue().index("[keys]")
            )
            self.assertLessEqual(pool.call_args.kwargs["max_workers"], 2)


if __name__ == "__main__":
    unittest.main()
