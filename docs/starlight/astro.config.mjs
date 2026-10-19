import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

export default defineConfig({
  site: "https://cheneeheng.github.io",
  base: "/ceh-claude-code-library/starlight",
  integrations: [
    starlight({
      title: "CEH Claude Code Library",
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/cheneeheng/ceh-claude-code-library",
        },
      ],
      sidebar: [
        { label: "Home", link: "/" },
        { label: "Plugins", items: [{ autogenerate: { directory: "plugins" } }] },
      ],
    }),
  ],
});
