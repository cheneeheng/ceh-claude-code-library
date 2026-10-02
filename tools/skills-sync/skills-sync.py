#!/usr/bin/env python3
"""skills-sync — copy Claude Code skills from a GitHub repo or local folder
into a project's .claude/skills/ directory.

Usage:
    skills-sync.py install (--repo owner/name [--ref REF] | --path DIR) \
        [--skills a,b|all] [--target DIR] [--token TOKEN]
    skills-sync.py update [--skills a,b|all] [--target DIR] [--token TOKEN]
    skills-sync.py add --skills a,b [--target DIR] [--token TOKEN]
    skills-sync.py remove --skills a,b [--target DIR]
    skills-sync.py list [--target DIR]

Requires Python 3.8+. Standard library only.
"""

import argparse
import json
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MANIFEST_NAME = ".manifest.json"
OLD_GITIGNORE_LINE = "skills/"  # legacy blanket-ignore line; migrated away from


def error(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def skills_dir(target):
    return Path(target) / ".claude" / "skills"


def manifest_path(target):
    return skills_dir(target) / MANIFEST_NAME


def load_manifest(target):
    path = manifest_path(target)
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_manifest(target, manifest):
    path = manifest_path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def gitignore_lines_for(skill_names):
    """Lines that should be present in .claude/.gitignore: one for the
    manifest itself, plus one per currently-installed skill folder."""
    lines = [f"skills/{MANIFEST_NAME}"]
    lines += [f"skills/{name}/" for name in sorted(skill_names)]
    return lines


def ensure_gitignore(target, skill_names):
    """Ensure .claude/.gitignore ignores the manifest and each given skill's
    folder individually (not the whole skills/ directory), so a project can
    track its own custom skills alongside synced ones.

    Migrates away from the old blanket "skills/" line if present. Appends
    any missing lines without reordering existing content; never duplicates
    a line.
    """
    path = Path(target) / ".claude" / ".gitignore"
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    before = list(lines)

    lines = [line for line in lines if line != OLD_GITIGNORE_LINE]

    for line in gitignore_lines_for(skill_names):
        if line not in lines:
            lines.append(line)

    if lines == before:
        return
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def remove_gitignore_lines(target, skill_names):
    """Remove the gitignore line for each given skill name, preserving all
    other lines and their order. No-op if the file doesn't exist."""
    path = Path(target) / ".claude" / ".gitignore"
    if not path.exists():
        return
    to_remove = {f"skills/{name}/" for name in skill_names}
    lines = path.read_text(encoding="utf-8").splitlines()
    new_lines = [line for line in lines if line not in to_remove]
    if new_lines == lines:
        return
    content = "\n".join(new_lines)
    if new_lines:
        content += "\n"
    path.write_text(content, encoding="utf-8")


def detect_skills(root):
    """Find every directory under root that directly contains a SKILL.md.

    Returns a dict mapping skill name (directory basename) -> Path. A
    SKILL.md at the root itself is skipped. If two directories share a
    basename, the last one found wins and a warning is printed.
    """
    root = Path(root).resolve()
    skills = {}
    for skill_md in sorted(root.rglob("SKILL.md")):
        skill_dir = skill_md.parent
        if skill_dir == root:
            continue
        name = skill_dir.name
        if name in skills and skills[name] != skill_dir:
            print(
                f"warning: duplicate skill name '{name}' found at "
                f"'{skill_dir}' and '{skills[name]}' — using the latter",
                file=sys.stderr,
            )
        skills[name] = skill_dir
    return skills


def resolve_selection(requested, available):
    """Resolve a --skills value ('all', a comma list, or None) against the
    skills available in the source. Errors out on unknown names."""
    if requested is None or requested.strip().lower() == "all":
        return sorted(available.keys())
    names = sorted({n.strip() for n in requested.split(",") if n.strip()})
    unknown = [n for n in names if n not in available]
    if unknown:
        error(
            f"unknown skill(s): {', '.join(unknown)}. "
            f"Available: {', '.join(sorted(available.keys())) or '(none)'}"
        )
    return names


def copy_skill(src, dest_root, name):
    dest = Path(dest_root) / name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def fetch_github(repo, ref, token):
    """Download and extract a GitHub repo tarball to a temp dir.

    Returns (root_path, tmpdir) where root_path is the directory inside
    tmpdir that holds the repo contents (descended past the
    owner-repo-<sha>/ wrapper). Caller must remove tmpdir when done.
    """
    headers = {"User-Agent": "skills-sync"}
    if token:
        url = f"https://api.github.com/repos/{repo}/tarball/{ref}"
        headers["Authorization"] = f"Bearer {token}"
    else:
        url = f"https://codeload.github.com/{repo}/tar.gz/{ref}"

    tmpdir = tempfile.mkdtemp(prefix="skills-sync-")
    try:
        tarball_path = os.path.join(tmpdir, "repo.tar.gz")
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp, open(tarball_path, "wb") as f:
                shutil.copyfileobj(resp, f)
        except urllib.error.HTTPError as e:
            hint = ""
            if e.code == 404:
                hint = " (check repo/ref/token — private repos 404 without a token)"
            error(f"HTTP {e.code} fetching {url}{hint}")
        except urllib.error.URLError as e:
            error(f"network error fetching {url}: {e.reason}")

        extract_dir = os.path.join(tmpdir, "extracted")
        os.makedirs(extract_dir)
        with tarfile.open(tarball_path) as tar:
            try:
                tar.extractall(extract_dir, filter="data")
            except TypeError:
                tar.extractall(extract_dir)

        entries = os.listdir(extract_dir)
        if len(entries) == 1 and os.path.isdir(os.path.join(extract_dir, entries[0])):
            root = os.path.join(extract_dir, entries[0])
        else:
            root = extract_dir

        return Path(root), tmpdir
    except SystemExit:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise
    except Exception:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise


def acquire_local(path, target):
    src = Path(path).resolve()
    if not src.is_dir():
        error(f"local source path does not exist or is not a directory: {src}")

    target_skills = skills_dir(target).resolve()
    if src == target_skills or target_skills in src.parents:
        error(
            f"source path '{src}' is inside the target's .claude/skills/ "
            f"— refusing to self-copy"
        )

    available = detect_skills(src)
    if not available:
        error(f"no skills (SKILL.md) found under '{src}'")

    return src, available


def cmd_install(args):
    target = Path(args.target)

    if args.path and args.ref is not None:
        error("--ref is only valid with --repo")

    cleanup_dir = None
    try:
        if args.repo:
            ref = args.ref or "main"
            src_root, cleanup_dir = fetch_github(args.repo, ref, args.token)
            available = detect_skills(src_root)
            if not available:
                error(f"no skills (SKILL.md) found in {args.repo}@{ref}")
        else:
            src_root, available = acquire_local(args.path, target)

        selection = resolve_selection(args.skills, available)
        if not selection:
            error("no skills selected")

        skills_root = skills_dir(target)
        skills_root.mkdir(parents=True, exist_ok=True)
        for name in selection:
            copy_skill(available[name], skills_root, name)

        manifest = {}
        if args.repo:
            manifest["source"] = "github"
            manifest["repo"] = args.repo
            manifest["ref"] = ref
        else:
            manifest["source"] = "local"
            manifest["path"] = str(src_root)
        manifest["updated"] = now_iso()
        manifest["skills"] = selection

        save_manifest(target, manifest)
        ensure_gitignore(target, selection)

        print(f"Installed {len(selection)} skill(s): {', '.join(selection)}")
    finally:
        if cleanup_dir:
            shutil.rmtree(cleanup_dir, ignore_errors=True)


def cmd_update(args, require_skills=False):
    target = Path(args.target)
    manifest = load_manifest(target)
    if manifest is None:
        error("no manifest found — run install first")

    if require_skills and not args.skills:
        error("--skills is required for 'add'")

    source = manifest.get("source")
    if source is None:
        source = "github" if "repo" in manifest else "local"

    cleanup_dir = None
    try:
        if source == "github":
            repo = manifest["repo"]
            ref = manifest.get("ref", "main")
            src_root, cleanup_dir = fetch_github(repo, ref, args.token)
        elif source == "local":
            src_root = Path(manifest["path"])
            if not src_root.is_dir():
                error(
                    f"local source path no longer exists: {src_root}. "
                    f"If the folder moved, re-run 'install --path' instead."
                )
        else:
            error(f"unknown manifest source: {source!r}")

        available = detect_skills(src_root)

        if args.skills:
            selection = resolve_selection(args.skills, available)
        else:
            selection = sorted(set(manifest.get("skills", [])) & set(available.keys()))

        skills_root = skills_dir(target)
        skills_root.mkdir(parents=True, exist_ok=True)
        for name in selection:
            copy_skill(available[name], skills_root, name)

        manifest["skills"] = sorted(set(manifest.get("skills", [])) | set(selection))
        manifest["updated"] = now_iso()
        save_manifest(target, manifest)
        ensure_gitignore(target, manifest["skills"])

        print(f"Updated {len(selection)} skill(s): {', '.join(selection) or '(none)'}")
    finally:
        if cleanup_dir:
            shutil.rmtree(cleanup_dir, ignore_errors=True)


def cmd_add(args):
    cmd_update(args, require_skills=True)


def cmd_remove(args):
    target = Path(args.target)
    manifest = load_manifest(target)
    if manifest is None:
        error("no manifest found — run install first")

    names = sorted({n.strip() for n in args.skills.split(",") if n.strip()})
    if not names:
        error("--skills is required for 'remove'")

    skills_root = skills_dir(target)
    removed = []
    for name in names:
        skill_path = skills_root / name
        if skill_path.exists():
            shutil.rmtree(skill_path)
        if name in manifest.get("skills", []):
            manifest["skills"].remove(name)
            removed.append(name)

    manifest["skills"] = sorted(manifest.get("skills", []))
    manifest["updated"] = now_iso()
    save_manifest(target, manifest)
    remove_gitignore_lines(target, names)

    print(f"Removed {len(removed)} skill(s): {', '.join(removed) or '(none found)'}")


def cmd_list(args):
    target = Path(args.target)
    manifest = load_manifest(target)
    if manifest is None:
        error("no manifest found — run install first")

    source = manifest.get("source")
    if source is None:
        source = "github" if "repo" in manifest else "local"

    if source == "github":
        label = f"{manifest['repo']}@{manifest.get('ref', 'main')}"
    else:
        label = manifest.get("path", "(unknown path)")

    print(f"{label} (updated {manifest.get('updated', 'unknown')})")
    for name in manifest.get("skills", []):
        print(f"  {name}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="skills-sync",
        description="Copy Claude Code skills from a GitHub repo or local "
        "folder into .claude/skills/",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_install = sub.add_parser("install", help="install skills into a project")
    src = p_install.add_mutually_exclusive_group(required=True)
    src.add_argument("--repo", help="source GitHub repo, owner/name")
    src.add_argument("--path", help="source local folder")
    p_install.add_argument(
        "--ref", default=None, help="git ref (github source only, default: main)"
    )
    p_install.add_argument(
        "--skills",
        default="all",
        help="comma-separated skill names, or 'all' (default: all)",
    )
    p_install.add_argument(
        "--target", default=".", help="target project directory (default: .)"
    )
    p_install.add_argument(
        "--token", default=None, help="GitHub token for private repos"
    )
    p_install.set_defaults(func=cmd_install)

    p_update = sub.add_parser("update", help="update installed skills")
    p_update.add_argument(
        "--skills",
        default=None,
        help="comma-separated skill names (default: all installed)",
    )
    p_update.add_argument(
        "--target", default=".", help="target project directory (default: .)"
    )
    p_update.add_argument(
        "--token", default=None, help="GitHub token for private repos"
    )
    p_update.set_defaults(func=cmd_update)

    p_add = sub.add_parser("add", help="add (and install) additional skills")
    p_add.add_argument("--skills", required=True, help="comma-separated skill names")
    p_add.add_argument(
        "--target", default=".", help="target project directory (default: .)"
    )
    p_add.add_argument("--token", default=None, help="GitHub token for private repos")
    p_add.set_defaults(func=cmd_add)

    p_remove = sub.add_parser("remove", help="remove installed skills")
    p_remove.add_argument("--skills", required=True, help="comma-separated skill names")
    p_remove.add_argument(
        "--target", default=".", help="target project directory (default: .)"
    )
    p_remove.set_defaults(func=cmd_remove)

    p_list = sub.add_parser("list", help="list installed skills")
    p_list.add_argument(
        "--target", default=".", help="target project directory (default: .)"
    )
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
