# UI Design Examples

Worked markup for the `design-ui` finishing recipes, in the skill's order. The core rules
(Layout → Density) are fully stated in `SKILL.md` and need no markup here. All snippets use the
bundled theme contract (tokens + component classes) and plain HTML — they translate 1:1 to Svelte
or JSX.

## Command dock

Global state + its one action in a dock below the topbar: three centered panels split by hairline
rules, width-aligned with the content column, accent rule crowning the top. The topbar above it
stays brand + nav on `--bg` so the chrome recedes.

```html
<section
  style="max-width: 1200px; margin: var(--space-4) auto; background: var(--surface);
                border: 1px solid var(--border); border-radius: var(--radius-lg);
                border-top: 3px solid var(--accent); box-shadow: var(--shadow-sm);
                display: flex; align-items: stretch;"
>
  <!-- left: identity -->
  <div
    style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: var(--space-2); padding: var(--space-4);"
  >
    <p class="eyebrow">Current round</p>
    <p
      style="font-family: var(--font-display); font-size: var(--fs-400); display: flex; align-items: center; gap: var(--space-3);"
    >
      Round 2
      <a
        class="mono"
        style="font-size: var(--fs-50); border: 1px solid var(--border); border-radius: var(--radius-full); padding: 2px var(--space-2); text-decoration: none;"
        href="#/round"
        >2 orders</a
      >
    </p>
    <!-- node-and-rail stepper goes here (see lifecycle stepper) -->
  </div>
  <!-- center: the action, with a micro-caption -->
  <div
    style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: var(--space-2); border-inline: 1px solid var(--border); padding: var(--space-4);"
  >
    <button class="btn btn-primary" style="border-radius: var(--radius-full);">
      End turn
    </button>
    <p class="subtle" style="font-size: var(--fs-50);">
      runs the 2 queued orders
    </p>
  </div>
  <!-- right: outcome stat block, whole panel a quiet link -->
  <a
    href="#/history"
    style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: var(--space-2); padding: var(--space-4); text-decoration: none;"
  >
    <p class="eyebrow">Last round</p>
    <div style="display: flex; gap: var(--space-6);">
      <div style="text-align: center;">
        <p class="numeric text-success" style="font-size: var(--fs-500);">1</p>
        <p class="subtle mono" style="font-size: var(--fs-50);">succeeded</p>
      </div>
      <div style="text-align: center;">
        <p class="numeric" style="font-size: var(--fs-500);">$0.12</p>
        <p class="subtle mono" style="font-size: var(--fs-50);">est. cost</p>
      </div>
      <!-- a "failed" column appears only when nonzero — a red zero is noise -->
    </div>
  </a>
</section>
```

## Humanized table

**Bad** — the primitive draft: symbol headers, bare integers, plain-text status, red zero:

```html
<table class="table">
  <tr>
    <th>#</th>
    <th>Status</th>
    <th>OK</th>
    <th>Fail</th>
  </tr>
  <tr>
    <td>2</td>
    <td>done</td>
    <td>1</td>
    <td class="text-danger">0</td>
  </tr>
</table>
```

**Good** — eyebrow header above the panel, words, lifecycle pill, only what happened, semantic
current-row highlight:

```html
<p class="eyebrow">Round history · 2</p>
<p
  class="muted"
  style="font-size: var(--fs-75); margin-bottom: var(--space-3);"
>
  each round runs the orders queued when its turn ended
</p>
<section class="card" style="padding: 0;">
  <table class="table">
    <tr>
      <th>Round</th>
      <th>Status</th>
      <th>Outcome</th>
      <th class="numeric">Cost</th>
    </tr>
    <!-- current (non-done) row: leading edge + wash via inset shadow, keyed to state not position -->
    <tr
      tabindex="0"
      style="background: var(--secondary-wash); box-shadow: inset 3px 0 0 var(--secondary); cursor: pointer;"
    >
      <td>Round 3</td>
      <td><span class="badge badge-secondary">executing</span></td>
      <td class="muted">—</td>
      <td class="numeric">0.04</td>
    </tr>
    <tr tabindex="0" style="cursor: pointer;">
      <td>Round 2</td>
      <td>
        <span class="badge"><span class="dot dot-success"></span> done</span>
      </td>
      <td>
        <span class="text-success">1 succeeded</span> ·
        <span class="text-danger">2 failed</span>
      </td>
      <td class="numeric">0.12</td>
    </tr>
  </table>
</section>
```

## Lifecycle stepper

One color per stage, used everywhere that stage appears. Past muted, current lit with a halo,
future ghosted, rail filled through the current node.

```html
<div
  role="img"
  aria-label="Status: executing"
  style="display: flex; align-items: center;"
>
  <!-- past -->
  <span
    style="width: 10px; height: 10px; border-radius: var(--radius-full); background: var(--fg-subtle);"
  ></span>
  <span
    style="width: var(--space-8); height: 2px; background: var(--secondary);"
  ></span>
  <!-- current: stage color + halo (add a pulse animation only while actively running) -->
  <span
    style="width: 10px; height: 10px; border-radius: var(--radius-full); background: var(--warning); box-shadow: 0 0 0 4px var(--warning-wash);"
  ></span>
  <span
    style="width: var(--space-8); height: 2px; background: var(--border);"
  ></span>
  <!-- future -->
  <span
    style="width: 10px; height: 10px; border-radius: var(--radius-full); background: var(--border);"
  ></span>
</div>
```

## Identity monogram

Stable per-entity color from the data ramp (hash the name to pick `--data-1…6`); wash fill with a
matching hairline border; the initial in the ramp color.

```html
<span
  aria-hidden="true"
  style="display: inline-grid; place-items: center; width: 28px; height: 28px;
      border-radius: var(--radius-md); background: color-mix(in srgb, var(--data-3) 14%, transparent);
      border: 1px solid var(--data-3); color: var(--data-3); font-weight: var(--weight-bold);
      font-size: var(--fs-75);"
  >A</span
>
```

## Input as recessed well, auto-growing

Inside a `--surface` card, the field steps _down_ to `--bg`; short placeholder, explanation in the
tooltip; grows with content but never sideways.

```html
<td>
  <!-- parent table uses table-layout: fixed -->
  <textarea
    class="input mono"
    placeholder="add instruction…"
    title="optional — blank uses the project's instruction template"
    style="background: var(--bg); font-size: var(--fs-75); field-sizing: content;
                   min-height: 38px; max-height: 40vh; resize: vertical; overflow-wrap: anywhere;"
  ></textarea>
</td>
```
