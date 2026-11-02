---
schema: repeat-mistake/v1
date: 2026-10-30
other_file: none
---

# Repeat mistakes — 2026-10-30

The page this retro measured is a private workspace page. It has since been redrawn without Mermaid,
so its Mermaid version survives only in private workspace history. The evidence below describes it
in words and numbers.

| Mistake                                                                                    | Evidence                                                                                                                                                                                                                                                                                                                                               | Rung | Fix                                                                                                            | Proof        | Status            |
| ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---- | -------------------------------------------------------------------------------------------------------------- | ------------ | ----------------- |
| A Mermaid page had no width rule, so each diagram and heading took whatever width it got   | User: "Some of the mermaid diagrams is horizontally scrollable and some no", "Why the diagrams have no max width". The page improvised a cutoff that treated diagrams differently by their width against the panel. At a 1762px window, 3 of 13 diagrams scrolled, 1 shrank to 73%, and the title measured 1706px against 561px and 647px for the text | 1    | Worked column and fit markup in `references/examples.md`, with a width rule in the Diagrams recipe             | not provable | applied           |
| A page built with `design-ui` skipped rules the skill already states                       | A `less-code` comment on the page excused copying only the theme tokens it used instead of the whole `brand.css`. The same page had no font import, no contents rail with six `h2` sections, and no `document.fonts.ready`                                                                                                                             | 5    | A Document audit item in the skill's Review pass, and `less-code` named as no exemption from the theme install | not provable | applied           |
| `var()` inside a Mermaid `classDef` breaks every diagram on the page                       | This session's rebuild: `classDef ok fill:var(--success-wash),...` rendered "Syntax error in text, mermaid version 11.17.2" in every panel. Same result on 12.2.0, by a run on 2026-11-02                                                                                                                                                              | 1    | The same worked markup colours nodes from page CSS, so no `classDef` is needed                                 | not provable | applied           |
| The `design-ui` prose cap may be wrong: text stops at about 65 characters on a wide screen | `skills/design-ui/SKILL.md:95`: "Prose: 65–75 characters per line (`max-width: 65ch`). Never let body text span a wide viewport." User, after seeing text and diagrams share one 1100px edge: "I think that might be a bug. I would expect the text to fill the screen width up until a fixed max width"                                               | 5    | To investigate later, see the draft                                                                            | not provable | awaiting approval |
| The Mermaid fit draft was proven on flowcharts only and has no print or narrow-column rule | The page's 23 diagrams were all flowcharts, so "23 of 23 diagrams" and the fixed 16px label say nothing about other types. `grep '@media print'` found nothing in `design-ui/SKILL.md`, `references/examples.md`, or either `brand.css`                                                                                                                | 1    | Replacement fit markup, and a label check before the rule goes beyond flowcharts                               | not provable | applied           |
| `design-ui` keeps conditional recipes and restated rules inline, so every run reads them   | `design-ui/SKILL.md` is 30,831 bytes (`wc -c`). Command dock, Variants board, Inputs, Lifecycle colors, and Identity monograms apply only when that component is present. Most of Anti-patterns restates the rules above it. Row 2 above shows a page skipping rules the skill already states, though nothing measured whether length is the cause     | 5    | Slim the file by about 20%, see the draft                                                                      | not provable | awaiting approval |

## Why this rung

- No width rule: rung 1 is the top rung. A copyable fit replaces the improvised one.
- Skipped rules: rung 1 does not fit because these pages are written freehand, with no generator to fix. Rungs 2 to 4 do not fit because no setting or validator sees a page in a git-ignored folder, and this is the first measured miss, so a hook is not earned yet.
- `var()` in `classDef`: rung 1 is the top rung. The worked markup leaves no `classDef` to get wrong.
- Prose cap: the rule is written guidance, so any change stays at rung 5. Whether it should change at all is still open.
- Fit draft gaps: rung 1 is the top rung. The worked markup carries the print and narrow-column rules, so a later session copies them instead of remembering them.
- Slimming: the problem is the skill's own text, so the change stays at rung 5. No setting or validator can decide what an agent needs to read.

## Applied

