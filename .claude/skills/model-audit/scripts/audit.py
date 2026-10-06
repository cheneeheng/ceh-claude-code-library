#!/usr/bin/env python3
"""Audit stale ceh-* plugins with headless Claude Code runs and record the results.

Run from anywhere:
  python .claude/skills/model-audit/scripts/audit.py [--plugins ceh-a ceh-b] [--model M --effort E] [--apply]

Per plugin, at most `jobs` plugins at a time because every run shares one rate limit:
  1. `/doctor prompt-audit <plugin>`, saved raw to audits/<date>/<plugin>.doctor.md.
  2. A filter pass that keeps only removals the missing model guides back.
  3. A tuning pass for each stale pinned agent or skill, with the override model.
Then it writes audits/<date>/<plugin>.md, updates tuning.json (never `tuned-for`), runs
`claude plugin validate <plugin> --strict`, and writes audits/<date>/SUMMARY.md.
Plugin files are edited only with --apply.
"""

from __future__ import annotations

import argparse
import datetime
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import detect

REPO = detect.REPO
CLAUDE = shutil.which("claude") or "claude"
CONFIG = detect.ASSETS / "config.json"
PROMPTS = detect.SKILL_DIR / "references"
READ_TOOLS = ["Read", "Glob", "Grep", "WebFetch(domain:platform.claude.com)"]
TUNING_KEYS = [
    "targets",
    "checked-against",
    "pinned",
    "last-audited",
    "audited-with",
    "audit-model",
    "audit-model-effort",
]


def claude(
    prompt: str, model: str, effort: str, tools: list[str] = ()
) -> tuple[str, str, int]:
    """One headless run: (final text, slug of the model that actually ran, denied tool calls)."""
    cmd = [
        CLAUDE,
        "-p",
        prompt,
        "--model",
        model,
        "--effort",
        effort,
        "--output-format",
        "json",
        "--no-session-persistence",
    ]
    if tools:
        cmd += ["--allowedTools", *tools]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=REPO)
    try:
        out = json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"claude exited {r.returncode}: {(r.stderr or r.stdout).strip()[:500]}"
        )
    if out.get("is_error"):
        raise RuntimeError(
            f"claude run failed: {out.get('result') or out.get('subtype')}"
        )
    usage = out.get("modelUsage") or {model: {}}
    main_model = max(usage, key=lambda m: usage[m].get("outputTokens", 0))
    used = usage[main_model].get("canonicalModel", main_model).removeprefix("claude-")
    return out.get("result", "").strip(), used, len(out.get("permission_denials", []))


def render(template: str, **values: str) -> str:
    return (PROMPTS / template).read_text(encoding="utf-8").format(**values)


def guide_list(slugs: list[str]) -> str:
    return "\n".join(f"- {detect.guide_url(s)}" for s in slugs)


