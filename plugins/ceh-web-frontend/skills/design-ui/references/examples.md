# UI Design Examples

Worked good/bad markup for the `design-ui` skill, in the same order as the skill: core rules
first (Layout → Density), then one example per finishing recipe. All snippets use the bundled
theme contract (tokens + component classes) and plain HTML — they translate 1:1 to Svelte or JSX.

## Layout — app shell archetype

Skeleton for a data-dense tool (≥5 destinations): fixed sidebar, scrollable content pane, content
capped and left-aligned.

```html
<div
  style="display: grid; grid-template-columns: 240px 1fr; min-height: 100vh;"
>
  <nav aria-label="Primary"><!-- sidebar nav, see Navigation example --></nav>
  <main style="padding: var(--space-8); max-width: 1320px;">
    <!-- page header + content -->
  </main>
</div>
```

Focused flow (auth, checkout) is the only archetype that centers:

```html
<main
  style="max-width: 480px; margin: 0 auto; padding: var(--space-16) var(--space-4);"
>
  <h1>Create your account</h1>
  <!-- titles the task, not the app -->
  <form><!-- one action per step --></form>
</main>
```

## Layout — content width

**Bad** — form and prose stretched across the viewport:

```html
<main style="width: 100%;">
  <p>Body text spanning 1900px is unreadable…</p>
  <form><input class="input" style="width: 100%;" /></form>
</main>
```

**Good** — each content type gets its reading width:

```html
<p style="max-width: 65ch;">Prose caps at 65–75 characters per line.</p>
<form style="max-width: 560px;"><!-- labels above inputs --></form>
<table class="table">
  <!-- tables alone may use the full pane -->
</table>
```

## Layout — spacing rhythm

**Bad** — uniform gaps, no grouping (label, field, and the next section all equidistant):

```html
<div style="display: flex; flex-direction: column; gap: var(--space-4);">
  <label>Name</label><input class="input" /> <label>Email</label
  ><input class="input" />
  <h2>Notifications</h2>
</div>
```

**Good** — within-group < between-group; the section break is 3× the field gap:

```html
<div style="display: flex; flex-direction: column; gap: var(--space-2);">
  <label>Name</label><input class="input" />
</div>
<div
  style="display: flex; flex-direction: column; gap: var(--space-2); margin-top: var(--space-4);"
>
  <label>Email</label><input class="input" />
</div>
<h2 style="margin-top: var(--space-12);">Notifications</h2>
```

## Hierarchy — page header anatomy

Full anatomy when the page has an identity beyond its nav label:

```html
<header
  style="display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: var(--space-8);"
>
  <div>
    <p class="eyebrow">Billing</p>
    <h1>Invoice #1042</h1>
    <p class="muted">Issued 3 Jul 2026 · due in 12 days</p>
  </div>
  <div style="display: flex; gap: var(--space-2);">
    <button class="btn btn-outline">Download PDF</button>
    <button class="btn btn-primary">Send invoice</button>
    <!-- the one primary action -->
  </div>
</header>
```

**Bad** — title repeats the active nav item with nothing added:

```html
<nav>…<a class="has-edge is-active" href="/dashboard">Dashboard</a>…</nav>
<main>
  <h1>Dashboard</h1>
  …
</main>
```

**Good** — either add value or drop the title and promote the content:

```html
<main>
  <h1>Dashboard <span class="muted">· last 30 days</span></h1>
  <!-- or: no h1, first metric row starts immediately -->
</main>
```

## Hierarchy — boxes are not structure

**Bad** — card nesting and per-item boxes:

```html
<div class="card">
  <div class="card">
    <div class="card">Revenue: $12,400</div>
  </div>
</div>
```

**Good** — one card groups the peer set; whitespace and a rule separate items inside:

```html
<section class="card">
  <h2>Revenue</h2>
  <dl>
    <div>
      <dt class="muted">This month</dt>
      <dd class="numeric">$12,400</dd>
    </div>
    <div style="border-top: 1px solid var(--border);">
      <dt class="muted">Last month</dt>
      <dd class="numeric">$11,050</dd>
    </div>
  </dl>
</section>
```

## Navigation — sidebar with grouping and active state

Ordered by frequency, grouped past 7 items, settings pinned to the bottom, current location marked:

