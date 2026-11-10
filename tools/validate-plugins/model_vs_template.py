# /// script
# requires-python = ">=3.10"
# dependencies = ["pydantic>=2,<3", "pyyaml>=6,<7"]
# ///
"""Check each YAML format's template against its model: the same keys, nested lists included.

    uv run --script tools/validate-plugins/model_vs_template.py <repo root>

Prints one `<template>: <key path>: <problem>` line per mismatch and exits 1 when there is any.
Run by the uv part of checks/artifact_models.py, which needs uv for pydantic.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import yaml


def load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # so pydantic resolves the model's string annotations
    spec.loader.exec_module(mod)
    return mod


def resolve(schema: dict, defs: dict, tmpl=None) -> dict:
    """Follow a $ref, pick the non-null branch of an Optional, and pick the branch of a
    discriminated union (`oneOf`) whose `state` constant is the template's `state`."""
    if "$ref" in schema:
        schema = defs[schema["$ref"].rsplit("/", 1)[-1]]
    for branch in schema.get("anyOf", []):
        if branch.get("type") != "null":
            return resolve(branch, defs, tmpl)
    if "oneOf" in schema and isinstance(tmpl, dict):
        for branch in schema["oneOf"]:
            branch = resolve(branch, defs)
            if branch.get("properties", {}).get("state", {}).get("const") == tmpl.get(
                "state"
            ):
                return branch
    return schema


def compare(tmpl, schema: dict, defs: dict, path: str, errors: list[str]) -> None:
    schema = resolve(schema, defs, tmpl)
    if isinstance(tmpl, dict):
        props = schema.get("properties", {})
        if set(tmpl) != set(props):
            missing = sorted(set(props) - set(tmpl))
            extra = sorted(set(tmpl) - set(props))
            errors.append(
                f"{path or '(top level)'}: missing {missing}, not in the model {extra}"
            )
        for key in set(tmpl) & set(props):
            compare(
                tmpl[key], props[key], defs, f"{path}.{key}" if path else key, errors
            )
    elif isinstance(tmpl, list) and tmpl and "items" in schema:
        compare(tmpl[0], schema["items"], defs, f"{path}[]", errors)


def main(root: Path) -> int:
    failed = False
    for model_path in sorted(root.glob("plugins/**/references/*-model.py")):
        name = model_path.name[: -len("-model.py")]
        template = model_path.parent.parent / "assets" / f"{name}.template.yaml"
        if not template.is_file():
            continue  # checks/artifact_models.py reports a missing template
        schema = load(model_path).MODEL.model_json_schema(by_alias=True)
        errors: list[str] = []
        compare(
            yaml.safe_load(template.read_text(encoding="utf-8")),
            schema,
            schema.get("$defs", {}),
            "",
            errors,
        )
        rel = template.relative_to(root).as_posix()
        for e in errors:
            print(f"{rel}: {e}")
        failed |= bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(Path(sys.argv[1])))
