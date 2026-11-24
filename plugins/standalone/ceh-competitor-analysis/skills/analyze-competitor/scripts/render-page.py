# /// script
# requires-python = ">=3.10"
# dependencies = ["pydantic>=2,<3", "pyyaml>=6,<7"]
# ///
"""Render a competitor report's HTML page from its competitor-report/v2 YAML.

    uv run --script render-page.py <slug>.yaml [--theme <name>]

Writes `<slug>.html` beside the YAML. The `<head>` and its CSS come from
`../assets/report-page.html`, and the body follows that template's COMPETITOR-ONLY blocks.
`--theme` defaults to the one `.css` in the YAML folder's `themes/`, else `meridian`.

Exit codes, as artifact.py: 0 written, 1 errors as `<path>: <where>: <error>` lines, 2 any other
failure, 3 no model for the file's `<name>/v<N>`.
"""

from __future__ import annotations

import html
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "report-page.html"
BADGE = {
    "Covered": "text-success",
    "Partial": "text-warning",
    "Gap": "text-danger",
    "N/A": "muted",
}
TITLE = re.compile(r"<title>(.*?)</title>", re.S)
SENTENCE = re.compile(r"\. (?=[A-Z])")


def load_artifact():
    spec = importlib.util.spec_from_file_location("artifact", HERE / "artifact.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def inline(text: str) -> str:
    """Escape a value, then turn its Markdown code spans and bold into HTML."""
    out = html.escape(text, quote=False)
    out = re.sub(
        r"``\s?(.+?)\s?``|`([^`]+)`", lambda m: f"<code>{m[1] or m[2]}</code>", out
    )
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)


def paras(block: str | None) -> str:
    if not block:
        return ""
    return "".join(
        f"<p>{inline(p.strip())}</p>" for p in re.split(r"\n\s*\n", block.strip())
    )


def covers(text: str, names: list[str]) -> str:
    if not names:
        return inline(text)
    codes = [f"<code>{html.escape(n, quote=False)}</code>" for n in names]
    joined = (
        codes[0] if len(codes) == 1 else ", ".join(codes[:-1]) + " and " + codes[-1]
    )
    return f"{inline(text)} Covers {joined}."


def card(strong: str, span: str, detail: str) -> str:
    return (
        f'<details class="x"><summary><strong>{inline(strong)}</strong><span>{inline(span)}</span>'
        f'</summary><div class="more"><p>{detail}</p></div></details>'
    )


def column(cls: str, title: str, hint: str, cards: list[str]) -> str:
    items = "\n          ".join(cards) or '<p class="muted">None</p>'
    return (
        f'      <div class="col {cls}">\n        <h3>{title}</h3><p class="muted">{hint}</p>\n'
        f'        <div class="items">\n          {items}\n        </div>\n      </div>'
    )


def label(page: Path) -> str:
    if page.name == "comparison.html":
        return "Comparison"
    m = TITLE.search(page.read_text(encoding="utf-8", errors="replace"))
    if not m:
        return page.stem
    title = html.unescape(m[1]).strip()
    if " · " in title:
        return title.split(" · ", 1)[0]
    return title.removeprefix("Competitor analysis: ")


def nav(folder: Path, own: Path, name: str) -> str:
    pages = {p.name: label(p) for p in folder.glob("*.html") if p.name != own.name}
    pages[own.name] = name
    first = ["comparison.html"] if "comparison.html" in pages else []
    rest = sorted((n for n in pages if n not in first), key=lambda n: pages[n].lower())
    links = []
    for n in first + rest:
        cur = ' aria-current="page"' if n == own.name else ""
        links.append(
            f'<a href="{html.escape(n)}"{cur}>{html.escape(pages[n], quote=False)}</a>'
        )
    return "\n    ".join(links)


