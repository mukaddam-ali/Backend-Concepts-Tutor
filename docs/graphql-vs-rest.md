# GraphQL vs REST

GraphQL is an alternative to REST for designing APIs, built around letting the client specify exactly what data it needs in a single request.

## The problems GraphQL addresses

- **Over-fetching**: a REST endpoint like `/users/42` might return a fixed set of fields, even if the client only needs the user's name. The extra data is wasted bandwidth.
- **Under-fetching**: if the client also needs the user's recent orders, it might need a second request to `/users/42/orders` — and a third for something else. Multiple round trips add latency, especially on mobile networks.

## How GraphQL works

- The server defines a **schema**: a strongly-typed description of all the data types and relationships available (e.g. a `User` type with `name`, `email`, and a list of `orders`).
- The client sends a single **query** describing exactly which fields it wants, potentially spanning multiple related types, and the server returns exactly that shape of data — nothing more, nothing less.
- There's typically a single endpoint (e.g. `/graphql`) rather than many resource-specific URLs.
- **Mutations** are GraphQL's equivalent of `POST`/`PUT`/`DELETE` — named operations that change data.

## Trade-offs vs REST

**GraphQL advantages:**
- One request can fetch exactly the data needed across multiple related resources, reducing round trips and over-fetching.
- Strongly-typed schema serves as living documentation and enables good tooling (autocomplete, validation).
- Clients can evolve independently without needing new server endpoints for every new data-shape requirement.

**REST advantages:**
- Simpler to build, cache, and reason about — HTTP caching (via URLs and `Cache-Control` headers) works naturally with REST's resource-based URLs, but is harder with GraphQL's single endpoint.
- Easier to rate-limit and monitor per-resource, since REST endpoints map cleanly to specific operations.
- Lower learning curve and less server-side complexity (no schema/resolver layer to build and maintain).

## When to choose which

GraphQL tends to shine in applications with complex, deeply nested data and multiple client types with different data needs (e.g. a mobile app and a web app hitting the same backend but wanting different fields). For simpler APIs, or where HTTP caching and operational simplicity matter more, REST is usually the more practical default.
