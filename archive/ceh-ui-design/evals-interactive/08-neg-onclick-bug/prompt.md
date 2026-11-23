---
max_turns: 6
timeout_seconds: 120
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

this button's onClick never fires, fix it

```jsx
export function SaveBar({ draft, onSaved }) {
  async function save() {
    await fetch("/api/drafts", { method: "POST", body: JSON.stringify(draft) });
    onSaved();
  }

  return (
    <div className="save-bar">
      <button type="button" onClick={() => save}>
        Save draft
      </button>
    </div>
  );
}
```
