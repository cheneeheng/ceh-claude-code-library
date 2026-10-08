# ceh-ui-design

Visual design for any UI: a web app, a dashboard, or a standalone HTML page such as a report. One
skill makes the layout, hierarchy, navigation, and state decisions explicitly before any markup,
then builds against a bundled token-driven theme so the result is finished on the first pass.

The skill is framework-agnostic. It moved here from `ceh-web-frontend` so that plugins which render
HTML without a frontend stack, such as `ceh-competitor-analysis`, can depend on it alone.

## Skills

| Skill       | Invoke                     | Triggers when                                                                                                                                                                                                                                                                               |
| ----------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `design-ui` | `/ceh-ui-design:design-ui` | Any UI visual design decision: layout archetypes, hierarchy, navigation placement and in-page contents, empty/loading/error states, density, finishing recipes (command dock, humanized tables, lifecycle steppers), plus theming from bundled token-driven templates (Meridian, Tidewater) |

`design-ui` bundles two themes under `references/` (`meridian/` and `tidewater/`, each a
`brand.css` plus a `brand-guide.html`) and worked markup for the finishing recipes in
`references/examples.md`.

## Used by

These plugins declare `ceh-ui-design` as a dependency, so installing any of them installs it:

| Plugin                    | Why                                                                                           |
| ------------------------- | --------------------------------------------------------------------------------------------- |
| `ceh-ag-ui`               | `build-ag-ui` and `add-canvas-component` call `design-ui` on every run for the theme          |
| `ceh-competitor-analysis` | `analyze-competitor` and `compare-competitors` call `design-ui` on every run for HTML pages   |
| `ceh-web-frontend`        | Keeps `design-ui` installed with the web stack, where it lived until `ceh-web-frontend` 1.1.0 |

## Prerequisites

None. The skill reads files and writes markup. The themes load their web fonts from Google Fonts,
so a page viewed offline falls back to system fonts.

The plugin reads no environment variables and ships no hooks.
