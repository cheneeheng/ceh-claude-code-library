---
schema: repeat-mistake/v1
date: 2026-10-30
other_file: none
---

# Repeat mistakes — 2026-10-30

The page this retro measured is a private workspace page. It has since been redrawn without Mermaid,
so its Mermaid version survives only in private workspace history. The evidence below describes it
in words and numbers.

| Mistake                                                                                    | Evidence                                                                                                                                                                                                                                                                                                                                               | Rung | Fix                                                                                                            | Proof        | Status   |
| ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---- | -------------------------------------------------------------------------------------------------------------- | ------------ | -------- |
| A Mermaid page had no width rule, so each diagram and heading took whatever width it got   | User: "Some of the mermaid diagrams is horizontally scrollable and some no", "Why the diagrams have no max width". The page improvised a cutoff that treated diagrams differently by their width against the panel. At a 1762px window, 3 of 13 diagrams scrolled, 1 shrank to 73%, and the title measured 1706px against 561px and 647px for the text | 1    | Worked column and fit markup in `references/examples.md`, with a width rule in the Diagrams recipe             | not provable | applied  |
| A page built with `design-ui` skipped rules the skill already states                       | A `less-code` comment on the page excused copying only the theme tokens it used instead of the whole `brand.css`. The same page had no font import, no contents rail with six `h2` sections, and no `document.fonts.ready`                                                                                                                             | 5    | A Document audit item in the skill's Review pass, and `less-code` named as no exemption from the theme install | not provable | applied  |
| `var()` inside a Mermaid `classDef` breaks every diagram on the page                       | This session's rebuild: `classDef ok fill:var(--success-wash),...` rendered "Syntax error in text, mermaid version 11.17.2" in every panel. Same result on 12.2.0, by a run on 2026-11-02                                                                                                                                                              | 1    | The same worked markup colours nodes from page CSS, so no `classDef` is needed                                 | not provable | applied  |
| The `design-ui` prose cap may be wrong: text stops at about 65 characters on a wide screen | The Prose bullet under Content width: "Prose: 65–75 characters per line (`max-width: 65ch`). Never let body text span a wide viewport." User, after seeing text and diagrams share one 1100px edge: "I think that might be a bug. I would expect the text to fill the screen width up until a fixed max width"                                         | 5    | None: the user kept the cap for pages of long text alone, with 1100px when a page has diagrams                 | not provable | rejected |
| The Mermaid fit draft was proven on flowcharts only and has no print or narrow-column rule | The page's 23 diagrams were all flowcharts, so "23 of 23 diagrams" and the fixed 16px label say nothing about other types. `grep '@media print'` found nothing in `design-ui/SKILL.md`, `references/examples.md`, or either `brand.css`                                                                                                                | 1    | Replacement fit markup, and a label check before the rule goes beyond flowcharts                               | not provable | applied  |
| `design-ui` keeps conditional recipes and restated rules inline, so every run reads them   | `design-ui/SKILL.md` is 30,831 bytes (`wc -c`). Command dock, Variants board, Inputs, Lifecycle colors, and Identity monograms apply only when that component is present. Most of Anti-patterns restates the rules above it. Row 2 above shows a page skipping rules the skill already states, though nothing measured whether length is the cause     | 5    | Conditional recipes moved beside their markup, each with a trigger, and restated rules cut                     | not provable | applied  |

## Why this rung

- No width rule: rung 1 is the top rung. A copyable fit replaces the improvised one.
- Skipped rules: rung 1 does not fit because these pages are written freehand, with no generator to fix. Rungs 2 to 4 do not fit because no setting or validator sees a page in a git-ignored folder, and this is the first measured miss, so a hook is not earned yet.
- `var()` in `classDef`: rung 1 is the top rung. The worked markup leaves no `classDef` to get wrong.
- Prose cap: the rule is written guidance, so any change stays at rung 5. The user decided no change.
- Fit draft gaps: rung 1 is the top rung. The worked markup carries the print and narrow-column rules, so a later session copies them instead of remembering them.
- Slimming: the problem is the skill's own text, so the change stays at rung 5. No setting or validator can decide what an agent needs to read.

## Applied

The width, skipped-rules, `classDef`, and fit-gap fixes landed through `product/plans/design-ui-diagram-width.md`, which records how the markup was tested and where it departed from the drafts. The slimming landed through `product/plans/design-ui-slimming.md`. No eval tested it: the user chose to look again only if rules keep getting skipped.

## Rejected

Prose cap, decided by the user on 2026-11-02: pages of long text alone keep `65ch`, and a page with diagrams uses the 1100px column. The investigation found the rule arrived whole in migration commit `4bca452` from `agent-skills`, with no reason beyond "a wide viewport", and its earlier history is not traced. A phone does not explain it, because `65ch` at 15px is about 526px, wider than a 400px screen. The `ceh-business-plan` page shell, which capped text at `72ch` above 960px diagrams, moved to one shared right edge.

## Pending drafts

None.
