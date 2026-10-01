---
name: domain-modeling
description: >-
  Load this skill when designing or modifying domain entities and their boundaries: defining new
  entity IDs, choosing identifier formats, creating or extending status fields, designing state
  transition rules, modelling ownership and relationships, or setting layer boundaries between route
  handlers, services, and the database layer. Auto-load whenever a new entity type is introduced, a
  status enum is added or changed, an ID field is defined, or a service/route/db responsibility
  split is decided.
disable-model-invocation: false
user-invocable: false
license: Apache-2.0
---

# Domain modeling

## Immutable identifiers

Every entity has an application-generated, prefixed, URL-safe identifier. Never use database auto-increment as the public ID — leaks row counts and is meaningless in logs.

```python
import secrets


def generate_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_urlsafe(12)}"


session_id = generate_id("sess")  # sess_abc123...
resource_id = generate_id("res")  # res_xyz456...
```

## Bounded status enums

Status values must come from an explicit, closed set. Never trust free-form strings from external callers for status fields.

```python
from enum import StrEnum


class ResourceStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
```

```ts
const ResourceStatus = {
  Active: "active",
  Archived: "archived",
  Deleted: "deleted",
} as const;
type ResourceStatus = (typeof ResourceStatus)[keyof typeof ResourceStatus];
```

## Immutability rules

- IDs are set once at creation, never changed
- `created_at` timestamps are set once, never updated
- Status transitions must be validated — not all transitions are legal
- Document all legal and illegal transitions explicitly

## Layer boundaries

Model the flow of control so each layer has one job. The boundaries are part of the domain design,
even though the concrete directory layout lives in `ceh-scaffolding`.

- Route handlers contain no business logic — they call services.
- Services contain no SQL — they call the database layer. The database layer contains no business logic.
- One mutation path per aggregate — if multiple services could write the same entity, route them through a single state manager.
