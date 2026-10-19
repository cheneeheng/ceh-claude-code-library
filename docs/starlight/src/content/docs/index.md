---
title: CEH Claude Code Library
description: Claude Code plugins that guide autonomous agents through a product's life, one plugin per use case.
---

Plugins for Claude Code that guide an agent through a product's life: shaping the idea, building
and proving the software, and telling people about it. It is written for developers who use Claude
Code. Each plugin works installed alone, so you add only the ones you need.

Add the marketplace, then install `ceh-every-session`, the one plugin every session should have.
[Get started](/ceh-claude-code-library/get-started/) lists the rest of the core for people who write code in git repos.

```text
/plugin marketplace add cheneeheng/ceh-claude-code-library
/plugin install ceh-every-session@ceh-claude-code-library --scope user
```

- **New here?** [Get started](/ceh-claude-code-library/get-started/): which plugins to install first, and which to leave out.
- **Know what you are about to do?** [Plugins](/ceh-claude-code-library/plugins/): every plugin, grouped by lifecycle stage.
- **Looking for one skill or agent?** [Catalog](/ceh-claude-code-library/reference/catalog/)
- **Configuring a plugin?** [Environment variables](/ceh-claude-code-library/reference/environment-variables/)
- **Wondering what installs with what?** [Plugin dependencies](/ceh-claude-code-library/reference/plugin-dependencies/)
- **Writing or running tests?** [Testing workflow](/ceh-claude-code-library/guides/testing-workflow/)
- **Checking what changed?** [Plugin versions](/ceh-claude-code-library/reference/plugin-versions/)
