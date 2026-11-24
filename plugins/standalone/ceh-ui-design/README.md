# ceh-ui-design

Visual design for any UI: a web app, a dashboard, or a standalone HTML page such as a report. Its
one skill settles the layout, hierarchy, navigation and states before any markup is written, then
builds against a bundled theme, so the first pass already looks finished. It works with any
framework.

## Install

See [Getting started](../../../docs/GETTING_STARTED.md). The plugin needs nothing else installed.
It also arrives by itself with `ceh-ag-ui`, `ceh-competitor-analysis` and `ceh-web-frontend`, which
depend on it.

## Skills

| Skill       | Say or type                                                                        | What it does                                                                |
| ----------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `design-ui` | "design the UI", "lay out this page", "polish this UI", `/ceh-ui-design:design-ui` | Makes the design decisions first, then builds the page on one of two themes |

## Agents

This plugin has no agents.

## Hooks

This plugin has no hooks.

## Settings

This plugin reads no settings.

## How it works

What `design-ui` decides and builds:

- **Layout:** a page archetype, including a Document archetype for plans and reports.
- **Reading order:** hierarchy, density, where the navigation sits, and in-page contents.
- **States:** what the page shows when it is empty, loading, or failed.
- **Options:** a variants board, throwaway HTML pages that each differ on one design answer, so
  you can pick by looking.
- **Finish:** a command dock, readable tables, lifecycle steppers, and Mermaid diagrams.
- **Theme:** Meridian or Tidewater, linked as a stylesheet or inlined into a single file.

The themes load their fonts from Google Fonts, so a page viewed offline falls back to system fonts.

## Not this plugin

- The frontend code itself (SvelteKit or React, tests, accessibility): `ceh-web-frontend`.
- The words on the page (labels, empty states, error text): `ceh-usability-audit`.

## Where its files live

The variants board goes to `.agents_workspace/product/design-variants/<surface>/`. The finished
page goes wherever the project keeps its UI.
