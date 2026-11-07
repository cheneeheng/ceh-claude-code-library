# /// script
# requires-python = ">=3.10"
# dependencies = ["pydantic>=2,<3", "pyyaml>=6,<7"]
# ///
"""Check a YAML artifact against its model, or render its Markdown.

    uv run --script artifact.py check <file.yaml>
    uv run --script artifact.py render <file.yaml>

The model is `<name>-model.py` in a `references/` folder of this plugin, matched on the file's
`schema: <name>/v<N>` key. `check` also reports a `.md` beside the YAML that differs from its
rendering. `render` checks, then writes that `.md`.

Exit codes: 0 valid (and rendered), 1 errors as `<path>: <where>: <error>` lines, 2 any other
failure, 3 no model for the file's `<name>/v<N>`.
"""

from __future__ import annotations

import importlib.util
import os
import re
import sys
import tempfile
import time
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = re.compile(
    r"""^schema:\s*["']?([a-z0-9]+(?:-[a-z0-9]+)*)/v(\d+)["']?\s*$""", re.M
)
# A plain YAML scalar ends at ` #`, so the rest of the line is silently dropped as a comment.
COMMENT = re.compile(r"\s+#")


class NoModel(Exception):
    pass


def load_model(name: str, version: int):
    for path in sorted(PLUGIN_ROOT.glob(f"**/references/{name}-model.py")):
        spec = importlib.util.spec_from_file_location(f"{name}_model", path)
        mod = importlib.util.module_from_spec(spec)
        # Registered first, so pydantic can resolve the model's string annotations.
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        if mod.VERSION == version:
            return mod
        raise NoModel(
            f"{name}/v{version} not checked, this plugin knows {name}/v{mod.VERSION}"
        )
    raise NoModel(f"{name}/v{version} not checked, this plugin has no {name} model")


def cut_comments(text: str, node, yaml) -> list[str]:
    """Each plain scalar followed by a comment on its line: the value YAML kept is cut short."""
    lines, found, stack = text.splitlines(), [], [node]
    while stack:
        n = stack.pop()
        if isinstance(n, yaml.ScalarNode):
            rest = (
                lines[n.end_mark.line][n.end_mark.column :] if n.style is None else ""
            )
            if COMMENT.match(rest):
                found.append(
                    f"{n.end_mark.line + 1}:{n.end_mark.column + 1}: value cut at ' #', "
                    "quote it or write it as a | block"
                )
        elif isinstance(n, yaml.SequenceNode):
            stack.extend(n.value)
        elif isinstance(n, yaml.MappingNode):
            stack.extend(v for pair in n.value for v in pair)
    return sorted(found, key=lambda s: tuple(int(x) for x in s.split(":")[:2]))


def validate(path: Path):
    """Return (errors, model module, parsed artifact). Raises NoModel for an unknown version."""
    import yaml
    from pydantic import ValidationError

    text = path.read_text(encoding="utf-8")
    m = SCHEMA.search(text)
    if not m:
        return [f"{path}: no 'schema: <name>/v<N>' key"], None, None
    mod = load_model(m.group(1), int(m.group(2)))
    try:
        node = yaml.compose(text)
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        where = f"{mark.line + 1}:{mark.column + 1}" if mark else "?"
        return [f"{path}:{where}: {getattr(e, 'problem', None) or e}"], mod, None
    errors = [f"{path}:{c}" for c in cut_comments(text, node, yaml)]
    try:
        doc = mod.MODEL.model_validate(data)
    except ValidationError as e:
        for err in e.errors():
            loc = ".".join(str(x) for x in err["loc"]) or "(top level)"
            errors.append(f"{path}: {loc}: {err['msg']}")
        doc = None
    return errors, mod, (doc if not errors else None)


def write_atomic(path: Path, text: str) -> None:
    # The hook and the skill both render after a write, often at once. An unchanged file is left
    # alone, so the second render touches nothing.
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return
    # A temp file in the same folder, then a rename: a parallel render never leaves half a file.
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        # Windows refuses the rename while another process has the target open: retry briefly.
        for attempt in range(10):
            try:
                os.replace(tmp, path)
                return
            except PermissionError:
                if attempt == 9:
                    raise
                time.sleep(0.1)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] not in ("check", "render"):
        print("usage: artifact.py check|render <file.yaml>")
        return 2
    command, path = argv[0], Path(argv[1])
    try:
        errors, mod, doc = validate(path)
    except NoModel as e:
        print(f"{path}: {e}")
        return 3
    if errors:
        print("\n".join(errors))
        return 1
    md = path.with_suffix(".md")
    text = mod.render(doc, path.name)
    if command == "render":
        write_atomic(md, text)
    elif md.exists() and md.read_text(encoding="utf-8") != text:
        print(f"{md}: stale, run: artifact.py render {path}")
        return 1
    return 0


if __name__ == "__main__":
    # A Windows console or pipe defaults to cp1252, which cannot print every character a plan holds.
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:  # anything unexpected is exit 2, never an empty exit 1
        print(f"artifact.py failed: {type(e).__name__}: {e}")
        sys.exit(2)
