"""Tests for the decisions in setup.py. Run: python -m unittest tools/setup/test_setup.py"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import setup  # noqa: E402

MARKET = "@ceh-claude-code-library"


def entry(name, scope, enabled=True, path=None, market=MARKET):
    e = {"id": name + market, "scope": scope, "enabled": enabled}
    if path is not None:
        e["projectPath"] = path
    return e


class PluginStatesTests(unittest.TestCase):
    def test_windows_path_with_backslashes_and_other_case_matches(self):
        states = setup.plugin_states(
            [entry("ceh-testing", "local", path="C:\\Work\\Repo")], "c:/work/repo", True
        )
        self.assertEqual(states, {"ceh-testing": ("on", "local")})

    def test_posix_path_is_case_sensitive(self):
        entries = [entry("ceh-testing", "local", path="/srv/a/Repo")]
        self.assertEqual(setup.plugin_states(entries, "/srv/a/repo", False), {})
        self.assertEqual(
            setup.plugin_states(entries, "/srv/a/Repo", False),
            {"ceh-testing": ("on", "local")},
        )

    def test_local_entry_wins_over_user_entry(self):
        entries = [
            entry("ceh-testing", "user", enabled=True),
            entry("ceh-testing", "local", enabled=False, path="/r"),
        ]
        self.assertEqual(
            setup.plugin_states(entries, "/r", False), {"ceh-testing": ("off", "local")}
        )

    def test_other_marketplace_and_other_folder_are_ignored(self):
        entries = [
            entry("ceh-testing", "user", market="@elsewhere"),
            entry("ceh-build-plan", "local", path="/other"),
        ]
        self.assertEqual(setup.plugin_states(entries, "/r", False), {})


class ResolveTests(unittest.TestCase):
    def test_unmet_requires_drops_the_plugin_and_names_its_skills(self):
        plugins, lines = setup.resolve(["ceh-python-library"], {"uv"}, None)
        self.assertNotIn("ceh-python-library", plugins)
        self.assertIn("ceh-testing", plugins)
        self.assertTrue(
            any(
                "ceh-python-library will not be installed: it needs uv" in line
                and "publish-python-library" in line
                for line in lines
            )
        )

    def test_unmet_degrades_keeps_the_plugin_and_names_what_loses_function(self):
        plugins, lines = setup.resolve(["ceh-git-workflow"], {"gh"}, None)
        self.assertEqual(plugins, ["ceh-git-workflow"])
        self.assertTrue(
            any(
                line.startswith("ceh-git-workflow: without gh")
                and "pull-request" in line
                for line in lines
            )
        )

    def test_a_dependency_that_degrades_is_warned(self):
        plugins, lines = setup.resolve(["ceh-web-frontend"], {"git"}, None)
        self.assertIn("ceh-testing", plugins)
        self.assertTrue(
            any(line.startswith("ceh-testing: without git") for line in lines)
        )

    def test_min_claude_above_the_installed_version(self):
        _, lines = setup.resolve(["ceh-workflow-runner"], set(), (2, 1, 200))
        self.assertTrue(
            any(
                "run-agentic-workflow need Claude Code 2.1.269 or later, you have 2.1.200"
                in line
                for line in lines
            )
        )
        _, lines = setup.resolve(["ceh-workflow-runner"], set(), (2, 1, 300))
        self.assertFalse(any("Claude Code" in line for line in lines))

    def test_chrome_note_whatever_is_installed(self):
        _, lines = setup.resolve(["ceh-testing"], set(), None)
        self.assertTrue(
            any(
                "Claude in Chrome" in line and "explore-app-for-bugs" in line
                for line in lines
            )
        )


class StatuslineCommandTests(unittest.TestCase):
    def test_set_statusline_is_left_alone(self):
        settings = {"statusLine": {"type": "command", "command": "x"}}
        self.assertIsNone(setup.statusline_command(settings, True, True, "p"))

    def test_windows_with_and_without_pwsh(self):
        self.assertEqual(
            setup.statusline_command({}, True, True, "C:\\c\\s.ps1"),
            'pwsh -NoProfile -File "C:\\c\\s.ps1"',
        )
        self.assertEqual(
            setup.statusline_command({}, True, False, "C:\\c\\s.ps1"),
            'powershell -NoProfile -File "C:\\c\\s.ps1"',
        )

    def test_linux_runs_the_sh_variant_with_bash(self):
        self.assertEqual(
            setup.statusline_command({}, False, False, "/h/.claude/s.sh"),
            'bash "/h/.claude/s.sh"',
        )


class BudgetTests(unittest.TestCase):
    def test_missing_file_gets_only_the_budget(self):
        self.assertEqual(
            setup.merge_budget({}, 0.02), {"skillListingBudgetFraction": 0.02}
        )

    def test_lower_value_is_raised_and_other_keys_kept(self):
        self.assertEqual(
            setup.merge_budget(
                {"model": "x", "skillListingBudgetFraction": 0.01}, 0.02
            ),
            {"model": "x", "skillListingBudgetFraction": 0.02},
        )

    def test_equal_or_higher_value_changes_nothing(self):
        self.assertIsNone(
            setup.merge_budget({"skillListingBudgetFraction": 0.02}, 0.02)
        )
        self.assertIsNone(
            setup.merge_budget({"skillListingBudgetFraction": 0.05}, 0.02)
        )

    def test_invalid_json_reads_as_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text("{not json", encoding="utf-8")
            self.assertIsNone(setup.read_settings(path))
            self.assertEqual(setup.read_settings(Path(tmp) / "missing.json"), {})


class WriteSettingsTests(unittest.TestCase):
    def test_write_keeps_other_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text('{"model": "x"}', encoding="utf-8")
            setup.write_settings(
                path, setup.merge_budget(setup.read_settings(path), 0.02)
            )
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"model": "x", "skillListingBudgetFraction": 0.02},
            )

    def test_failed_write_leaves_the_old_file_whole(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text('{"model": "x"}', encoding="utf-8")
            with patch.object(setup.os, "replace", side_effect=OSError("disk full")):
                with self.assertRaises(OSError):
                    setup.write_settings(path, {"model": "y"})
            self.assertEqual(path.read_text(encoding="utf-8"), '{"model": "x"}')


class ExitCodeTests(unittest.TestCase):
    def run_main(self, install_code):
        """main with a terminal, the marketplace added, every tool found, and every yes given,
        where `claude plugin install` exits with install_code."""

        def fake_run(cmd, timeout=60):
            if cmd[:3] == ["claude", "plugin", "install"]:
                return install_code, "boom" if install_code else ""
            if cmd[:2] == ["claude", "--version"]:
                return 0, "2.1.300 (Claude Code)"
            return 1, ""

        def fake_json(*args):
            return [{"name": setup.MARKETPLACE}] if "marketplace" in args else []

        with tempfile.TemporaryDirectory() as tmp:
            with (
                patch.object(setup.sys.stdin, "isatty", return_value=True),
                patch.object(setup.shutil, "which", return_value="x"),
                patch.object(setup, "run", fake_run),
                patch.object(setup, "claude_json", fake_json),
                patch.object(setup, "probe", return_value=(True, "1.0")),
                patch.object(setup, "ask", return_value=True),
                patch.object(setup, "settings_path", return_value=Path(tmp) / "s.json"),
                patch("builtins.print"),
            ):
                return setup.main(["--plugins", "ceh-ui-design"])

    def test_failed_plugin_install_exits_1(self):
        self.assertEqual(self.run_main(1), 1)

    def test_successful_run_exits_0(self):
        self.assertEqual(self.run_main(0), 0)


class VersionTests(unittest.TestCase):
    def test_python3_probe_output_meets_its_floor(self):
        self.assertEqual(setup.version_of("3.13\n"), (3, 13))
        self.assertTrue(
            setup.version_of("3.13") >= setup.TOOLS["python3"]["min_version"]
        )
        self.assertFalse(
            setup.version_of("3.9") >= setup.TOOLS["python3"]["min_version"]
        )

    def test_node_output(self):
        self.assertEqual(setup.version_of("v18.19.1"), (18, 19))


if __name__ == "__main__":
    unittest.main()
