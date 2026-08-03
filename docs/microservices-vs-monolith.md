# Microservices vs Monolith

This is a fundamental architectural decision about how to structure a backend system as it grows.

## Monolithic architecture

A single application that contains all functionality — the API, business logic, and often the database access — deployed and run as one unit.

**Advantages:**
- Simple to develop, test, and deploy early on — one codebase, one deployment.
- Easier to reason about, since everything runs in the same process (no network calls between internal components).
- No distributed systems complexity (no need to handle partial failures between services).

**Disadvantages:**
- As the codebase grows, it can become hard to understand and modify safely (tight coupling between modules).
- The entire application must be redeployed for any change, even a small one.
- Scaling is all-or-nothing — you can't scale just the heavily-used part of the app independently.

## Microservices architecture

The application is split into multiple small, independently deployable services, each responsible for a specific piece of business functionality (e.g. a `users` service, an `orders` service, a `payments` service), communicating over the network (often via REST APIs or message queues).

**Advantages:**
- Teams can develop, deploy, and scale services independently.
- A failure in one service doesn't necessarily bring down the whole system.
- Each service can use the technology stack best suited to its job.

**Disadvantages:**
- Significant added complexity: network calls between services can fail, so you need retries, timeouts, and circuit breakers.
- Harder to test end-to-end, since a single user action might involve several services.
- Requires more operational maturity: service discovery, distributed tracing, monitoring across many moving parts.
- Data consistency across services is harder — you often can't use a simple database transaction across service boundaries.

## Which to choose

Most experienced teams recommend **starting with a monolith**. It's simpler to build and reason about, and you often don't yet know where the real scaling or team boundaries will be. Split into microservices later, once specific parts of the system have a clear, independent scaling or ownership need — not as a default starting architecture.