def body(doc, legend: str, navlinks: str) -> str:
    t, f = doc.take, doc.fields
    rows = [r for g in doc.coverage for r in g.rows]
    tally = {k: sum(r.rating == k for r in rows) for k in BADGE}
    groups = doc.inventory.groups
    top = [g for g in groups if g.count > 0][:2]
    facts = [(str(g.count), g.group.lower()) for g in top]
    facts.append((str(tally["Partial"] + tally["Gap"]), "partial or gap"))
    facts_html = "\n      ".join(
        f'<div><span class="numeric">{v}</span><span class="muted">{html.escape(k)}</span></div>'
        for v, k in facts
    )

    adopt = [card(r.idea, r.lands_in, covers(r.why, r.covers)) for r in t.adopt_now]
    build = [
        card(r.idea, r.lands_in, covers(f"{r.why} Effort {r.effort}.", r.covers))
        for r in t.build
    ]
    skip = [
        card(
            r.idea,
            SENTENCE.split(r.why_not, 1)[0].rstrip("."),
            covers(r.why_not, r.covers),
        )
        for r in t.skip
    ]
    steps = "\n      ".join(f"<div>{inline(s)}</div>" for s in doc.how_it_works)
    wows = (
        "\n      ".join(
            f'<details class="x"><summary><span class="n">{n:02d}</span><h3>{inline(o.what)}</h3>'
            f'<p>{inline(o.one_line)}</p></summary><div class="more"><p>{inline(o.how)}</p>'
            f"<p><code>{html.escape(o.evidence, quote=False)}</code></p></div></details>"
            for n, o in enumerate(doc.oh_wow, 1)
        )
        or '<p class="muted">None found.</p>'
    )

    largest = groups[0].count or 1
    bars = []
    for i, g in enumerate(groups):
        if g.count == 0:
            bars.append(
                f'<div class="inv-row"><span class="muted">{inline(g.group)}</span>'
                '<div class="bar-track"></div><span class="numeric muted">—</span></div>'
            )
            continue
        pct = max(1, round(g.count / largest * 100))
        bars.append(
            f'<div class="inv-row"><span>{inline(g.group)}</span><div class="bar-track">'
            f'<div class="bar-fill is-{i % 4 + 1}" style="width:{pct}%"></div></div>'
            f'<span class="numeric">{g.count}</span></div>'
        )
    inv_note = paras(doc.inventory.notes).replace("<p>", '<p class="muted">')

    cov_caption = (
        f"{tally['Covered']} covered, {tally['Partial']} partial, {tally['Gap']} gaps, "
        f"{tally['N/A']} N/A. {inline(legend)}"
    )
    cov_notes = paras(doc.coverage_notes).replace("<p>", '<p class="muted">')
    tables = []
    for g in doc.coverage:
        trs = "\n      ".join(
            f"<tr><td>{inline(r.component)}</td><td>{inline(r.what)}</td>"
            f'<td><span class="badge {BADGE[r.rating]}">{r.rating}</span></td>'
            f"<td>{inline(r.ours) if r.ours else '—'}</td></tr>"
            for r in g.rows
        )
        tables.append(
            f'    <h3 class="cov-group">{inline(g.group)} · {len(g.rows)}</h3>\n'
            '    <div class="panel"><table class="table">\n'
            f"      <tr><th>{html.escape(doc.competitor)} component</th><th>What it does</th>"
            f"<th>Ours</th><th>Our component</th></tr>\n      {trs}\n    </table></div>"
        )
    footer = " · ".join(
        inline(s)
        for s in (
            doc.source,
            f"{f.version}, {f.version_from}",
            f.license,
            f.author,
            f"{f.read}, analysed {doc.analysed.isoformat()}",
        )
    )
    total = sum(g.count for g in groups)
    bars_html = "\n      ".join(bars)
    tables_html = "\n\n".join(tables)
    return f"""<body>
<header class="topbar"><div class="topbar-in">
  <span class="eyebrow">Competitor analysis</span>
  <nav aria-label="Reports">
    {navlinks}
  </nav>
</div></header>

<main>
  <div class="hero">
    <div>
      <span class="eyebrow">Competitor</span>
      <h1>{html.escape(doc.competitor)}</h1>
      <p class="lead">{inline(doc.summary)} <strong>{inline(doc.verdict)}</strong></p>
    </div>
    <div class="facts">
      {facts_html}
    </div>
  </div>

  <section>
    <div class="sec-head"><span class="eyebrow">Decision</span><h2>What we take</h2><p class="muted">Open a card for where it lands and why.</p></div>
    <div class="board">
{column("now", "Adopt now", "Effort S.", adopt)}
{column("later", "Build", "Effort M or L.", build)}
{column("skip", "Skip", "Not for us, with the reason.", skip)}
    </div>
  </section>

  <section>
    <div class="sec-head"><span class="eyebrow">How it works</span><h2>From first step to result</h2></div>
    <div class="steps">
      {steps}
    </div>
  </section>

  <section>
    <div class="sec-head"><span class="eyebrow">Oh wow · {len(doc.oh_wow)}</span><h2>Mechanisms worth knowing</h2><p class="muted">Open a card for how it works and where it lives.</p></div>
    <div class="cards">
      {wows}
    </div>
  </section>

  <section>
    <div class="sec-head"><span class="eyebrow">Inventory · {total:,} components</span><h2>What it ships</h2>{inv_note}</div>
    <div class="inv">
      {bars_html}
    </div>
  </section>

  <section>
    <div class="sec-head"><span class="eyebrow">Coverage · {len(rows)} components</span><h2>What they ship against what we ship</h2><p class="muted">{cov_caption}</p>{cov_notes}</div>

{tables_html}
  </section>

  <p class="muted source">{footer}</p>
</main>
</body>
</html>
"""


def main(argv: list[str]) -> int:
    theme = None
    if len(argv) == 3 and argv[1] == "--theme":
        theme = argv[2]
    elif len(argv) != 1:
        print("usage: render-page.py <slug>.yaml [--theme <name>]")
        return 2
    path = Path(argv[0])
    art = load_artifact()
    try:
        errors, mod, doc = art.validate(path)
    except art.NoModel as e:
        print(f"{path}: {e}")
        return 3
    if errors:
        print("\n".join(errors))
        return 1
    if not hasattr(mod, "LEGEND"):
        print(f"{path}: render-page.py renders competitor-report files only")
        return 2
    folder = path.resolve().parent
    if theme is None:
        found = sorted((folder / "themes").glob("*.css"))
        theme = found[0].stem if len(found) == 1 else "meridian"
    css = folder / "themes" / f"{theme}.css"
    if not css.is_file():
        print(f"{css}: missing, copy the theme's brand.css there first")
        return 2
    shell = TEMPLATE.read_text(encoding="utf-8")
    head = shell[shell.index("<html") : shell.index("</head>") + len("</head>")]
    head = head.replace(
        "{{page title}}", f"{html.escape(doc.competitor)} · Competitor analysis"
    )
    head = head.replace("{{theme}}", html.escape(theme))
    page = path.with_suffix(".html")
    navlinks = nav(folder, page, doc.competitor)
    art.write_atomic(
        page, f"<!doctype html>\n{head}\n{body(doc, mod.LEGEND, navlinks)}"
    )
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:  # anything unexpected is exit 2, never an empty exit 1
        print(f"render-page.py failed: {type(e).__name__}: {e}")
        sys.exit(2)