```html
<nav
  aria-label="Primary"
  style="display: flex; flex-direction: column; height: 100%; padding: var(--space-4);"
>
  <a class="has-edge is-active" href="/inbox">Inbox</a>
  <a class="has-edge" href="/projects">Projects</a>
  <a class="has-edge" href="/reports">Reports</a>
  <p class="eyebrow" style="margin-top: var(--space-6);">Admin</p>
  <a class="has-edge" href="/members">Members</a>
  <a class="has-edge" href="/billing">Billing</a>
  <a class="has-edge" href="/settings" style="margin-top: auto;">Settings</a>
</nav>
```

Tabs switch peer views of the _same_ object in place — they never navigate away:

```html
<div role="tablist">
  <button role="tab" aria-selected="true" class="has-edge is-active">
    Overview
  </button>
  <button role="tab" aria-selected="false" class="has-edge">Activity</button>
  <button role="tab" aria-selected="false" class="has-edge">Settings</button>
</div>
```

## Color and depth

**Bad** — brand color as decoration, two primaries, semantic color without meaning:

```html
<section
  style="background: var(--secondary-wash); border: 1px solid var(--border); box-shadow: var(--shadow-md);"
>
  <h2 class="text-success">Team members</h2>
  <button class="btn btn-primary">Invite</button>
  <button class="btn btn-primary">Export</button>
</section>
```

**Good** — neutral surface, one depth cue, brand only on the primary action, semantic color only on state:

```html
<section class="card">
  <h2>Team members</h2>
  <span class="badge"><span class="dot dot-success"></span> 12 active</span>
  <button class="btn btn-primary">Invite</button>
  <button class="btn btn-ghost">Export</button>
</section>
```

## States

Empty — one line of what belongs here plus the action that creates it:

```html
<div class="card" style="text-align: center; padding: var(--space-12);">
  <h2>No projects yet</h2>
  <p class="muted">Projects group your team's work in one place.</p>
  <button class="btn btn-primary">Create project</button>
</div>
```

Loading — skeleton mirrors the real layout (spinner only for sub-second, in-place waits):

```html
<div aria-busy="true">
  <div
    style="height: var(--space-6); width: 40%; background: var(--surface-2); border-radius: var(--radius-sm);"
  ></div>
  <div
    style="height: var(--space-4); width: 100%; background: var(--surface-2); border-radius: var(--radius-sm); margin-top: var(--space-3);"
  ></div>
</div>
```

Error — what happened plus what to do, in place:

```html
<div class="card" role="alert">
  <p class="text-danger">Couldn't load projects.</p>
  <p class="muted">Check your connection, then try again.</p>
  <button class="btn btn-outline">Retry</button>
</div>
```

Overflow — truncation with the full value recoverable; numbers tabular:

```html
<td
  style="max-width: 24ch; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;"
  title="Quarterly infrastructure cost reconciliation"
>
  Quarterly infrastructure cost…
</td>
<td class="numeric">1,204.50</td>
```

## Density

Dense table for a daily-use tool — compact rows, small type, tabular numbers:

```html
<table class="table" style="font-size: var(--fs-50);">
  <tr style="height: 34px;">
    <td>ord_8231</td>
    <td><span class="dot dot-live"></span> Processing</td>
    <td class="numeric">240.00</td>
  </tr>
</table>
```

The same data on an occasional consumer surface would instead run airy: card per order,
`--fs-200` type, `--space-8` section gaps.

## Finishing recipes — command dock

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
    <!-- node-and-rail stepper goes here (see lifecycle recipe) -->
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

## Finishing recipes — section header above the panel

The eyebrow + caption labels the section from the page, outside the card; the panel holds only
the table. Same vocabulary on every view.

```html
<p class="eyebrow">Queued orders · 2</p>
<p
  class="muted"
  style="font-size: var(--fs-75); margin-bottom: var(--space-3);"
>
  when the turn ends, each order runs its plan in its repo
</p>
<section class="card" style="padding: 0;">
  <table class="table">
    <!-- see humanized table -->
  </table>
</section>
```

## Finishing recipes — humanized table

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

**Good** — words, lifecycle pill, only what happened, semantic current-row highlight:

```html
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
```

## Finishing recipes — lifecycle stepper

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

## Finishing recipes — identity monogram

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

## Finishing recipes — input as recessed well, auto-growing

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

App-wide scrollbar theming (once, in global CSS):

```css
* {
  scrollbar-width: thin;
  scrollbar-color: var(--border-strong) transparent;
}
```