def audit_plugin(state: dict, run: dict) -> dict:
    name = state["plugin"]
    pdir = REPO / "plugins/standalone" / name
    rel = pdir.relative_to(REPO).as_posix()
    tuning = detect.load_tuning(pdir)
    if run["apply"]:
        apply_note = f"Apply each kept edit with the Edit tool, editing only files under `{rel}`."
        tools = READ_TOOLS + [f"Edit(./{rel}/**)"]
    else:
        apply_note, tools = "Do not edit any file.", READ_TOOLS
    parts = [
        f"# Model audit: {name}",
        "",
        f"- Date: {run['date']}",
        f"- {run['cc_version']}",
        f"- Edits applied: {'yes' if run['apply'] else 'no'}",
    ]
    denied = 0
    tuned = []

    guides = state["missing"]
    if guides:
        # A new model generation (a slug with no minor version, e.g. opus-6) gets the stronger pair.
        generation = any(len(detect.version(s)[1]) == 1 for s in guides)
        model, effort = (
            run["override"] if generation and not run["forced"] else run["default"]
        )
        print(f"[{name}] /doctor prompt-audit with {model}/{effort}", file=sys.stderr)
        raw, _, _ = claude(f"/doctor prompt-audit {rel}", model, effort)
        raw_path = run["out_dir"] / f"{name}.doctor.md"
        raw_path.write_text(raw + "\n", encoding="utf-8")
        pinned = ", ".join(f"`{p['file']}`" for p in state["pinned"]) or "none"
        text, used, n = claude(
            render(
                "filter.md",
                raw_report=raw_path.relative_to(REPO).as_posix(),
                plugin_dir=rel,
                guide_urls=guide_list(guides),
                pinned_files=pinned,
                apply_instruction=apply_note,
            ),
            model,
            effort,
            tools,
        )
        denied += n
        parts += [
            "",
            f"## Unpinned audit against {', '.join(guides)}",
            "",
            f"Audit model: {used}, effort: {effort}. Raw output: [{raw_path.name}]({raw_path.name}).",
            "",
            text,
        ]
        tuning["checked-against"] = sorted(
            set(tuning["checked-against"]) | set(guides), key=detect.version
        )
        tuning.update(
            {
                "last-audited": run["date"],
                "audited-with": run["cc_version"],
                "audit-model": used,
                "audit-model-effort": effort,
            }
        )

    old = tuning.get("pinned", {})
    tuning["pinned"] = {}
    for p in state["pinned"]:
        prev = old.get(p["file"], {})
        entry = {
            "model": p["target"] or p["frontmatter-model"],
            "tuned-for": prev.get("tuned-for"),
        }
        entry |= {
            k: prev[k]
            for k in ("proposed-for", "tuned-by-model", "tuned-by-model-effort")
            if k in prev
        }
        if p["stale"]:
            model, effort = run["override"]
            print(f"[{name}] tuning {p['file']} with {model}/{effort}", file=sys.stderr)
            text, used, n = claude(
                render(
                    "tune.md",
                    file=f"{rel}/{p['file']}",
                    target=p["target"],
                    frontmatter_model=p["frontmatter-model"],
                    tuned_for=p["tuned-for"] or "never",
                    guide_urls=f"- {detect.GUIDES_PAGE}\n" + guide_list(p["chain"]),
                    apply_instruction=apply_note,
                ),
                model,
                effort,
                tools,
            )
            denied += n
            entry |= {
                "proposed-for": p["target"],
                "tuned-by-model": used,
                "tuned-by-model-effort": effort,
            }
            tuned.append(p["file"])
            parts += [
                "",
                f"## Pinned tuning: `{p['file']}` for {p['target']}",
                "",
                f"Tuning model: {used}, effort: {effort}. Last tuned for: {p['tuned-for'] or 'never'}.",
                "",
                text,
            ]
        elif p["target"] is None:
            parts += [
                "",
                f"## Pinned: `{p['file']}`",
                "",
                f"No prompting guide exists for `{p['frontmatter-model']}`, so it was not tuned.",
            ]
        tuning["pinned"][p["file"]] = entry

    if denied:
        parts.insert(
            5,
            f"- WARNING: {denied} tool call(s) were denied, so the report may be incomplete.",
        )
    (run["out_dir"] / f"{name}.md").write_text(
        "\n".join(parts) + "\n", encoding="utf-8"
    )
    ordered = {k: tuning[k] for k in TUNING_KEYS if k in tuning}
    (pdir / ".claude-plugin/tuning.json").write_text(
        json.dumps(ordered, indent=2) + "\n", encoding="utf-8"
    )
    v = subprocess.run(
        [CLAUDE, "plugin", "validate", rel, "--strict"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=REPO,
    )
    return {
        "plugin": name,
        "guides": guides,
        "tuned": tuned,
        "valid": v.returncode == 0,
        "validate-output": (v.stdout + v.stderr).strip(),
    }


def safe_audit(state: dict, run: dict) -> dict:
    try:
        return audit_plugin(state, run)
    except Exception as e:  # one failed plugin must not sink the others
        return {"plugin": state["plugin"], "error": str(e)}


def write_summary(results: list[dict], run: dict, repo_valid: bool) -> Path:
    lines = [
        f"# Model audit {run['date']}",
        "",
        f"{run['cc_version']}. Edits applied: {'yes' if run['apply'] else 'no'}.",
        "",
        "| Plugin | Report | Guides audited | Pinned files tuned | Strict validate |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in results:
        if "error" in r:
            lines.append(f"| {r['plugin']} | - | - | - | ERROR: {r['error'][:200]} |")
            continue
        lines.append(
            f"| {r['plugin']} | [{r['plugin']}.md]({r['plugin']}.md) | {', '.join(r['guides']) or '-'} "
            f"| {', '.join(r['tuned']) or '-'} | {'pass' if r['valid'] else 'FAIL'} |"
        )
    lines += [
        "",
        f"`validate.py`: {'pass' if repo_valid else 'FAIL'}.",
        "",
        "## Reviewer checklist",
        "",
        "- Keep or drop each proposed edit. Without `--apply`, apply the kept ones from the reports.",
        "- For each plugin whose edits you keep: PATCH-bump `plugin.json` and `marketplace.json`, "
        "and update its `docs/PLUGIN_VERSIONS.md` row.",
        "- Before merging, add this PR's `CHANGELOG.md` entry under the date it was opened.",
        "- For each pinned file whose tuning you accept: set its `tuned-for` to its `model` in "
        "`tuning.json`.",
        "- Optional: run `claude plugin eval` from a plugin root before merging.",
    ]
    path = run["out_dir"] / "SUMMARY.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--plugins", nargs="+", help="audit these plugins even if not stale"
    )
    ap.add_argument("--model", help="unpinned-audit model (default from config.json)")
    ap.add_argument("--effort", help="unpinned-audit effort")
    ap.add_argument(
        "--tune-model", help="pinned-tuning model (override pair in config.json)"
    )
    ap.add_argument("--tune-effort", help="pinned-tuning effort")
    ap.add_argument("--jobs", type=int, help="plugins audited in parallel")
    ap.add_argument(
        "--apply", action="store_true", help="apply proposed edits to plugin files"
    )
    args = ap.parse_args()

    cfg = detect.load_json(CONFIG, {})
    known = detect.load_json(detect.KNOWN, [])
    if not known:
        sys.exit("FAIL: known-model-guides.json is empty - run detect.py --write first")
    using = detect.in_use(known)
    if args.plugins:
        states = []
        for name in args.plugins:
            pdir = REPO / "plugins/standalone" / name
            if not pdir.is_dir():
                sys.exit(
                    f"FAIL: no plugin directory {pdir.relative_to(REPO).as_posix()}"
                )
            state = detect.plugin_state(pdir, known, using, force=True)
            state["missing"] = (
                state["missing"] or using
            )  # a named plugin is always re-audited
            states.append(state)
    else:
        states = detect.stale_plugins(known)
    if not states:
        print("Nothing stale.")
        return 0

    version = subprocess.run(
        [CLAUDE, "--version"], capture_output=True, text=True
    ).stdout.split()
    run = {
        "date": datetime.date.today().isoformat(),
        "cc_version": f"claude-code {version[0] if version else 'unknown'}",
        "apply": args.apply,
        "forced": bool(args.model or args.effort),
        "default": (
            args.model or cfg["default"]["model"],
            args.effort or cfg["default"]["effort"],
        ),
        "override": (
            args.tune_model or cfg["override"]["model"],
            args.tune_effort or cfg["override"]["effort"],
        ),
        "out_dir": REPO / "audits" / datetime.date.today().isoformat(),
    }
    run["out_dir"].mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(args.jobs or cfg.get("jobs", 3)) as pool:
        results = list(pool.map(lambda s: safe_audit(s, run), states))
    repo_valid = (
        subprocess.run(
            [sys.executable, "tools/validate-plugins/validate.py"], cwd=REPO
        ).returncode
        == 0
    )
    print(
        f"Summary: {write_summary(results, run, repo_valid).relative_to(REPO).as_posix()}"
    )
    ok = repo_valid and all(r.get("valid") for r in results)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
