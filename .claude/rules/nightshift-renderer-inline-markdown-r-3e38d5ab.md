---
schema: nightshift-rule/v1
decided: 2026-11-24
source: "nightshift rule r-3e38d5ab"
---

# Renderer inline markdown

When writing a renderer that converts inline Markdown, run the conversion on every text field, footers and other fixed parts included, and write and run the failing check first, because the first `analyze-competitor` HTML renderer left the footer without backtick-to-code conversion and one test file was built wrong.
