"""artifact-paths: plugin files name product artifacts at their one path, and by their YAML.

A product artifact lives in `.agents_workspace/product/` (`decision-artifact-locations.md`), so a
root `product/` path is a stale location, and a format with a YAML source is referred to by its
`.yaml`, so a `.md` path of one is a stale reference. Lines the allowlist names are the exceptions
listed in `product/plans/consolidate-product-artifacts.yaml` under "References that stay Markdown".
"""

from __future__ import annotations

import fnmatch
import re
import sys

from common import REPO, fail, main, rel

ROOT = REPO / "plugins" / "standalone"
SUFFIXES = {".md", ".py", ".sh", ".yaml", ".yml", ".json", ".cjs", ".js"}
# A root product/ path: not preceded by a path character, so .agents_workspace/product/ passes.
ROOT_PRODUCT = re.compile(r"(?<![\w./-])product/[\w<*]")
# The .md path of a format with a YAML source: its folder and its stem.
P = r"[^\s`'\"()\[\]]*"
YAML_FORMAT_MD = re.compile(
    "|".join(
        (
            rf"product/plans/{P}\.md\b",
            r"product/(?:business/)?(?:VISION|STRATEGY|ARCHITECTURE|EVIDENCE|BUSINESS_PLAN)\.md\b",
            rf"product/fixes/{P}\.md\b",
            rf"product/retros/{P}repeat-mistake\.md\b",
            rf"product/qa/{P}QA_REPORT\.md\b",
            rf"product/perf/{P}\.md\b",
            rf"product/security-audit/{P}security-audit\.md\b",
            rf"product/ux-audits/{P}(?:UX_AUDIT|ERROR_MESSAGES)\.md\b",
            rf"handoff/{P}handoff\.md\b",
        )
    )
)
# (file glob under plugins/standalone/, line pattern, reason). A line matching both is allowed.
ALLOW = (
    (
        "ceh-build-plan/skills/implement-from-plan/SKILL.md",
        r"old root `product/plans/`",
        "the old-path sentence names the folder it reports",
    ),
    (
        "*/references/business-plan-schema.md",
        r"`product/BUSINESS_PLAN\.md`",
        "the old-location note that moves a business plan",
    ),
    (
        "ceh-build-plan/evals/*",
        r"product/plans/[\w-]+\.md",
        "the eval fixtures build plan/v1 plans, which are Markdown with no YAML",
    ),
    (
        "ceh-build-plan/scripts/build-record-guard.py",
        r"plans/\*\.md",
        "a plan/v1 plan is Markdown, and the guard covers its Built Phase lines",
    ),
    (
        "ceh-product-direction/skills/develop-business-plan/scripts/build-plan-html.cjs",
        r"BUSINESS_PLAN\.md",
        "the HTML build reads the generated Markdown",
    ),
    (
        "*/references/fix-record-model.py",
        r"\(\\\.agents_workspace/\)\?product/",
        "the model still checks a record saved with the old root paths",
    ),
)


def allowed(path: str, line: str) -> bool:
    return any(
        fnmatch.fnmatch(path, glob) and re.search(pattern, line)
        for glob, pattern, _ in ALLOW
    )


def check() -> None:
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.suffix not in SUFFIXES:
            continue
        sub = p.relative_to(ROOT).as_posix()
        if "/evals/results/" in f"/{sub}" or "__pycache__" in sub:
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for pat, what in (
                (ROOT_PRODUCT, "a root product/ path"),
                (YAML_FORMAT_MD, "the .md path of a YAML format"),
            ):
                if (m := pat.search(line)) and not allowed(sub, line):
                    fail(
                        f"{rel(p)}:{n}",
                        f"{what} '{m.group()}': name .agents_workspace/product/ and the .yaml",
                    )


if __name__ == "__main__":
    sys.exit(main(check))
