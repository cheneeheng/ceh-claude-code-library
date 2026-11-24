// Publish the repo's own docs as site pages, so the site never drifts from them.
// Writes src/content/docs/** (git-ignored) and src/sidebar.json, both read by the build.
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { BASE, REPO, TITLE } from "../site.mjs";

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const ROOT = path.resolve(SITE, "../..");
const OUT = path.join(SITE, "src/content/docs");
const read = (rel) => readFileSync(path.join(ROOT, rel), "utf8");

// Repo file -> page slug, title, and the home page card blurb. Plugin pages are added below.
const PAGES = [
  ["docs/GETTING_STARTED.md", "get-started", "Get started"],
  ["docs/TESTING_WORKFLOW.md", "guides/testing-workflow", "Testing workflow", "Writing or running tests? How the testing skills and agents route."],
  ["docs/RETRO_WORKFLOW.md", "guides/retro-workflow", "Retro workflow", "Running a retro? Which of the three retro skills to start, and where its report goes."],
  ["docs/CATALOG.md", "reference/catalog", "Catalog", "Looking for one skill or agent? Every one, grouped by plugin."],
  ["docs/ENVIRONMENT_VARIABLES.md", "reference/environment-variables", "Environment variables", "Configuring a plugin? Every variable a plugin reads."],
  ["docs/PLUGIN_DEPENDENCIES.md", "reference/plugin-dependencies", "Plugin dependencies", "Wondering what installs with what? The dependency graph."],
  ["docs/PLUGIN_VERSIONS.md", "reference/plugin-versions", "Plugin versions", "Checking what changed? Every plugin's current version."],
].map(([src, slug, title, blurb]) => ({ src, slug, title, blurb }));

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
slugOf.set("README.md", "index"); // the home page, written below

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
        // Starlight serves the index page at the site root, not at /index/.
        if (slug) return `](${BASE}/${slug === "index" ? "" : slug + "/"}${hash && "#" + hash})`;
        if (!existsSync(path.join(ROOT, target))) console.warn(`broken link in ${src}: ${url}`);
        const kind = statSync(path.join(ROOT, target), { throwIfNoEntry: false })?.isDirectory() ? "tree" : "blob";
        return `](${REPO}/${kind}/main/${target}${hash && "#" + hash})`;
      });
    })
    .join("\n");
}

function write(slug, frontmatter, body, ext = "md") {
  const file = path.join(OUT, `${slug}.${ext}`);
  mkdirSync(path.dirname(file), { recursive: true });
  const head = Object.entries(frontmatter).map(([k, v]) => `${k}: ${JSON.stringify(v)}`);
  writeFileSync(file, `---\n${head.join("\n")}\n---\n\n${body}`);
}

// Every file in OUT is generated, so clear it: a page dropped from PAGES must not stay built.
rmSync(OUT, { recursive: true, force: true });
for (const { src, slug, title, description } of PAGES) {
  // Starlight renders the frontmatter title as the H1, so drop the source's own.
  const body = rewriteLinks(read(src), src).replace(/^\s*# .*\n/, "");
  write(slug, description ? { title, description } : { title }, body);
}

// The home page: a splash hero from the README's first paragraph, then its "By lifecycle stage"
// table and cards for the other pages, so the landing text keeps its one home in README.md. The
// README's full plugin table stays on GitHub only: too wide for a landing page.
const readme = read("README.md").replace(/\r\n/g, "\n");
const [, intro] = readme.match(/^# .+\n\n([\s\S]+?)\n\n/);
const stageSection = readme.split("### By lifecycle stage")[1].split("\n---")[0].trim();
const card = (title, blurb, slug) =>
  `  <LinkCard title={${JSON.stringify(title)}} description={${JSON.stringify(blurb)}} href="${BASE}/${slug}/" />`;
const grid = (cards) => `<CardGrid>\n${cards.join("\n")}\n</CardGrid>`;
const cardsUnder = (prefix) => PAGES.filter((p) => p.slug.startsWith(prefix)).map((p) => card(p.title, p.blurb, p.slug));
write(
  "index",
  {
    title: "Home",
    description: intro.split(". ")[0].replace(/\s+/g, " ") + ".",
    template: "splash",
    hero: {
      title: TITLE,
      tagline: intro.replace(/\*\*/g, "").replace(/\s+/g, " "),
      actions: [
        { text: "Get started", link: `${BASE}/get-started/`, icon: "right-arrow" },
        { text: "Browse plugins", link: `${BASE}/plugins/`, variant: "minimal" },
      ],
    },
  },
  [
    'import { CardGrid, LinkCard } from "@astrojs/starlight/components";',
    `## Plugins by lifecycle stage\n\n${rewriteLinks(stageSection, "README.md")}`,
    `## Learn\n\n${grid([card("Plugins", "Know what you are about to do? Every plugin, grouped by lifecycle stage.", "plugins"), ...cardsUnder("guides/")])}`,
    `## Reference\n\n${grid(cardsUnder("reference/"))}`,
  ].join("\n\n") + "\n",
  "mdx",
);

// The plugin hub and sidebar follow the README's "By lifecycle stage" table.
const stages = stageSection
  .split("\n")
  .filter((line) => line.startsWith("|") && !/^\|\s*(Stage|-)/.test(line))
  .map((line) => {
    const [, stage, question, names] = line.split("|").map((c) => c.trim());
    return { stage, question, names: [...new Set(names.match(/ceh-[a-z-]+/g))].filter((n) => n in summary) };
  });
const staged = new Set(stages.flatMap((s) => s.names));
const unstaged = plugins.filter((n) => !staged.has(n));
if (unstaged.length) stages.push({ stage: "Other", question: "Not yet placed in a stage.", names: unstaged });

// JSON.stringify inside {} passes each value as a JS string, so quotes and braces need no escaping.
const hub = stages.map(({ stage, question, names }) => {
  const cards = names.map(
    (n) =>
      `  <LinkCard title={${JSON.stringify(n)}} description={${JSON.stringify(summary[n] + ".")}} href="${BASE}/plugins/${n}/" />`,
  );
  return `## ${stage}\n\n${question}\n\n<CardGrid>\n${cards.join("\n")}\n</CardGrid>`;
});
// Each stage heading's anchor: lowercase, spaces to hyphens ("On demand" -> #on-demand).
const stageLinks = stages.map(({ stage }) => `[${stage}](#${stage.toLowerCase().replace(/\s+/g, "-")})`);
write(
  "plugins/index",
  { title: "Plugins", description: "Every plugin, grouped by the lifecycle stage it serves." },
  `import { CardGrid, LinkCard } from "@astrojs/starlight/components";\n\n${plugins.length} plugins, each installable alone. Find the stage you are in, then open the plugin for what it does, how it is invoked, and what it needs. Which to install first is in [Get started](${BASE}/get-started/).\n\nA product moves through stages in its life, and the plugins are grouped by the stage they serve: ${stageLinks.join(" · ")}.\n\n${hub.join("\n\n")}\n`,
  "mdx",
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
