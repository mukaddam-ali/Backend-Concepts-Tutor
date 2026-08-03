# Resilience Patterns: Building for Scale and Failure

In a distributed system, things fail: a downstream service goes down, a
network call times out, traffic spikes beyond capacity. Resilience patterns
are established techniques for handling this gracefully instead of letting
one failure cascade into a full outage.

## Circuit breaker

Mirrors an electrical circuit breaker: if calls to a downstream service
keep failing, the circuit "trips" and the system stops calling that service
for a while, immediately returning a fallback response instead of waiting
for (and piling up) more failed/slow requests. After a cooldown period, it
allows a few test requests through — if they succeed, the circuit "closes"
again and normal calls resume. This prevents a struggling downstream
service from being overwhelmed further, and prevents the calling service
from wasting resources on calls that are very likely to fail anyway.

## Backpressure

A mechanism for a system to signal "I'm at capacity, slow down" back to
whatever is sending it work, rather than silently accepting more than it
can handle and collapsing. For example, a message queue consumer that's
falling behind can signal the producer to slow down, or a service can
reject new requests with a `503 Service Unavailable` once its internal
work queue is full, instead of accepting requests it has no hope of
processing in time.

## Throttling

Deliberately limiting the rate of requests a system processes, either to
protect itself (similar to rate limiting, see that document, but often
applied internally between services rather than at the public API) or to
smooth out how work is applied to a downstream dependency.

## Graceful degradation

Designing a system to keep providing *some* useful functionality when part
of it fails, rather than failing completely. For example, an e-commerce
site whose recommendation service is down might still let users browse and
purchase products — just without personalized recommendations — instead of
the whole page failing to load.

## Load shifting

Redirecting load away from an overwhelmed or failing component — to
another region, another instance, a cache, or a queued/deferred processing
path — to keep the overall system responsive even when one part is under
stress.

## Why these patterns matter together

These patterns share a common theme: assume failure *will* happen, and
design explicitly for what the system should do when it does, rather than
only designing for the happy path. A backend built only for the case where
everything works correctly tends to fail catastrophically the first time
something doesn't; a backend built with these patterns degrades gracefully
instead. This connects directly to observability (you need to detect these
conditions — see the Observability document) and to architectural choices
like microservices, where more moving parts means more places these
patterns become necessary.

## Free resources

- [Martin Fowler: CircuitBreaker](https://martinfowler.com/bliki/CircuitBreaker.html) — free, widely referenced article.
- [AWS Builders' Library: Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) — free, practical resilience patterns writeup.
- [roadmap.sh/backend](https://roadmap.sh/backend)
