#!/usr/bin/env python3
"""Find the ceh-* plugins that are stale against Claude's per-model prompting guides.

Stdlib-only, no LLM. Run from anywhere: `python .claude/skills/model-audit/scripts/detect.py [--write]`.
Prints JSON: the guide slugs new since the last run, the in-use slugs, and every stale plugin.

  1. Fetch the best-practices page and extract every `prompting-claude-<slug>` link.
     Zero links is a hard failure, so a page redesign cannot pass silently.
  2. Diff against known-model-guides.json (`--write` saves the union back).
  3. A plugin is stale when its `.claude-plugin/tuning.json` `checked-against` misses an
     in-use slug, or a pinned agent/skill's resolved model differs from its `tuned-for`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[2]
ASSETS = SKILL_DIR / "assets"
BASE = "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering"
GUIDES_PAGE = f"{BASE}/claude-prompting-best-practices"
GUIDE_LINK = re.compile(r"/prompt-engineering/prompting-claude-([a-z]+(?:-\d+)+)")
SLUG = re.compile(r"^([a-z]+)-(\d+(?:-\d+)*)$")
KNOWN = ASSETS / "known-model-guides.json"
IN_USE = ASSETS / "models-in-use.json"


def guide_url(slug: str) -> str:
    return f"{BASE}/prompting-claude-{slug}"


def fetch_slugs() -> set[str]:
    req = urllib.request.Request(GUIDES_PAGE, headers={"User-Agent": "ceh-model-audit"})
    with urllib.request.urlopen(req, timeout=60) as r:
        slugs = set(GUIDE_LINK.findall(r.read().decode("utf-8", "replace")))
    if not slugs:
        sys.exit(f"FAIL: no prompting-claude-<slug> links found on {GUIDES_PAGE}")
    return slugs


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def version(slug: str) -> tuple[str, tuple[int, ...]]:
    m = SLUG.match(slug)
    if not m:
        return slug, ()
    return m.group(1), tuple(int(n) for n in m.group(2).split("-"))


def resolve(model: str, known: list[str]) -> str | None:
    """Map a model value to a guide slug: a family alias resolves to its newest guide."""
    v = re.sub(r"\[.*\]$", "", model.strip().lower()).removeprefix("claude-")
    v = re.sub(r"-\d{8}$", "", v)
    if v in known:
        return v
    family = [s for s in known if version(s)[0] == v]
    return max(family, key=lambda s: version(s)[1]) if family else None


def in_use(known: list[str]) -> list[str]:
    """models-in-use.json entries are slugs or family aliases; absent means every guide."""
    entries = load_json(IN_USE, None)
    if entries is None:
        return sorted(known)
    return sorted({s for e in entries if (s := resolve(e, known))})


def plugin_dirs() -> list[Path]:
    return sorted(p for p in (REPO / "plugins/standalone").glob("ceh-*") if p.is_dir())


def frontmatter_model(path: Path) -> str | None:
    m = re.match(r"---\r?\n(.*?)\r?\n---", path.read_text(encoding="utf-8"), re.S)
    found = m and re.search(r"^model:[ \t]*['\"]?([^'\"\r\n]+)", m.group(1), re.M)
    model = found.group(1).strip() if found else None
    return None if model in (None, "inherit") else model


def pinned_files(plugin_dir: Path) -> dict[str, str]:
    """{plugin-relative path: frontmatter model} for every pinned agent and skill."""
    docs = sorted(plugin_dir.glob("agents/*.md")) + sorted(
        plugin_dir.glob("skills/*/SKILL.md")
    )
    return {
        d.relative_to(plugin_dir).as_posix(): m
        for d in docs
        if (m := frontmatter_model(d))
    }


def load_tuning(plugin_dir: Path) -> dict:
    return load_json(
        plugin_dir / ".claude-plugin/tuning.json",
        {"targets": "general", "checked-against": [], "pinned": {}},
    )


def generation(slug: str, known: list[str]) -> list[str]:
    """`slug` and its same-generation predecessors (opus-5-5 -> opus-5, opus-5-5), oldest first.

    Each guide is a diff from its predecessor, so the newest alone misses what earlier point
    releases of its generation introduced. Older generations are skipped as superseded.
    """
    family, top = version(slug)
    return sorted(
        (
            s
            for s in known
            if version(s)[0] == family
            and version(s)[1][:1] == top[:1]
            and version(s)[1] <= top
        ),
        key=lambda s: version(s)[1],
    )


def guide_chain(tuned_for: str | None, target: str, known: list[str]) -> list[str]:
    """Guides from just after `tuned_for` up to `target` in one family, oldest first."""
    family, top = version(target)
    old_family, low = version(tuned_for) if tuned_for else (None, ())
    if old_family != family:
        return generation(target, known)
    return sorted(
        (s for s in known if version(s)[0] == family and low < version(s)[1] <= top),
        key=lambda s: version(s)[1],
    )


def plugin_state(
    plugin_dir: Path, known: list[str], using: list[str], force: bool = False
) -> dict:
    """State of one plugin.

    `missing`: in-use slugs not yet checked, the audit trigger. `guides`: those slugs with their
    same-generation predecessors, minus what is checked, the guides to act on. `other-guides`: the
    in-use generations of the other families, which an unpinned change must not hurt. `force` ignores
    `checked-against` and re-tunes pinned files whose last proposal is still unreviewed.
    """
    tuning = load_tuning(plugin_dir)
    checked = set() if force else set(tuning.get("checked-against", []))
    missing = [s for s in using if s not in checked]
    guides = {g for s in missing for g in generation(s, known)} - checked
    stale_families = {version(s)[0] for s in missing}
    others = {
        g
        for s in using
        if version(s)[0] not in stale_families
        for g in generation(s, known)
    }
    pinned = []
    for path, model in pinned_files(plugin_dir).items():
        entry = tuning.get("pinned", {}).get(path, {})
        tuned_for = entry.get("tuned-for")
        target = resolve(model, known)
        proposed = not force and entry.get("proposed-for") == target
        pinned.append(
            {
                "file": path,
                "frontmatter-model": model,
                "target": target,
                "tuned-for": tuned_for,
                "stale": target is not None and target != tuned_for and not proposed,
                "chain": guide_chain(tuned_for, target, known) if target else [],
            }
        )
    return {
        "plugin": plugin_dir.name,
        "missing": missing,
        "guides": sorted(guides, key=version),
        "other-guides": sorted(others, key=version),
        "pinned": pinned,
    }


def stale_plugins(known: list[str]) -> list[dict]:
    using = in_use(known)
    states = [plugin_state(d, known, using) for d in plugin_dirs()]
    return [s for s in states if s["missing"] or any(p["stale"] for p in s["pinned"])]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--write", action="store_true", help="save new slugs to known-model-guides.json"
    )
    args = ap.parse_args()

    known = load_json(KNOWN, [])
    fetched = fetch_slugs()
    new = sorted(fetched - set(known))
    known = sorted(fetched | set(known), key=lambda s: version(s))
    if args.write and new:
        KNOWN.write_text(json.dumps(known, indent=2) + "\n", encoding="utf-8")
    report = {"new-guides": new, "in-use": in_use(known), "stale": stale_plugins(known)}
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
