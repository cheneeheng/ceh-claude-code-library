---
name: make-ui-accessible
description: >-
  Load this skill when writing component markup with interactive elements, images, forms, or
  navigation in any web frontend. Auto-load whenever a .svelte or .tsx file is created or modified
  and HTML structure is being written or reviewed. Accessibility rules are framework-agnostic — they
  apply to SvelteKit and React alike.
disable-model-invocation: false
user-invocable: true
paths:
  - "**/*.svelte"
  - "**/*.tsx"
  - "**/*.html"
license: Apache-2.0
---

# Make the UI Accessible

- All interactive elements must be keyboard-accessible
- Images must have `alt` attributes (empty `alt=""` for decorative images)
- Use semantic HTML (`<button>`, `<nav>`, `<main>`, `<section>`, `<header>`) — not `<div>` for everything
- `svelte-check` runs a11y checks — fix all warnings before opening a PR

## Keyboard navigation

- Every action reachable by mouse must be reachable by keyboard
- Visible focus indicator must never be removed (`outline: none` without a replacement is forbidden)
- Tab order must follow the visual reading order
- Modal dialogs must trap focus while open and return focus to the trigger on close

## ARIA

Use native HTML semantics first. Add ARIA only when no native element fits:

```svelte
<button onclick={handleAction}>Submit</button>
<button aria-label="Close dialog" onclick={close}>✕</button>
<p aria-live="polite" aria-atomic="true">{statusMessage}</p>
<button aria-expanded={open} onclick={toggle}>Details</button>
```

Do not add `role="button"` to a `<div>` — use `<button>`. Never use `aria-hidden="true"` on a focusable element.

## Forms

```svelte
<label for="topic">Topic</label>
<input id="topic" type="text" bind:value={topic} />

<input id="email" aria-describedby="email-error" aria-invalid={!!emailError} />
<span id="email-error" role="alert">{emailError}</span>
```

## Color and contrast

- Text contrast ratio: 4.5:1 minimum (3:1 for large text ≥ 18px or bold ≥ 14px)
- Do not rely on color alone to convey information — pair with an icon or text label
