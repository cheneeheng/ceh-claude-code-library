"""artifact-models: each YAML format's `<name>-model.py` sits beside its `<name>-schema.md`, with
`../assets/<name>.template.yaml`, and a plugin carrying a model ships `artifact.py` and the two
artifact hooks (the `copies` check keeps their copies identical), unless it is one of `READERS`. With uv, each template's keys
must also be exactly its model's, through `model_vs_template.py`, and each `product/plans/*.yaml`
must pass `artifact.py check`, so its generated Markdown is not stale."""

from __future__ import annotations

import importlib.util
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

from common import REPO, fail, main, plugin_dirs, rel

MODEL_SUFFIX = "-model.py"
# The scripts every plugin carrying a model ships, which must not drift between plugins.
SHARED_SCRIPTS = ("artifact.py", "artifact-render-hook.py", "generated-md-guard.py")
# Plugins whose skills only read a format (or, as write-fastapi-endpoints, render it themselves)
# carry the models in their skills and no hooks, per Phase 6 of
# product/plans/artifact-validation-formats.yaml.
READERS = {
    "ceh-every-session",
    "ceh-blog",
    "ceh-seo",
    "ceh-documentation",
    "ceh-python-service",
}
CLI = REPO / "plugins" / "standalone" / "ceh-build-planning" / "scripts" / "artifact.py"


def _survives_refused_read() -> None:
    """On Windows, reading the Markdown while another render renames over it is refused
    (product/fixes/render-reads-markdown-while-another-render-replaces-it.md): write_atomic
    must still write. artifact.py imports only the stdlib at the top, so this needs no uv."""
    spec = importlib.util.spec_from_file_location("artifact_cli", CLI)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with tempfile.TemporaryDirectory() as tmp:
        target = pathlib.Path(tmp) / "plan.md"
        target.write_text("old\n", encoding="utf-8")
        real = pathlib.Path.read_text

        def refused(self, *args, **kwargs):
            if self == target:
                raise PermissionError(13, "Permission denied", str(self))
            return real(self, *args, **kwargs)

        pathlib.Path.read_text = refused
        try:
            mod.write_atomic(target, "new\n")
            ok = real(target, encoding="utf-8") == "new\n"
        except Exception:
            ok = False
        finally:
            pathlib.Path.read_text = real
    if not ok:
        fail(rel(CLI), "write_atomic does not survive a refused read")


def check() -> None:
    _survives_refused_read()
    for d in plugin_dirs():
        models = sorted(d.glob("**/references/*" + MODEL_SUFFIX))
        for model in models:
            name = model.name[: -len(MODEL_SUFFIX)]
            if not (model.parent / f"{name}-schema.md").is_file():
                fail(rel(model), f"no {name}-schema.md beside it")
            if not (model.parent.parent / "assets" / f"{name}.template.yaml").is_file():
                fail(rel(model), f"no ../assets/{name}.template.yaml")
        for script in SHARED_SCRIPTS:
            path = d / "scripts" / script
            if models and d.name not in READERS and not path.is_file():
                fail(rel(d), f"carries a model but no scripts/{script}")

    # Comparing a template with its model needs pydantic, so it runs through uv: skipped without
    # uv, as shellcheck is in checks/scripts.py, but required in CI, which installs it.
    uv = shutil.which("uv")
    if not uv:
        if os.environ.get("CI"):
            fail(
                ".github/workflows/validate.yml",
                "uv is not installed, templates were not compared with their models",
            )
        else:
            print(
                "artifact-models: uv not installed, templates not compared with their models",
                file=sys.stderr,
            )
        return
    script = REPO / "tools" / "validate-plugins" / "model_vs_template.py"
    r = subprocess.run(
        [uv, "run", "--quiet", "--script", str(script), str(REPO)],
        capture_output=True, text=True, encoding="utf-8", timeout=120,
    )  # fmt: skip
    for line in r.stdout.splitlines():
        where, _, problem = line.partition(": ")
        fail(where, f"does not match its model: {problem}")
    if r.returncode not in (0, 1) or (r.returncode == 1 and not r.stdout.strip()):
        fail(rel(script), f"exited {r.returncode}: {r.stderr.strip()[-300:]}")

    # This repo's own plan/v2 plans: a hand edit to the YAML outside Claude Code leaves its
    # generated Markdown stale, which no hook sees.
    for plan in sorted((REPO / "product" / "plans").glob("*.yaml")):
        r = subprocess.run(
            [uv, "run", "--quiet", "--script", str(CLI), "check", str(plan)],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )  # fmt: skip
        if r.returncode:
            fail(rel(plan), (r.stdout or r.stderr).strip()[-300:])


if __name__ == "__main__":
    sys.exit(main(check))
