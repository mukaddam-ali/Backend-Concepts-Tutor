# API Design and Versioning

Good API design makes an API predictable and easy to integrate with. Versioning lets an API evolve without breaking existing clients.

## API design principles

- **Consistency**: use the same naming conventions, casing, pagination style, and error format across every endpoint.
- **Predictable resource naming**: use plural nouns for collections (`/users`, not `/user`), and nest resources logically (`/users/42/orders`).
- **Meaningful error responses**: return a structured error body with a clear message and machine-readable error code, not just a status code — e.g. `{"error": "invalid_email", "message": "Email format is invalid"}`.
- **Pagination for large collections**: never return an entire table in one response. Use `limit`/`offset` or cursor-based pagination (`?cursor=abc123&limit=20`).
- **Idempotency**: `PUT` and `DELETE` should be idempotent — calling them multiple times with the same input produces the same result as calling them once. This matters because clients may retry requests after network failures.

## Why version an API

Once external clients depend on your API, you can't freely change response shapes or remove fields without breaking them. Versioning gives you a safe way to introduce breaking changes while existing clients keep working against the old version.

## Common versioning strategies

- **URL versioning**: `/api/v1/users`, `/api/v2/users`. Simple and highly visible, the most common approach.
- **Header versioning**: the client specifies a version in a custom header (e.g. `Accept: application/vnd.myapi.v2+json`). Keeps URLs clean but is less discoverable.
- **Query parameter versioning**: `/api/users?version=2`. Less common, easy to overlook.

## Backward-compatible vs breaking changes

- **Backward-compatible** (usually safe without a version bump): adding a new optional field, adding a new endpoint, adding a new optional query parameter.
- **Breaking** (requires a new version): removing or renaming a field, changing a field's type, changing required parameters, changing error response formats.

A good rule of thumb: if an existing, well-behaved client's code would break or misbehave because of your change, it's a breaking change.
