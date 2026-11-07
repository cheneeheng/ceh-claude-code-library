"""artifact-models: each YAML format's `<name>-model.py` sits beside its `<name>-schema.md`, with
`../assets/<name>.template.yaml`, and every copy of a model, of `artifact.py`, and of the two
artifact hooks is byte-identical across plugins. With uv, each template's keys must also be
exactly its model's, through `model_vs_template.py`, and each `product/plans/*.yaml` must pass
`artifact.py check`, so its generated Markdown is not stale."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from collections import defaultdict

from common import REPO, fail, main, plugin_dirs, rel

MODEL_SUFFIX = "-model.py"
# The scripts every plugin carrying a model ships, which must not drift between plugins.
SHARED_SCRIPTS = ("artifact.py", "artifact-render-hook.py", "generated-md-guard.py")


def check() -> None:
    copies = defaultdict(list)
    for d in plugin_dirs():
        models = sorted(d.glob("**/references/*" + MODEL_SUFFIX))
        for model in models:
            name = model.name[: -len(MODEL_SUFFIX)]
            if not (model.parent / f"{name}-schema.md").is_file():
                fail(rel(model), f"no {name}-schema.md beside it")
            if not (model.parent.parent / "assets" / f"{name}.template.yaml").is_file():
                fail(rel(model), f"no ../assets/{name}.template.yaml")
            copies[model.name].append(model)
        for script in SHARED_SCRIPTS:
            path = d / "scripts" / script
            if path.is_file():
                copies[script].append(path)
            elif models:
                fail(rel(d), f"carries a model but no scripts/{script}")

    for name, paths in copies.items():
        first = paths[0].read_bytes()
        for other in paths[1:]:
            if other.read_bytes() != first:
                fail(rel(other), f"differs from its copy {rel(paths[0])}")

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
    cli = (
        REPO
        / "plugins"
        / "standalone"
        / "ceh-build-planning"
        / "scripts"
        / "artifact.py"
    )
    for plan in sorted((REPO / "product" / "plans").glob("*.yaml")):
        r = subprocess.run(
            [uv, "run", "--quiet", "--script", str(cli), "check", str(plan)],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )  # fmt: skip
        if r.returncode:
            fail(rel(plan), (r.stdout or r.stderr).strip()[-300:])


if __name__ == "__main__":
    sys.exit(main(check))
