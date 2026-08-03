# Rate Limiting

Rate limiting restricts how many requests a client can make to an API within a given time window, protecting the backend from overload and abuse.

## Why rate limit

- **Protect infrastructure**: prevent a single client (buggy or malicious) from overwhelming your servers or database.
- **Fair usage**: ensure one heavy user doesn't degrade service for everyone else.
- **Cost control**: for APIs that call metered downstream services (e.g. paid third-party APIs), rate limiting caps how much you spend.
- **Security**: slows down brute-force login attempts and scraping.

## Common algorithms

- **Fixed window**: allow N requests per fixed time window (e.g. 100 requests per minute, resetting every minute on the clock). Simple, but allows bursts right at window boundaries (e.g. 100 requests at 0:59 and another 100 at 1:00).
- **Sliding window**: tracks requests over a rolling time window rather than fixed clock boundaries, smoothing out the boundary-burst problem.
- **Token bucket**: a bucket holds tokens, refilled at a steady rate. Each request consumes a token; if the bucket is empty, the request is rejected or delayed. Allows short bursts up to the bucket size while enforcing a steady average rate.
- **Leaky bucket**: similar to token bucket but processes requests at a constant, fixed rate, smoothing out bursts entirely.

## Implementation notes

- Rate limits are usually tracked per API key, user ID, or IP address.
- A distributed cache like Redis is commonly used to track request counts, since it needs to be shared across all your application servers, not just one.
- When a client is rate-limited, respond with `429 Too Many Requests`, and include a `Retry-After` header telling the client when it can try again.

## Where to enforce it

Rate limiting can be enforced at multiple layers: at the API gateway/load balancer (before requests even reach your application), or inside the application itself. Enforcing it as early as possible (e.g. at the gateway) protects more of your infrastructure from excess load.
