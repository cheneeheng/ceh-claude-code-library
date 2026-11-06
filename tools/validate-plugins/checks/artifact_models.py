"""artifact-models: each YAML format's `<name>-model.py` sits beside its `<name>-schema.md`, with
`../assets/<name>.template.yaml`, and every copy of a model, of `artifact.py`, and of the two
artifact hooks is byte-identical across plugins."""

from __future__ import annotations

import sys
from collections import defaultdict

from common import fail, main, plugin_dirs, rel

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


if __name__ == "__main__":
    sys.exit(main(check))
