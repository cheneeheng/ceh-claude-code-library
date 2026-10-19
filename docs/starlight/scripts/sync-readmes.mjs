// Publish each listed plugin's README as a page, so the site never drifts from the plugin.
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";

const PLUGINS = ["ceh-every-session", "ceh-coding-conduct", "ceh-git-workflow"];
const SRC = new URL("../../../plugins/standalone/", import.meta.url);
const OUT = new URL("../src/content/docs/plugins/", import.meta.url);

mkdirSync(OUT, { recursive: true });
for (const name of PLUGINS) {
  const readme = readFileSync(new URL(`${name}/README.md`, SRC), "utf8");
  // Starlight renders the frontmatter title as the H1, so drop the README's own.
  const body = readme.replace(/^# .*\r?\n/, "");
  writeFileSync(new URL(`${name}.md`, OUT), `---\ntitle: ${name}\n---\n${body}`);
}
