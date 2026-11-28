import datetime as dt
import importlib.util
import io
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

    def test_command_without_a_merge_starts_no_git_process(self):
        payload = io.StringIO(
            json.dumps({"cwd": str(self.top), "tool_input": {"command": "ls"}})
        )
        with (
            patch.object(sync, "git") as commands,
            patch.object(sync.sys, "argv", ["sync", "merge"]),
            patch.object(sync.sys, "stdin", payload),
        ):
            sync.main()
        commands.assert_not_called()

    def test_shell_keyword_or_assignment_before_merge_is_recorded(self):
        for command in (
            "if true; then gh pr merge 12 --merge; fi",
            "GH_PAGER= gh pr merge 13 --merge",
        ):
            sync.record_merge(self.top, self.workspace, command)
        self.assertEqual(
            sorted(entry.name for entry in self.pending.iterdir()), ["pr-12", "pr-13"]
        )

    def test_unexpanded_reference_records_the_current_branch(self):
        for command in (
            "N=$(gh pr view --json number -q .number) && gh pr merge $N --merge",
            'gh pr merge "$N" --merge',
            "gh pr merge ${N} --merge",
            "gh pr merge `echo 5` --merge",
            "gh pr merge $(gh pr view --json number -q .number) --merge",
        ):
            with self.subTest(command=command):
                with patch.object(sync, "current_branch", return_value="feat/x"):
                    sync.record_merge(self.top, self.workspace, command)
                (entry,) = self.pending.iterdir()
                self.assertEqual(entry.read_text().splitlines()[1], "feat/x")
                entry.unlink()

    def test_quoted_merge_mention_is_not_a_command(self):
        sync.record_merge(self.top, self.workspace, "printf '%s' '; gh pr merge 12 ;'")
        self.assertFalse(self.pending.exists())

    def test_merge_in_another_repo_records_nothing(self):
        for flag in ("--repo o/r", "--repo=o/r", "-R o/r", "-Ro/r"):
            sync.record_merge(self.top, self.workspace, f"gh pr merge 12 {flag}")
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
                self.top, self.workspace, "main", self.pending, "repeat", False, ""
            )
        self.assertFalse(
            any(call.args[1] == "commit" for call in commands.call_args_list)
        )
        self.assertEqual(list(self.pending.iterdir()), [])

    def test_checkpoint_commit_leaves_uncommitted_workspace_files_alone(self):
        workspace = self.top / "real" / ".agents_workspace"
        workspace.mkdir(parents=True)
        for args in (
            ("init", "-q", "-b", "main"),
            ("config", "user.email", "test@example.com"),
            ("config", "user.name", "test"),
            ("commit", "-q", "--allow-empty", "-m", "root"),
        ):
            subprocess.run(["git", "-C", str(workspace), *args], check=True)
        (workspace / "plan.yaml").write_text("unrelated\n")
        (workspace / "staged.yaml").write_text("unrelated\n")
        sync.git(workspace, "add", "staged.yaml")
        pending = Path(sync.git(workspace, "rev-parse", "--absolute-git-dir")[1])
        pending /= "ceh-checkpoint-pending"
        sync.record_merge(self.top, workspace, "gh pr merge 12")
        view = json.dumps(
            {
                "state": "MERGED",
                "number": 12,
                "url": "https://github.com/example/project/pull/12",
                "mergeCommit": {"oid": "merged-12"},
                "mergedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
            }
        )
        run = subprocess.run

        def fake_run(command, *args, **kwargs):
            if command[0] == "stub-gh":
                return subprocess.CompletedProcess(command, 0, view, "")
            return run(command, *args, **kwargs)

        with (
            patch.object(sync.shutil, "which", return_value="stub-gh"),
            patch.object(sync.subprocess, "run", side_effect=fake_run),
        ):
            sync.checkpoints(self.top, workspace, "main", pending, "s", False, "")
        self.assertEqual(
            sync.git(workspace, "log", "-1", "--format=%s")[1],
            "chore(workspace): checkpoint source pr #12",
        )
        self.assertEqual(
            sync.git(workspace, "show", "--format=", "--name-only", "HEAD"), (0, "")
        )
        self.assertEqual(
            sync.git(workspace, "status", "--porcelain")[1],
            "A  staged.yaml\n?? plan.yaml",
        )

    def test_catch_up_reports_a_merge_that_times_out(self):
        workspace = self.top / "real" / ".agents_workspace"
        workspace.mkdir(parents=True)
        branch = "ceh-ws/main/feature"
        for args in (
            ("init", "-q", "-b", "main"),
            ("config", "user.email", "test@example.com"),
            ("config", "user.name", "test"),
            ("commit", "-q", "--allow-empty", "-m", "root"),
            ("branch", branch),
            ("commit", "-q", "--allow-empty", "-m", "main moves on"),
        ):
            subprocess.run(["git", "-C", str(workspace), *args], check=True)
        sync.git(workspace, "checkout", "-q", branch)
        sync.git(workspace, "commit", "-q", "--allow-empty", "-m", "branch work")
        sync.git(workspace, "checkout", "-q", "main")
        run = subprocess.run

        def slow_merge(command, *args, **kwargs):
            if "merge" in command and "--autostash" in command:
                raise subprocess.TimeoutExpired(command, kwargs.get("timeout"))
            return run(command, *args, **kwargs)

        with patch.object(sync.subprocess, "run", side_effect=slow_merge):
            failed = sync.catch_up(workspace, "main")
        self.assertEqual(failed, [branch])


