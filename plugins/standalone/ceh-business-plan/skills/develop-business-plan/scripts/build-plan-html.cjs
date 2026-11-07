// Builds BUSINESS_PLAN.html next to a business plan, from the page shell and the Meridian theme in
// ../assets, which it inlines so the HTML stays one file. Rerun after every edit to the plan:
//   node build-plan-html.cjs <path/to/BUSINESS_PLAN.md>
// Needs Node 18+ and network on first run: npx fetches the marked CLI.
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const planPath = path.resolve(process.argv[2] || ".agents_workspace/product/business/BUSINESS_PLAN.md");
const asset = (f) => path.join(__dirname, "..", "assets", f);
const src = fs.readFileSync(planPath, "utf8").replace(/\r\n/g, "\n");
const [, front, fullBody] = src.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
// The markdown's own contents list is dropped: the HTML draws a contents rail instead.
const body = fullBody.replace(/^\*\*Contents\*\*\n[\s\S]*?(?=^## )/m, "");
const meta = Object.fromEntries(
  front.split("\n").map((l) => [l.slice(0, l.indexOf(":")), l.slice(l.indexOf(":") + 1).trim()]),
);

let html = execSync("npx -y marked@4 --no-header-ids --no-mangle", { input: body, encoding: "utf8" });

html = html.replace(
  /<pre><code class="language-mermaid">([\s\S]*?)<\/code><\/pre>/g,
  '<figure class="panel diagram"><pre class="mermaid">$1</pre></figure>',
);
html = html.replace(/<table>/g, '<div class="panel table-wrap"><table class="table">');
html = html.replace(/<\/table>/g, "</table></div>");

// GitHub's heading anchor, so the markdown's own links (#0401-strategy) also work in the HTML.
// less-code: entities are dropped, not decoded; fine while headings use only & < > " ' as symbols.
const slug = (t) => t.replace(/<[^>]+>|&#?\w+;/g, "").toLowerCase().replace(/[^\p{L}\p{N} _-]/gu, "").replace(/ /g, "-");
const toc = [];
html = html.replace(/<h([2-6])>(.*?)<\/h\1>/g, (_, level, text) => {
  const id = slug(text);
  toc.push({ level, id, text: text.replace(/<[^>]+>/g, "") });
  const shown = text.replace(/^§([\d.]+) /, '<span class="sec numeric">§$1</span> ');
  return `<h${level} id="${id}">${shown}</h${level}>`;
});

// Evidence tags and table verdicts become badges, outside the Mermaid sources only.
const kinds = { evidence: "tag-evidence", assumption: "tag-assumption", "hypothesis-to-test": "tag-hypothesis" };
const verdicts = { yes: "badge tag-evidence", no: "badge", "not stated": "badge badge-dashed" };
html = html
  .split(/(<pre class="mermaid">[\s\S]*?<\/pre>)/)
  .map((part, i) => i % 2 ? part : part
    .replace(/\[(evidence|assumption|hypothesis-to-test)((?:[:, ][^\]]*)?)\]/g,
      (_, kind, rest) => `<span class="badge tag ${kinds[kind]}">${kind}${rest}</span>`)
    .replace(/<td>(yes|no|not stated)<\/td>/g,
      (_, v) => `<td><span class="${verdicts[v]}">${v}</span></td>`))
  .join("");

const tocHtml = toc
  .map((t) => `<li class="toc-${t.level}" style="--lvl: ${t.level}"><a href="#${t.id}">${t.text}</a></li>`)
  .join("\n");

const out = path.join(path.dirname(planPath), "BUSINESS_PLAN.html");
const page = fs.readFileSync(asset("business-plan-page.html"), "utf8")
  .replace("/*BRAND_CSS*/", () => fs.readFileSync(asset("brand.css"), "utf8"))
  .replace(/\{\{(\w+)\}\}/g, (_, k) => ({ TOC: tocHtml, BODY: html, ...meta })[k] ?? "");
fs.writeFileSync(out, page);
console.log(`wrote ${out}: ${toc.length} headings`);
