# Observability: Logging, Metrics, and Tracing

Observability is the ability to understand what's happening inside a running system from the outside — essential once an application is too complex to just "read the code and know." It rests on three main pillars.

## Logging

Logs are timestamped records of discrete events: "user 42 logged in," "payment failed: card declined," "request to /api/orders took 340ms." They're the most detailed and most flexible observability tool, but also the most expensive to store and search at scale.

- **Structured logging** (writing logs as JSON with consistent fields like `timestamp`, `level`, `user_id`, `message`) is far more useful than plain text, since it can be filtered and queried programmatically.
- **Log levels** (`DEBUG`, `INFO`, `WARNING`, `ERROR`) let you control verbosity — noisy debug logs in development, quieter info/error-only logs in production.

## Metrics

Metrics are numeric measurements aggregated over time: request count, average response time, error rate, CPU usage, queue depth. Unlike logs, metrics are cheap to store at high volume because they're pre-aggregated numbers, not full event records.

- **Counters**: values that only increase (e.g. total requests served).
- **Gauges**: values that go up and down (e.g. current memory usage, current queue length).
- **Histograms**: distributions of values (e.g. response time percentiles — p50, p95, p99 — which matter more than the average, since averages hide slow outliers).

Metrics are what power dashboards and alerts ("page someone if error rate exceeds 5% for 5 minutes").

## Tracing

A single user request in a modern backend often passes through multiple services (an API gateway, an auth service, a database, a payment provider). **Distributed tracing** follows one request's full journey across all of them, showing exactly how long each step took and where time was spent.

- A **trace** represents one end-to-end request.
- Each **span** within a trace represents one unit of work (e.g. "call the payments service," "query the database").
- Tracing is especially valuable in microservices architectures, where a slow response could originate in any one of many services, and logs/metrics alone might not make the exact bottleneck obvious.

## Why all three matter together

Metrics tell you *something* is wrong (error rate spiked). Tracing tells you *where* in the request path it went wrong (the payments service call is slow). Logs tell you *why* (payments service logged "connection pool exhausted"). Relying on only one pillar usually means slower incident response, since you're missing part of the picture.
