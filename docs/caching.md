# Caching

Caching stores a copy of expensive-to-compute or expensive-to-fetch data somewhere fast, so future requests can be served quickly without redoing the work.

## Why cache

- Reduce load on a database or downstream service.
- Reduce response latency for the end user.
- Reduce cost (fewer expensive queries or API calls).

## Common caching layers in a backend

- **In-memory application cache**: data cached inside the running process (e.g. a Python dict or an LRU cache). Fast, but lost on restart and not shared across multiple server instances.
- **Distributed cache (Redis / Memcached)**: a separate, shared cache service that all your application servers can read from and write to. Survives individual server restarts and is shared across a fleet of servers.
- **CDN (Content Delivery Network)**: caches static assets (images, JS, CSS) or even full page responses at edge locations physically close to users, reducing latency.
- **HTTP caching**: using headers like `Cache-Control`, `ETag`, and `Last-Modified` so browsers and intermediate proxies can cache responses without hitting your server at all.

## Cache invalidation strategies

Cache invalidation — deciding when cached data is stale and must be refreshed — is famously one of the hardest problems in computer science.

- **TTL (Time To Live)**: cached data automatically expires after a fixed duration (e.g. 5 minutes). Simple, but data can be stale for up to the TTL window.
- **Write-through**: every write to the database also updates the cache immediately, keeping them in sync.
- **Cache-aside (lazy loading)**: the application checks the cache first; on a miss, it reads from the database and populates the cache for next time.
- **Explicit invalidation**: when data changes, the application explicitly deletes or updates the relevant cache entry.

## Trade-offs

Caching trades some consistency (the cache might be briefly out of date) for a large gain in speed and reduced load. The right strategy depends on how tolerant your application is of serving slightly stale data.
