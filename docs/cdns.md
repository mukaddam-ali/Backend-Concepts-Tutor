# Content Delivery Networks (CDNs)

A CDN is a geographically distributed network of servers that cache and deliver content from a location physically close to the end user, instead of every request traveling all the way back to your origin server.

## Why distance matters

Network latency is bounded by the speed of light plus routing overhead — a user in Tokyo requesting a file from a server in Virginia will always wait longer than a user requesting it from a server in Tokyo. A CDN solves this by keeping copies ("edge caches") of your content at many locations ("points of presence" or PoPs) around the world, so users are served from the nearest one.

## What CDNs typically cache

- **Static assets**: images, videos, CSS, JavaScript bundles, fonts — content that doesn't change per-request and is safe to cache for a long time.
- **Full page responses**: for content that's the same for every visitor (e.g. a marketing homepage), some CDNs can cache the entire rendered HTML page.
- Dynamic, personalized responses (e.g. a logged-in user's dashboard) are generally **not** cached by a CDN, since they differ per user.

## How it works, briefly

1. A user requests `example.com/logo.png`.
2. DNS or the CDN's routing directs the request to the nearest edge server.
3. If that edge server already has the file cached, it returns it immediately (a "cache hit") — the origin server is never contacted.
4. If not cached yet (a "cache miss"), the edge server fetches it from the origin, serves it to the user, and caches it for the next request to that region.

## Benefits beyond speed

- **Reduced origin load**: your own servers handle far fewer requests, since most static content is served from the edge.
- **Resilience**: if the origin server briefly goes down, cached content can often still be served from the edge.
- **DDoS mitigation**: many CDN providers absorb and filter malicious traffic at the edge before it ever reaches your infrastructure.

## Cache invalidation

Like any cache (see the caching document), CDN content needs an invalidation strategy: a short TTL for content that changes often, versioned file names (e.g. `app.a1b2c3.js`) so a new deployment naturally gets a new, uncached URL, or explicit "purge" API calls to force-remove stale content from the edge immediately.
