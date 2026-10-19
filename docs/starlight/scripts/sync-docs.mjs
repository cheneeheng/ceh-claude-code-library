// Publish the repo's own docs as site pages, so the site never drifts from them.
// Writes src/content/docs/** (git-ignored) and src/sidebar.json, both read by the build.
import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { BASE, REPO } from "../site.mjs";

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const ROOT = path.resolve(SITE, "../..");
const OUT = path.join(SITE, "src/content/docs");
const read = (rel) => readFileSync(path.join(ROOT, rel), "utf8");

// Repo file -> page slug and title. Plugin pages are added below.
const PAGES = [
  ["docs/GETTING_STARTED.md", "get-started", "Get started"],
  ["docs/VISION.md", "why", "Why this library"],
  ["docs/STRATEGY.md", "concepts", "How the plugins fit together"],
  ["docs/TESTING_WORKFLOW.md", "guides/testing-workflow", "Testing workflow"],
  ["docs/CATALOG.md", "reference/catalog", "Catalog"],
  ["docs/ENVIRONMENT_VARIABLES.md", "reference/environment-variables", "Environment variables"],
  ["docs/PLUGIN_DEPENDENCIES.md", "reference/plugin-dependencies", "Plugin dependencies"],
  ["docs/PLUGIN_VERSIONS.md", "reference/plugin-versions", "Plugin versions"],
].map(([src, slug, title]) => ({ src, slug, title }));

const plugins = readdirSync(path.join(ROOT, "plugins/standalone")).sort();
const summary = {};
for (const name of plugins) {
  const { description } = JSON.parse(read(`plugins/standalone/${name}/.claude-plugin/plugin.json`));
  // Drop the "CEH <name>: " lead-in, which repeats the plugin name beside it in the hub.
  const first = description.split(". ")[0].replace(/^CEH [^:]+: /, "").replace(/\.$/, "");
  summary[name] = first[0].toUpperCase() + first.slice(1);
  PAGES.push({
    src: `plugins/standalone/${name}/README.md`,
    slug: `plugins/${name}`,
    title: name,
    description,
  });
}

// A link to a page's file, or to a plugin's folder, lands on that page.
const slugOf = new Map(PAGES.map((p) => [p.src, p.slug]));
for (const name of plugins) slugOf.set(`plugins/standalone/${name}`, `plugins/${name}`);

function rewriteLinks(md, src) {
  let fenced = false;
  return md
    .split("\n")
    .map((line) => {
      if (/^\s*(```|~~~)/.test(line)) fenced = !fenced;
      if (fenced) return line;
      return line.replace(/\]\(([^)\s]+)\)/g, (whole, url) => {
        if (/^([a-z]+:|#)/i.test(url)) return whole;
        const [file, hash = ""] = url.split("#");
        const target = path.posix.join(path.posix.dirname(src), file).replace(/\/$/, "");
        const slug = slugOf.get(target);
        if (slug) return `](${BASE}/${slug}/${hash && "#" + hash})`;
        if (!existsSync(path.join(ROOT, target))) console.warn(`broken link in ${src}: ${url}`);
        const kind = statSync(path.join(ROOT, target), { throwIfNoEntry: false })?.isDirectory() ? "tree" : "blob";
        return `](${REPO}/${kind}/main/${target}${hash && "#" + hash})`;
      });
    })
    .join("\n");
}

function write(slug, frontmatter, body) {
  const file = path.join(OUT, `${slug}.md`);
  mkdirSync(path.dirname(file), { recursive: true });
  const head = Object.entries(frontmatter).map(([k, v]) => `${k}: ${JSON.stringify(v)}`);
  writeFileSync(file, `---\n${head.join("\n")}\n---\n\n${body}`);
}

for (const { src, slug, title, description } of PAGES) {
  // Starlight renders the frontmatter title as the H1, so drop the source's own.
  const body = rewriteLinks(read(src), src).replace(/^\s*# .*\n/, "");
  write(slug, description ? { title, description } : { title }, body);
}

// The plugin hub and sidebar follow the README's "By lifecycle stage" table.
const stageTable = read("README.md").split("### By lifecycle stage")[1].split("\n---")[0];
const stages = stageTable
  .split("\n")
  .filter((line) => line.startsWith("|") && !/^\|\s*(Stage|-)/.test(line))
  .map((line) => {
    const [, stage, question, names] = line.split("|").map((c) => c.trim());
    return { stage, question, names: [...new Set(names.match(/ceh-[a-z-]+/g))].filter((n) => n in summary) };
  });
const staged = new Set(stages.flatMap((s) => s.names));
const unstaged = plugins.filter((n) => !staged.has(n));
if (unstaged.length) stages.push({ stage: "Other", question: "Not yet placed in a stage.", names: unstaged });

const hub = stages.map(({ stage, question, names }) => {
  const items = names.map((n) => `- [\`${n}\`](${BASE}/plugins/${n}/): ${summary[n]}.`);
  return `## ${stage}\n\n${question}\n\n${items.join("\n")}`;
});
write(
  "plugins/index",
  { title: "Plugins", description: "Every plugin, grouped by the lifecycle stage it serves." },
  `${plugins.length} plugins, each installable alone. Find the stage you are in, then open the plugin for what it does, how it is invoked, and what it needs. Which to install first is in [Get started](${BASE}/get-started/).\n\n${hub.join("\n\n")}\n`,
);
writeFileSync(
  path.join(SITE, "src/sidebar.json"),
  JSON.stringify(
    stages.map(({ stage, names }) => ({
      label: stage,
      collapsed: true,
      items: names.map((n) => ({ slug: `plugins/${n}` })),
    })),
  ),
);
