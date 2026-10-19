"""Publish each listed plugin's README as a page, so the site never drifts from the plugin."""

from pathlib import Path

from mkdocs.structure.files import File

PLUGINS = ["ceh-every-session", "ceh-coding-conduct", "ceh-git-workflow"]
ROOT = Path(__file__).resolve().parents[2] / "plugins" / "standalone"


def on_files(files, config):
    for name in PLUGINS:
        readme = (ROOT / name / "README.md").read_text(encoding="utf-8")
        files.append(File.generated(config, f"plugins/{name}.md", content=readme))
    return files
