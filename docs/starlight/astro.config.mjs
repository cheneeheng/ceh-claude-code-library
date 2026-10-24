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
      logo: { src: "./public/favicon.svg" },
      social: [{ icon: "github", label: "GitHub", href: REPO }],
      customCss: ["./src/styles/meridian-tokens.css", "./src/styles/theme.css"],
      expressiveCode: {
        styleOverrides: { borderRadius: "var(--radius-md)", codeFontFamily: "var(--font-mono)" },
      },
      head: [
        { tag: "link", attrs: { rel: "preconnect", href: "https://fonts.googleapis.com" } },
        { tag: "link", attrs: { rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: "" } },
        {
          tag: "link",
          attrs: {
            rel: "stylesheet",
            href: "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap",
          },
        },
      ],
      sidebar: [
        { label: "Start here", items: [{ slug: "get-started" }, { slug: "why" }, { slug: "concepts" }] },
        { label: "Plugins", items: [{ label: "Overview", slug: "plugins" }, ...stages] },
        { label: "Guides", items: [{ slug: "guides/testing-workflow" }, { slug: "guides/retro-workflow" }] },
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
