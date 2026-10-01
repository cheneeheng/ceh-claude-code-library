---
name: add-observability
description: >-
  Load this skill when adding or modifying logging, metrics, health checks, or correlation ID
  propagation in a Python service: writing structured log calls, choosing log levels, adding
  Prometheus metrics, defining the health check endpoint, or wiring up correlation ID middleware.
  Auto-load whenever a log call is written, a metric is added, or the /health endpoint is touched.
  Not for frontend/browser logging.
disable-model-invocation: false
user-invocable: true
compatibility: >-
  Requires Python 3.12+ with `structlog` and the OpenTelemetry packages installed as project
  dependencies via `uv sync` - not assumed present globally. Exporting traces additionally needs a
  reachable OTLP collector endpoint; without one, logging still works and tracing is a no-op.
license: Apache-2.0
---

# Add Observability to a Python Service

All log output is structured JSON. Never use `print()` or unstructured interpolation.

```python
import structlog

log = structlog.get_logger()

log.info("request_completed", endpoint="/resources", status=200, duration_ms=42)
log.warning("upstream_timeout", service="payment-api", attempt=2)
log.error("database_connection_failed", host=settings.db_host, error=str(e))
```

| Level     | Use for                                       |
| --------- | --------------------------------------------- |
| `DEBUG`   | Detailed diagnostics (disabled in production) |
| `INFO`    | Normal operations                             |
| `WARNING` | Unexpected but recoverable                    |
| `ERROR`   | Failures requiring attention                  |

Do not log at `INFO` on every request — use `DEBUG` for high-frequency events.

**Never log:** secrets, tokens, passwords, PII, raw user-provided content, or full external API responses.

## Correlation IDs

Every request carries a `correlation_id`:

- Generated at the API boundary if absent from request headers
- Bound to every log entry via `structlog.contextvars`
- Returned in the `X-Correlation-ID` response header
- Included in API error response bodies

```python
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", generate_id("req"))
    with structlog.contextvars.bound_contextvars(correlation_id=correlation_id):
        response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
```

## Required metrics

| Metric                      | Type      | Labels                              |
| --------------------------- | --------- | ----------------------------------- |
| `requests_total`            | Counter   | `endpoint`, `method`, `status_code` |
| `request_duration_ms`       | Histogram | `endpoint`, `method`                |
| `errors_total`              | Counter   | `error_type`, `endpoint`            |
| `external_calls_total`      | Counter   | `service`, `status`                 |
| `external_call_duration_ms` | Histogram | `service`                           |

Use Prometheus-compatible instrumentation (`prometheus-fastapi-instrumentator` or equivalent).

## Health check endpoint

```
GET /health
```

Returns `200` when healthy:

```json
{ "status": "ok", "database": "ok", "version": "1.4.2" }
```

Returns `503` when any critical dependency is unavailable:

```json
{ "status": "degraded", "database": "error", "version": "1.4.2" }
```

Must verify actual database connectivity — not just process liveness. Used by load balancers, deployment pipelines, and rollback automation.
