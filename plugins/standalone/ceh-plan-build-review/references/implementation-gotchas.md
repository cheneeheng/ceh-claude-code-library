# Implementation gotchas

Common technical traps in fullstack projects. Apply them when writing §04 (Backend), §05
(Frontend), or §06 (LLM): address applicable gotchas proactively in the plan, do not wait for the
developer to discover them. Each entry names the trap, why it happens, and the fix. Examples use
Python/TypeScript but the principle applies across stacks.

**Backend**

- **Middleware order is counterintuitive.** Most frameworks apply middleware in reverse
  registration order (last registered = outermost), so CORS and auth middleware registered in the
  wrong order fail preflight or auth checks silently. Always document the intended middleware stack
  order in the plan with a comment explaining why.
- **ORM async + migration tool mismatch.** With an async ORM driver (asyncpg, aiomysql, motor),
  migration tools (Alembic, Flyway) default to synchronous connections and fail or silently skip
  tables. Bridge the async engine explicitly for migrations. Migration tools also only discover
  models that have been imported: a missing import in the model registry makes the table invisible
  to autogenerate.
- **Cached config breaks tests.** Singletons or cached config objects (e.g. `@lru_cache` on a
  settings loader) capture environment variables at first call. Tests that set env vars after
  import silently use the wrong config, including connecting to the wrong database. Mutate the
  cached instance in a test fixture before any test runs, or clear the cache between tests.
- **Sequential ID / index assignment under concurrency.** `SELECT MAX(n) + 1` without a row lock
  lets two concurrent transactions compute the same next value. Use a database sequence, an
  auto-increment column, or `SELECT FOR UPDATE` inside a transaction whenever assigning ordered
  identifiers.
- **Resource ownership: 403 not 404.** Returning 404 when a resource exists but belongs to another
  user leaks its existence. Always return 403 (or consistently 404 for both cases), never 404
  specifically for "exists but not yours".
- **Implicit resource creation race.** Creating a resource on the first dependent action (e.g.
  creating a session when the first message is sent) leaves a window where a second concurrent
  action arrives before the resource exists. Create resources as an explicit user action and
  trigger dependent operations after creation confirms.

**Frontend**

- **Stable references for framework config objects.** Frameworks that accept component registries
  or config objects (graph libraries, data grid libraries, rich text editors) compare them by
  reference. Defined inside a component, a new object is created on every render and the framework
  tears down and remounts all children. Define them at module level, outside any component.
- **httpOnly cookie cross-origin.** Cookies set by the API are not sent by the browser on
  cross-origin requests unless `withCredentials: true` (or equivalent) is set on the HTTP client.
  Missing this makes auth fail silently on every request.
- **SSE: native EventSource limitations.** The browser's `EventSource` API only supports GET
  requests and cannot send custom headers. Endpoints that require a POST body or auth header must
  use `fetch()` with `ReadableStream` parsing instead.
- **React StrictMode double-invocation.** In development, React 18 StrictMode intentionally mounts
  components twice, so any `useEffect` that triggers a one-time action (auto-send, session init,
  analytics event) fires twice. Guard with a `useRef(false)` flag that is set on first invocation.
- **Volume mounts shadow installed packages.** Mounting a source directory into a container
  overwrites the container's package directory with the host's (which has none). Add an anonymous
  volume for `node_modules` (and `.venv` for Python) to shield them from the host mount.

**Auth and sessions**

- **Token refresh race condition.** Multiple concurrent requests that each receive a 401 each
  attempt a token refresh independently. The second refresh call typically fails (token already
  rotated) and logs the user out. Queue concurrent 401s and resolve them all with the result of a
  single refresh call.
- **Refresh cookie parameter mismatch.** A refresh cookie set with different parameters in register
  vs login (different `path`, `samesite`, or `secure` values) results in two separate cookies, one
  of which is never sent. Set cookie parameters identically across all endpoints that issue it.

**LLM integration**

- **API role constraints.** Most LLM APIs only accept specific role values in the messages array
  (e.g. `user` and `assistant` only, no `system` role in the array). Messages stored with other
  roles in the database must be transformed before sending to the API. Plan this transformation in
  the build-messages function.
- **Context window overflow.** Long-running sessions eventually exceed the model's context limit.
  Plan a truncation or summarisation strategy upfront: sliding window, summarise-and-replace, or
  drop oldest. Deciding this after the fact requires retrofitting the message model.
- **SSE heartbeat composition.** Composing a keep-alive heartbeat with a streaming LLM response is
  error-prone if done via task cancellation/restart. Use a shared async queue: one producer task
  writes LLM tokens, a second writes periodic pings, a single consumer reads from the queue and
  yields to the client.