def run_git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


class WorkspacePushTests(unittest.TestCase):
    """push() and the push triggers in main(), on a real bare remote."""

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        root = Path(self.scratch.name)
        self.remote = root / "remote.git"
        run_git(root, "init", "-q", "--bare", "-b", "main", str(self.remote))
        self.top = root / "project"
        self.top.mkdir()
        run_git(self.top, "init", "-q", "-b", "main")
        self.workspace = self.clone(self.top / ".agents_workspace")
        self.commit(self.workspace, "root.md", "root\n")
        run_git(self.workspace, "push", "-q", "-u", "origin", "main")

    def clone(self, path):
        run_git(self.remote.parent, "clone", "-q", str(self.remote), str(path))
        run_git(path, "config", "user.email", "test@example.com")
        run_git(path, "config", "user.name", "test")
        return path

    def commit(self, repo, name, text):
        (repo / name).write_text(text)
        run_git(repo, "add", name)
        run_git(repo, "commit", "-q", "-m", f"write {name}")

    def remote_head(self):
        return run_git(self.remote, "rev-parse", "main")

    def other_clone_pushes(self, name, text):
        other = self.clone(Path(self.scratch.name) / "other")
        self.commit(other, name, text)
        run_git(other, "push", "-q")

    def test_ahead_branch_is_pushed(self):
        self.commit(self.workspace, "plan.md", "plan\n")
        self.assertTrue(sync.push(self.workspace))
        self.assertEqual(
            self.remote_head(), run_git(self.workspace, "rev-parse", "HEAD")
        )

    def test_rejected_push_merges_the_remote_and_pushes_again(self):
        self.other_clone_pushes("other.md", "other\n")
        self.commit(self.workspace, "plan.md", "plan\n")
        self.assertTrue(sync.push(self.workspace))
        self.assertEqual(
            self.remote_head(), run_git(self.workspace, "rev-parse", "HEAD")
        )
        self.assertTrue((self.workspace / "other.md").exists())

    def test_conflicting_remote_is_aborted_and_nothing_is_pushed(self):
        self.other_clone_pushes("plan.md", "theirs\n")
        self.commit(self.workspace, "plan.md", "ours\n")
        before = run_git(self.workspace, "rev-parse", "HEAD")
        remote = self.remote_head()
        self.assertFalse(sync.push(self.workspace))
        self.assertEqual(run_git(self.workspace, "rev-parse", "HEAD"), before)
        self.assertEqual(run_git(self.workspace, "status", "--porcelain"), "")
        self.assertEqual((self.workspace / "plan.md").read_text(), "ours\n")
        self.assertEqual(self.remote_head(), remote)

    def test_uncommitted_files_stop_the_fetch_and_merge(self):
        self.other_clone_pushes("other.md", "other\n")
        self.commit(self.workspace, "plan.md", "plan\n")
        (self.workspace / "draft.md").write_text("editing\n")
        self.assertFalse(sync.push(self.workspace))
        self.assertFalse((self.workspace / "other.md").exists())
        self.assertEqual(
            run_git(self.workspace, "status", "--porcelain"), "?? draft.md"
        )

    def test_unreachable_remote_fails_without_a_merge(self):
        self.commit(self.workspace, "plan.md", "plan\n")
        before = run_git(self.workspace, "rev-parse", "HEAD")
        run_git(
            self.workspace, "fetch", "-q"
        )  # leaves a FETCH_HEAD a later merge could use
        run_git(self.workspace, "remote", "set-url", "origin", str(self.top / "gone"))
        with patch.object(sync, "git", wraps=sync.git) as commands:
            self.assertFalse(sync.push(self.workspace))
        pushes = [call for call in commands.call_args_list if "push" in call.args]
        self.assertEqual(len(pushes), 1)
        self.assertEqual(run_git(self.workspace, "rev-parse", "HEAD"), before)

    def test_branch_without_upstream_is_never_pushed(self):
        run_git(self.workspace, "branch", "--unset-upstream")
        self.commit(self.workspace, "plan.md", "plan\n")
        with patch.object(sync, "git", wraps=sync.git) as commands:
            self.assertFalse(sync.push(self.workspace))
        self.assertFalse(any("push" in call.args for call in commands.call_args_list))

    def run_main(self, event, hook):
        payload = io.StringIO(
            json.dumps({"cwd": str(self.top), "hook_event_name": hook})
        )
        out = io.StringIO()
        with (
            patch.object(sync, "detach") as detach,
            patch.object(sync.sys, "argv", ["sync", event]),
            patch.object(sync.sys, "stdin", payload),
            patch.object(sync.sys, "stdout", out),
        ):
            sync.main()
        return detach, out.getvalue()

    def test_stop_starts_a_push_worker_only_when_ahead(self):
        detach, _ = self.run_main("commit", "Stop")
        detach.assert_not_called()
        self.commit(self.workspace, "plan.md", "plan\n")
        detach, _ = self.run_main("commit", "Stop")
        detach.assert_called_once_with(
            self.workspace, "push-worker", str(self.workspace)
        )

    def test_session_start_notes_an_unpushed_branch(self):
        _, out = self.run_main("start", "SessionStart")
        self.assertNotIn("did not go through", out)
        self.commit(self.workspace, "plan.md", "plan\n")
        _, out = self.run_main("start", "SessionStart")
        self.assertIn("is 1 ahead and 0 behind origin/main", out)


