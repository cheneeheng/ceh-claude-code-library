---
name: write-sveltekit-code
description: >-
  Load this skill when adding or modifying SvelteKit routes, writing load functions, managing Svelte
  stores, or building components. Auto-load whenever a +page.svelte, +page.server.ts, +page.ts,
  store, or component file is created or modified.
disable-model-invocation: false
user-invocable: true
paths:
  - "**/*.svelte"
  - "**/+page*.ts"
  - "**/+layout*.ts"
  - "**/+server.ts"
compatibility: >-
  Requires Node.js 20+ or `bun` on PATH, with `@sveltejs/kit`, `svelte`, and `vite` installed as
  project dependencies and network access for the first install. None is assumed to be present
  globally; the dev server also needs a free local port.
license: Apache-2.0
---

# Write SvelteKit Code

## Route file naming

| File                | Purpose                                                                        |
| ------------------- | ------------------------------------------------------------------------------ |
| `+page.svelte`      | Page UI component                                                              |
| `+page.server.ts`   | Server-only load function and form actions (access to private env vars and DB) |
| `+page.ts`          | Universal load function (runs on server + client)                              |
| `+layout.svelte`    | Layout wrapper applied to child routes                                         |
| `+layout.server.ts` | Server-only layout load                                                        |
| `+error.svelte`     | Error page for this route segment                                              |

Use `+page.server.ts` when the load requires server-side credentials or direct database access.

## Load functions

```ts
export const load: PageServerLoad = async ({ params }) => {
  const session = await apiClient.getSession(params.session_id);
  if (!session) error(404, "Session not found"); // SvelteKit error(), not throw new Error()
  return { session };
};
```

- Throw `error()` from `@sveltejs/kit` for HTTP errors
- Use `redirect()` from `@sveltejs/kit` for redirects — do not call `goto()` inside load functions
- Load functions return data; they do not directly mutate state

## Svelte stores

Stores live in `src/lib/stores/`. Updated **only** from API responses — never mutated directly by components.

```ts
export const sessionStore = writable<SessionState | null>(null);
export const openChallenges = derived(
  sessionStore,
  ($session) => $session?.challenges.filter((c) => c.status === "open") ?? [],
);
```

- Derived stores are preferred over computed values inside components
- Do not define stores inside components — they live in `$lib/stores/`

## Components: props only, no direct store writes

```svelte
<script lang="ts">
  type Props = {
    challenges: Challenge[];
    onChallengeClick: (id: string) => void;  // callback, not direct store write
  };
  let { challenges, onChallengeClick }: Props = $props();
</script>
```

## Centralized API client

All `fetch` calls go through `src/lib/api/client.ts`. Components and stores never call `fetch` directly.

```ts
export const apiClient = {
  async sendMessage(
    sessionId: string,
    content: string,
  ): Promise<MessageResponse> {
    const response = await fetch(
      `${PUBLIC_API_BASE_URL}/sessions/${sessionId}/message`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      },
    );
    if (!response.ok) {
      const err = await response.json();
      throw new ApiRequestError(response.status, err.error);
    }
    return response.json();
  },
};
```

## Environment variables

```ts
import { PUBLIC_API_BASE_URL } from "$env/static/public"; // safe for browser
import { DATABASE_URL } from "$env/static/private"; // server-only
```

Never use `import.meta.env.VITE_*`.

## Error handling

```ts
class ApiRequestError extends Error {
  constructor(
    public readonly status: number,
    public readonly error: ApiError,
  ) {
    super(error.message);
  }
}
```

Component pattern:

```svelte
<script lang="ts">
  let error = $state<string | null>(null);
  let loading = $state(false);

  async function handleSend() {
    error = null; loading = true;
    try {
      const result = await apiClient.sendMessage(sessionId, input);
      onSuccess(result.state);
    } catch (e) {
      error = e instanceof ApiRequestError
        ? e.error.message
        : 'An unexpected error occurred. Please try again.';
    } finally { loading = false; }
  }
</script>

{#if error}<p class="error">{error}</p>{/if}
```

- Never expose internal error codes or stack traces to users
- Map `error.code` values to user-friendly messages in a centralized map
- Always show the `correlation_id` so users can report it

## Reactive declarations

```svelte
<script lang="ts">
  let { challenges }: { challenges: Challenge[] } = $props();
  const openCount = $derived(challenges.filter((c) => c.status === 'open').length);
</script>
```

Do not put complex logic in a `$derived` expression — use `$derived.by(() => { ... })` or extract a named function.
