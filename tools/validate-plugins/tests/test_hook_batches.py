import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import common
import hooks


class HookBatchTests(unittest.TestCase):
    def tearDown(self):
        common.errors.clear()

    def test_batches_isolate_roots_preserve_sequences_and_report_every_failure(self):
        seen = []
        coordinator = threading.get_ident()
        with tempfile.TemporaryDirectory() as tmp:
            plugins = []
            for name, script in (("one", "a.py"), ("two", "b.py")):
                plugin = Path(tmp) / name
                (plugin / "scripts").mkdir(parents=True)
                (plugin / "hooks").mkdir()
                (plugin / "hooks/hooks.json").write_text(
                    json.dumps({"command": f"python /scripts/{script}"}),
                    encoding="utf-8",
                )
                (plugin / "scripts" / script).write_text(
                    "import json,sys\nfrom pathlib import Path\n"
                    "p=Path(json.load(sys.stdin)['path'])\n"
                    "n=int(p.read_text()) if p.exists() else 0\n"
                    "p.write_text(str(n+1))\n",
                    encoding="utf-8",
                )
                plugins.append(plugin)

            def fixtures(root):
                def after(index, path, count):
                    self.assertEqual(path.read_text(), str(count))
                    seen.append((index, root))

                return [
                    {
                        "script": "one/a.py",
                        "stdin": {"path": str(root / "a")},
                        "before": lambda: self.assertFalse((root / "a").exists()),
                        "out": "missing-0",
                        "after": lambda: after(0, root / "a", 1),
                    },
                    {
                        "script": "two/b.py",
                        "stdin": {"path": str(root / "b")},
                        "repeat": 2,
                        "out": "missing-1",
                        "after": lambda: after(1, root / "b", 2),
                    },
                    {
                        "script": "one/a.py",
                        "stdin": {"path": str(root / "a")},
                        "before": lambda: self.assertEqual(
                            (root / "a").read_text(), "1"
                        ),
                        "out": "missing-2",
                        "after": lambda: after(2, root / "a", 2),
                    },
                ]

            def fail(where, message):
                self.assertEqual(threading.get_ident(), coordinator)
                common.fail(where, message)

            with (
                patch.object(hooks, "plugin_dirs", return_value=plugins),
                patch.object(hooks, "hook_fixtures", side_effect=fixtures),
                patch.object(hooks, "check_bash", return_value=None),
                patch.object(hooks.os, "cpu_count", return_value=2),
                patch.object(hooks, "fail", side_effect=fail),
            ):
                errors = common.run_check(hooks.check)

        self.assertEqual(sorted(i for i, root in seen), [0, 1, 2])
        roots = dict(seen)
        self.assertEqual(roots[0], roots[2])
        self.assertNotEqual(roots[0], roots[1])
        self.assertEqual(len(errors), 3)
        for i, error in enumerate(errors):
            self.assertIn(f"hook fixture {i}", error)
            self.assertIn(f"missing-{i}", error)


if __name__ == "__main__":
    unittest.main()
