---
schema: plan/v1
title: Slim design-ui by moving conditional recipes beside their markup
status: ready
created: 2026-11-02
---

## Goal

An agent loading `ceh-ui-design:design-ui` reads what applies on every run and opens one section of
`references/examples.md` only when its surface meets that section's condition. The flow that matters
most: an agent building a page with no app-wide state reads no command dock rules, and an agent with
app-wide state is told in one line where they are. The source is the slimming row of
`product/retros/2026-10-30-repeat-mistake.md`, and the reason is vision principle 5, only the delta.

## Scope

**In:**

- Command dock, Variants board, Lifecycle colors, Identity monograms, and Inputs on dense surfaces
  move to `references/examples.md`, each leaving a one-line trigger in `SKILL.md` that states its
  condition.
- Procedure step 3 and the Finishing recipes intro tell the agent to read only the section a trigger
  names, instead of consulting the whole file on every build.
- Anti-patterns keeps only what no other rule in `SKILL.md` still states after the moves.
- Motion loses the one bullet of general performance advice.
- Every description of `examples.md` as markup only says it also holds the conditional rules.
- The retro's slimming row becomes `applied`, and its draft leaves Pending drafts.

**Out:**

- An eval: the user chose to land without one and look again only if rules keep getting skipped.
- The Theme layer, because other plugins invoke the skill for it.
- The design pass, archetypes, hierarchy, navigation, states, Review pass, token and class contract,
  Humanized tables, Section headers, and Diagrams: each applies on almost every run.
- The Content width prose cap: it waits on the user's answer to the separate investigation.
- Stat blocks and Micro-interactions: the retro does not name Stat blocks, and Micro-interactions
  is already short.

## Design

- **The cut rule:** what applies on every run stays inline, what applies only when a component is
  present moves to `references/examples.md`, and what restates another section goes. This fits
  `decision-skill-bundled-files.md`, under which `design-ui` is a catalog exception.
- **Size:** the cut rule wins over a byte target, because cutting a rule to hit a number loses
  guidance. The estimate is about 5,400 bytes off the 32,567 at this plan's creation, and the build
  reports the real figure.
- **Trigger wording:** a model can skip a link, and an agent may not know a component's name, so each
  trigger states the condition from its own section, then the section:
  - "App-wide state exists: read `references/examples.md` § Command dock".
  - "Items move through known stages: read `references/examples.md` § Lifecycle stepper".
  - "Rows show named entities: read `references/examples.md` § Identity monogram".
  - "A form field sits inside a card, or takes free text: read `references/examples.md` § Input as
    recessed well".
  - "The user asks for options, design-pass question 2 or 4 has two answers that both fit, or a flow's
    behavior is the open question: read `references/examples.md` § Variants board".

  The builder takes each condition's exact words from its source section, and these lines are the
  shape.

- **Where moved text goes:** each section joins its existing `examples.md` section, above the markup,
  and an existing intro sentence that restates the moved text is dropped. Variants board has no
  section there yet, so it gets one first in the file, because the design pass comes before the
  recipes.
- **Text moves whole:** moved sentences change only where a reference to "above" or "below" would
  break. Rewording during a move hides what changed. A sentence that stays and points at moved text
  is fixed too, such as Humanized tables' "(next recipe)".
- **Scrollbars stay inline:** "Theme scrollbars app-wide" sits inside Inputs on dense surfaces but
  applies to every themed surface, so Phase 1 moves it to the Anti-patterns finish tell about OS
  scrollbars.
- **Anti-patterns:** these bullets go, because each is stated by a rule that stays: everything
  centered, every section boxed, uniform spacing, hero on a document, two primary buttons, lone `h1`,
  happy path only, same-background slab, `#` column, red zero, global state repeated, and five type
  sizes. The last one's three-font half goes with it, because the Tidewater theme ships three
  families. These stay: gradient hero, emoji, brand wash, OS scrollbars, and state machine as plain
  text, whose only rule moves in Phase 1.
- **Motion:** cut only "Move and resize with `transform` and `opacity`", which is general performance
  advice. "Keep the layout still" and "Show progress, not suspense" stay, because they carry opinions
  stated nowhere else: no entrance animation, no staggered reveals, no looping outside a live state.
- **Names that stay:** Review pass item 7 and the Finishing recipes intro still name lifecycle colors
  and the dock, because a reviewer checks them when the component is present.
- **Version:** `ceh-ui-design` PATCH, because this is a content update. It rides in the build's PR
  with a changelog entry and a `docs/PLUGIN_VERSIONS.md` row. `plugin.json`'s description still names
  a variants board, which remains true.
- **Local gate:** as in `design-ui-diagram-width.md`, `validate.py` runs on a clean export of the
  staged index, because this checkout fails its `hygiene` check on git-ignored files.

## Phases

### Phase 1: Move the conditional recipes

- **Builds:** the five moves, the five triggers, the scrollbar line's new place, the Procedure step 3
  and Finishing recipes wording, the `examples.md` intro, and the descriptions in the plugin
  `README.md` and `plugins/CLAUDE.md`.
- **Check:** a throwaway script takes each line `git diff` removes from `SKILL.md` and prints any not
  found in `references/examples.md`, and only the sentences Design says change may print. `grep -c
"^#### Command dock\|^### Variants board\|^#### Lifecycle colors\|^#### Identity monograms\|^#### Inputs on dense"`
  on `SKILL.md` prints `0`. Each of the five section names appears once in a `SKILL.md` trigger,
  by `grep -c` per name.
- **Status:** todo

### Phase 2: Cut what restates another section

- **Builds:** the Anti-patterns and Motion cuts named in Design.
- **Check:** `grep -c "scrollbar-width: thin"` on `SKILL.md` prints `1`, and a grep finds each kept
  item: `--dur-fast`, `--ease-out`, `prefers-reduced-motion`, "Keep the layout still", "Show
  progress", `.spinner`, and the five kept Anti-patterns bullets. "Move and resize" is gone. `wc -c`
  gives the figure the build reports.
- **Status:** todo

### Phase 3: Land

- **Builds:** the version bump, changelog entry, `docs/PLUGIN_VERSIONS.md` row, and retro update, with
  the row's "see the draft" replaced and `## Applied` naming this plan, then the PR through
  `ceh-git-workflow:pull-request`.
- **Check:** `python tools/validate-plugins/validate.py` passes on a clean export of the index and in
  CI, `grep -c "awaiting approval" product/retros/2026-10-30-repeat-mistake.md` prints `1`, and the
  draft's heading no longer appears under Pending drafts.
- **Status:** todo

## Open

None

## Record

- 2026-11-02 Planned: status ready
- 2026-11-02 Reviewed: Revise first, 4 blocking (Procedure step 3 still opens examples.md on every build; triggers name the component, not its condition; Variants trigger drops the logic prototype; Motion cut has an undecidable test)
- 2026-11-02 Design changed: was "`SKILL.md` ends at least 5,000 bytes smaller", now the cut rule wins and the build reports the figure, because a number could force a good rule out; was three Motion bullets conditional on what the model does untold, now only "Move and resize" goes, because no eval can apply that test
- 2026-11-02 PR: #188 https://github.com/cheneeheng/ceh-claude-code-library/pull/188
