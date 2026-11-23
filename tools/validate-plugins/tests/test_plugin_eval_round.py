import contextlib
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
    / ".claude/skills/evaluate-plugin/scripts/plugin_eval_round.py"
)
spec = importlib.util.spec_from_file_location("plugin_eval_round", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ASSISTANT = {
    "type": "assistant",
    "message": {"content": [{"type": "text", "text": "done"}]},
}
GRADERS = [{"name": "fired", "passed": True, "explanation": "ok"}]


def lines(*events):
    return "\n".join(e if isinstance(e, str) else json.dumps(e) for e in events)


class PluginEvalRoundTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.top = Path(scratch.name)
        self.out = self.top / "flow" / "baseline"

    def trace(self, name, text):
        path = self.top / "runs" / name / "trace.jsonl"
        path.parent.mkdir(parents=True)
        if isinstance(text, bytes):
            path.write_bytes(text)
        else:
            path.write_text(text, "utf-8")
        return str(path)

    def rows(self, file="results.jsonl"):
        text = (self.out / file).read_text("utf-8")
        return [json.loads(line) for line in text.splitlines()]

    def convert(self, *runs, name="case"):
        aggregate = {"cases": [{"name": name, "arms": {"with": list(runs)}}]}
        with contextlib.redirect_stderr(io.StringIO()) as err:
            counts = mod.convert(aggregate, self.out)
        return counts, err.getvalue()

    def main(self, *argv, run_eval):
        base = ["--plugin", str(self.top), "--flow", str(self.out.parent)]
        with (
            patch.object(mod.sys, "argv", ["x", *base, "--variant", "baseline", *argv]),
            patch.object(mod, "run_eval", run_eval),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            return mod.main()

    def test_convert_skips_blank_and_malformed_transcript_lines(self):
        path = self.trace("a", lines("", "not json", {"type": "assistant"}, ASSISTANT))
        (rows, errors, _), _ = self.convert({"tracePath": path, "graders": GRADERS})
        self.assertEqual((rows, errors), (1, 0))
        self.assertEqual(self.rows()[0]["grade"]["fired"], 1)
        turns = json.loads((self.out / "traces" / "case_rep0.json").read_text("utf-8"))
        self.assertEqual(turns[-1], {"role": "assistant", "content": "done"})

    def test_convert_counts_a_null_cost_as_zero(self):
        (_, _, cost), _ = self.convert(
            {"costUsd": None, "judgeCostUsd": 0.5, "graders": GRADERS}
        )
        self.assertEqual(cost, 0.5)

    def test_convert_keeps_the_other_runs_when_one_cannot_be_read(self):
        bad = self.trace("bad", b"\xff\xfe\xff")
        good = self.trace("good", lines(ASSISTANT))
        (rows, errors, _), _ = self.convert(
            {"tracePath": bad, "graders": GRADERS},
            {"tracePath": good, "graders": GRADERS},
        )
        self.assertEqual((rows, errors), (1, 1))
        self.assertEqual(self.rows()[0]["rep"], 1)
        self.assertEqual(self.rows("errors.jsonl")[0]["rep"], 0)

    def test_convert_records_the_model_that_cost_most(self):
        result = {
            "type": "result",
            "modelUsage": {"helper": {"costUSD": 0.01}, "main": {"costUSD": 1.2}},
        }
        path = self.trace("a", lines(ASSISTANT, result))
        self.convert({"tracePath": path, "graders": GRADERS})
        row = self.rows()[0]
        self.assertEqual(row["model"], "main")
        self.assertEqual(row["models"], ["helper", "main"])

    def test_convert_removes_the_temp_dir_of_an_errored_run(self):
        root = Path(tempfile.mkdtemp(prefix="claude-eval-"))
        self.addCleanup(mod.shutil.rmtree, root, True)
        path = root / "run" / "trace.jsonl"
        path.parent.mkdir()
        path.write_text(lines(ASSISTANT), "utf-8")
        (rows, errors, _), _ = self.convert(
            {"tracePath": str(path), "graders": [], "error": "api"}
        )
        self.assertEqual((rows, errors), (0, 1))
        self.assertFalse(root.exists())

    def test_convert_warns_when_a_temp_dir_is_left(self):
        path = self.trace("a", lines(ASSISTANT))
        _, err = self.convert({"tracePath": path, "graders": GRADERS})
        self.assertIn("not removed", err)
        self.assertTrue(Path(path).exists())

    def test_a_rerun_that_fails_does_not_convert_the_previous_round(self):
        def finished(args, raw, extra):
            raw.mkdir(parents=True)
            run = {"graders": GRADERS}
            aggregate = {"cases": [{"name": "old", "arms": {"with": [run]}}]}
            (raw / "aggregate-result.json").write_text(json.dumps(aggregate), "utf-8")
            return 0

        self.assertEqual(self.main(run_eval=finished), 0)
        self.assertEqual(len(self.rows()), 1)
        (self.out / "traces" / "stale_rep9.json").write_text("[]", "utf-8")

        self.assertEqual(self.main(run_eval=lambda *a: 1), 2)
        self.assertFalse((self.out / "results.jsonl").exists())
        self.assertFalse((self.out / "traces" / "stale_rep9.json").exists())

    def test_summary_records_the_target_kind(self):
        def finished(args, raw, extra):
            raw.mkdir(parents=True)
            (raw / "aggregate-result.json").write_text('{"cases": []}', "utf-8")
            return 0

        self.assertEqual(self.main("--target", "hook", run_eval=finished), 0)
        summary = json.loads((self.out / "summary.json").read_text("utf-8"))
        self.assertEqual(summary["target"], "hook")

    def run_eval(self, which, extra=(), timeout=None, effect=None):
        args = mod.argparse.Namespace(
            plugin=self.top,
            runs=1,
            case=None,
            model=None,
            concurrency=None,
            max_cost_usd=None,
            timeout_s=timeout,
        )
        done = subprocess.CompletedProcess([], 0)
        with (
            patch.object(mod.shutil, "which", return_value=which),
            patch.object(
                mod.subprocess, "run", return_value=done, side_effect=effect
            ) as run,
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            code = mod.run_eval(args, self.out / "raw", list(extra))
        return code, run

    def test_run_eval_starts_claude_without_a_shell(self):
        code, run = self.run_eval("/bin/claude", timeout=5)
        self.assertEqual(code, 0)
        self.assertEqual(run.call_args.args[0][0], "/bin/claude")
        self.assertFalse(run.call_args.kwargs.get("shell"))
        self.assertEqual(run.call_args.kwargs.get("timeout"), 5)

    def test_run_eval_reports_a_missing_claude(self):
        code, run = self.run_eval(None)
        self.assertEqual(code, 2)
        run.assert_not_called()

    def test_run_eval_refuses_shell_characters_for_a_cmd_shim(self):
        code, run = self.run_eval("C:/bin/claude.cmd", extra=["--case", "a&b"])
        self.assertEqual(code, 2)
        run.assert_not_called()

    def test_run_eval_turns_a_timeout_into_a_failed_run(self):
        expired = subprocess.TimeoutExpired("claude", 5)
        code, _ = self.run_eval("/bin/claude", timeout=5, effect=expired)
        self.assertEqual(code, 124)


if __name__ == "__main__":
    unittest.main()
