---
type: llm
focus: { source: file, path: signup.html }
weight: 1
---

Judge the page markup and its page-specific styles. Pass only if every claim holds:

1. One centered, narrow form column, capped at about 400–640px; no sidebar and no multi-link nav menu.
2. The h1 of the form names the task (e.g. "Create your account"), not the page or app ("Signup Page", "Sign up form").
3. Each label sits above its input, and each input has a programmatically associated label.
4. Exactly one primary (filled) button and one h1 are visible in any one state; any other action (e.g. "Log in instead") is a link or ghost/outline button. A success screen that replaces the form is a separate state and may have its own h1 and primary button.
5. A field-level error state is designed in the markup or styles (error text tied to a field, using a danger colour token), not only browser defaults.
6. No gradient hero, no glassmorphism, no emoji.
