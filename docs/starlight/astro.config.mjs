import { readFileSync } from "node:fs";
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";
import { BASE, REPO } from "./site.mjs";

const stages = JSON.parse(readFileSync(new URL("./src/sidebar.json", import.meta.url), "utf8"));

export default defineConfig({
  site: "https://cheneeheng.github.io",
  base: BASE,
  integrations: [
    starlight({
      title: "CEH Claude Code Library",
      social: [{ icon: "github", label: "GitHub", href: REPO }],
      sidebar: [
        { label: "Home", link: "/" },
        { slug: "get-started" },
        { label: "Plugins", items: [{ slug: "plugins" }, ...stages] },
        { label: "Guides", items: [{ slug: "guides/testing-workflow" }] },
        {
          label: "Reference",
          items: [
            { slug: "reference/catalog" },
            { slug: "reference/environment-variables" },
            { slug: "reference/plugin-dependencies" },
            { slug: "reference/plugin-versions" },
          ],
        },
      ],
    }),
  ],
});
