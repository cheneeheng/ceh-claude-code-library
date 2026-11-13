import datetime as dt
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "plugins/standalone/ceh-git-workflow/scripts/sync-agents-workspace.py"
)
spec = importlib.util.spec_from_file_location("workspace_sync", SCRIPT)
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class WorkspaceCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.top = Path(self.scratch.name)
        self.workspace = self.top / ".agents_workspace"
        self.directory = self.workspace / ".git"
        self.directory.mkdir(parents=True)
        self.pending = self.directory / "ceh-checkpoint-pending"

    def test_quoted_separator_in_subject_preserves_merge(self):
        for separator in (";", "|"):
            with self.subTest(separator=separator):
                sync.record_merge(
                    self.top,
                    self.workspace,
                    f"gh pr merge --subject 'fix{separator} ship' 12 --merge",
                )
                self.assertTrue((self.pending / "pr-12").exists())

    def test_quoted_merge_mention_is_not_a_command(self):
        sync.record_merge(self.top, self.workspace, "printf '%s' '; gh pr merge 12 ;'")
        self.assertFalse(self.pending.exists())

    def test_distinct_branch_references_do_not_overwrite_each_other(self):
        for branch in ("feat/a", "feat_a", "feat/b", "feat_b", "feat/A"):
            sync.record_merge(self.top, self.workspace, f"gh pr merge {branch}")
        self.assertEqual(len(list(self.pending.iterdir())), 5)

    def test_long_branch_reference_fits_a_pending_filename(self):
        branch = "a" * 130 + "/" + "b" * 130
        sync.record_merge(self.top, self.workspace, f"gh pr merge {branch}")
        self.assertEqual(len(list(self.pending.iterdir())), 1)

    def test_repeated_merge_event_does_not_repeat_a_checkpoint(self):
        sync.record_merge(self.top, self.workspace, "gh pr merge 12")
        result = subprocess.CompletedProcess(
            [],
            0,
            json.dumps(
                {
                    "state": "MERGED",
                    "number": 12,
                    "url": "https://github.com/example/project/pull/12",
                    "mergeCommit": {"oid": "merged-12"},
                    "mergedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
                }
            ),
            "",
        )

        def git(repo, *args):
            if args[0] == "rev-parse":
                return 0, str(self.directory)
            if args[0] == "log":
                return 0, "existing-checkpoint-commit"
            return 0, ""

        with (
            patch.object(sync, "git", side_effect=git) as commands,
            patch.object(sync.shutil, "which", return_value="stub-gh"),
            patch.object(sync.subprocess, "run", return_value=result),
        ):
            sync.checkpoints(
                self.top, self.workspace, "main", self.pending, "repeat", False
            )
        self.assertFalse(
            any(call.args[1] == "commit" for call in commands.call_args_list)
        )
        self.assertEqual(list(self.pending.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