class WorktreeCwdInsideWorkspaceTests(unittest.TestCase):
    """A worktree session whose cwd moved into its own nested .agents_workspace
    (fix/20261128-115700-workspace-sync-nested-cwd)."""

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        main = Path(self.scratch.name) / "project"
        main.mkdir()
        run_git(main, "init", "-q", "-b", "main")
        run_git(main, "config", "user.email", "test@example.com")
        run_git(main, "config", "user.name", "test")
        run_git(main, "commit", "-q", "--allow-empty", "-m", "root")
        self.workspace = main / ".agents_workspace"
        self.workspace.mkdir()
        run_git(self.workspace, "init", "-q", "-b", "project")
        run_git(self.workspace, "config", "user.email", "test@example.com")
        run_git(self.workspace, "config", "user.name", "test")
        run_git(self.workspace, "commit", "-q", "--allow-empty", "-m", "root")
        worktree = main / ".claude" / "worktrees" / "w1"
        run_git(main, "worktree", "add", "-q", "-b", "worktree-w1", str(worktree))
        self.branch = "ceh-ws/project/w1"
        self.nested = worktree / ".agents_workspace"
        run_git(
            self.workspace, "worktree", "add", "-q", "-b", self.branch, str(self.nested)
        )
        (self.nested / "doc.md").write_text("worker edit\n")

    def run_main(self, event, payload=None):
        argv = ["sync", event] + ([str(self.nested)] if event == "end-worker" else [])
        stdin = io.StringIO(json.dumps(payload or {}))
        with (
            patch.object(sync.sys, "argv", argv),
            patch.object(sync.sys, "stdin", stdin),
            patch.object(sync, "detach"),
        ):
            sync.main()

    def test_session_end_merges_the_branch_when_cwd_is_the_nested_workspace(self):
        run_git(self.nested, "add", "doc.md")
        run_git(self.nested, "commit", "-q", "-m", "worker edit")
        head = run_git(self.nested, "rev-parse", "HEAD")
        self.run_main("end-worker")
        merged = subprocess.run(
            [
                "git",
                "-C",
                str(self.workspace),
                "merge-base",
                "--is-ancestor",
                head,
                "project",
            ]
        )
        self.assertEqual(merged.returncode, 0)

    def test_stop_commits_the_change_when_cwd_is_the_nested_workspace(self):
        self.run_main("commit", {"cwd": str(self.nested), "hook_event_name": "Stop"})
        self.assertEqual(run_git(self.nested, "status", "--porcelain"), "")
        self.assertEqual(
            run_git(self.nested, "log", "-1", "--format=%s"),
            "chore(workspace): sync worktree w1",
        )


if __name__ == "__main__":
    unittest.main()
