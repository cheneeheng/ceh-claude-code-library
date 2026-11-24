# ceh-ui-design design notes

Maintainer detail moved out of the plugin README on 2026-11-24, when the README was rewritten for
the person installing the plugin. The site does not publish this file.

## Why the skill lives here

The skill is framework-agnostic. It moved here from `ceh-web-frontend` so that plugins which render
HTML without a frontend stack, such as `ceh-competitor-analysis`, can depend on it alone.