The width, skipped-rules, `classDef`, and fit-gap fixes landed through `product/plans/design-ui-diagram-width.md`, which records how the markup was tested and where it departed from the drafts.

## Pending drafts

### The `design-ui` prose cap may be wrong: text stops at about 65 characters on a wide screen

Not a ready edit. The user set this investigation for after the fixes above land, and nothing changes until then.

- **The user's view:** text should fill the screen up to one fixed max width, 1100px on this page. They expect the character limit was meant to make things look good on a phone.
- **What to check first:** a phone may not explain the rule. `65ch` at 15px is about 526px (scaled from a measured `80ch` of 647px), wider than a 400px phone screen, so the cap does nothing there, and the rule's own words name "a wide viewport". Run `git log -L95,95:plugins/standalone/ceh-ui-design/skills/design-ui/SKILL.md` and read where the rule came from, including its source in `agent-skills`.
- **Evidence so far:** on the private page, the user approved text at 1100px, about 135 characters per line. That page's paragraphs run one to three lines, so it says little about long documents.
- **Found on 2026-11-02:** the rule arrived whole in the migration commit `4bca452` from `agent-skills`, with no reason beyond "a wide viewport". That repo has no local clone here and GitHub's code search returned nothing, so its earlier history is not traced. The repo disagrees with itself: the `ceh-business-plan` page shell caps text at `72ch` above 960px diagrams, the layout the user called sloppy, and the user's standing preference is one shared right edge when a page holds text and wider elements. No evidence yet covers a page that is only long text.
- **Questions to settle:** should the cap become one fixed max width for all page content, and in which archetypes? Does a long report need a shorter line than this page? If the rule changes, the "Prose" bullet changes with it, and the "overrides the prose cap" wording in the Document bullet under Content width goes away.

### `design-ui` keeps conditional recipes and restated rules inline, so every run reads them

Not a ready edit. The user approved it going ahead with its own plan, in its own PR after the fixes above, with no eval. The full comparison is in a private competitor analysis that a fresh clone does not have, so the proposal is repeated here.

diagram-design is not the reason to slim. Only the Diagrams recipe overlaps it, 1,183 of 30,831 bytes, and that stays because Mermaid stays. The reason is vision principle 5, only the delta.

The rule to cut by: what applies on every run stays inline, what applies only when a component is present moves to `references/examples.md`, and what restates another section goes. That fits `decision-skill-bundled-files.md`, under which `design-ui` is already a catalog exception.

| Section                              | Bytes | Proposal                                                                                      | Estimated saving        |
| ------------------------------------ | ----- | --------------------------------------------------------------------------------------------- | ----------------------- |
| Command dock                         | 1,733 | Move beside its markup. Only for app-wide state, and its examples come from one app           | about 1,600             |
| Variants board                       | 1,437 | Move, keep a one-line trigger. Runs only on request or a tie                                  | about 1,300             |
| Anti-patterns                        | 1,366 | Keep only what no rule states: gradient hero, emoji, brand wash                               | about 1,000             |
| Lifecycle colors, Identity monograms | 995   | Move beside their markup                                                                      | about 850               |
| Motion, Micro-interactions           | 2,213 | Keep the token and easing choices and the reduced-motion rule, cut general performance advice | about 800               |
| Inputs on dense surfaces             | 821   | Move beside its markup                                                                        | about 750               |
| **Total**                            |       |                                                                                               | **about 6,300, or 20%** |

Section bytes were measured before the fixes above landed. The savings are estimates, and those fixes added bytes back, so measure again when planning.

These stay: the design pass, archetypes, hierarchy, navigation, and states, which apply to every run; the Review pass, which is the skill's done condition; the token and class contract, because the alternative is reading a 20 KB `brand.css`; Humanized tables and Section headers, which appear on almost every surface; and Diagrams.

- **Skipped links:** a moved recipe can be skipped behind a link, so each needs a one-line trigger in `SKILL.md`, such as "building a dock: read `references/examples.md` § Command dock".
- **Callers:** `ceh-ag-ui` and `ceh-competitor-analysis` invoke this skill for its Theme layer, which this proposal leaves alone.
- **Proof:** no eval has tested any of this, and the user chose to land it without one, looking again only if rules keep getting skipped.
