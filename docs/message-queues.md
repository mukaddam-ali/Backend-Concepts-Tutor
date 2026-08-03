# Message Queues

A message queue lets different parts of a system communicate asynchronously by sending messages through an intermediary broker, instead of calling each other directly.

## Why use a message queue

- **Decoupling**: the sender (producer) doesn't need to know anything about the receiver (consumer), or even whether it's currently running.
- **Buffering / smoothing traffic spikes**: if a sudden burst of work arrives, messages queue up instead of overwhelming a downstream service. Consumers process them at a sustainable pace.
- **Reliability**: most queues persist messages until they're successfully processed, so work isn't lost if a consumer crashes mid-task.
- **Background/async processing**: long-running tasks (sending emails, processing images, generating reports) can be handed off to a queue so the original request can return to the user immediately instead of blocking.

## Common tools

- **RabbitMQ**: a traditional message broker implementing protocols like AMQP, good for complex routing between producers and consumers.
- **Apache Kafka**: a distributed event streaming platform, built for very high throughput and for cases where multiple independent consumers need to read the same stream of events (not just "consume once and remove").
- **Redis Streams / Pub-Sub**: lightweight messaging built into Redis, good for simpler use cases already using Redis for caching.
- **Cloud-managed queues**: e.g. AWS SQS, Google Cloud Pub/Sub — managed services so you don't run the broker yourself.

## Basic pattern

1. A **producer** publishes a message to a queue (e.g. "send welcome email to user 42").
2. The message sits in the queue until a **consumer** is ready.
3. A **consumer** (often called a "worker") picks up the message and processes it.
4. Once processing succeeds, the consumer acknowledges the message, and it's removed from the queue. If it fails, the message can be retried or sent to a "dead-letter queue" for investigation.

## When to reach for one

If an operation doesn't need to complete before you respond to the user (e.g. sending a confirmation email after signup), or if you need to smooth out bursty load, a message queue is usually the right tool. If the caller genuinely needs the result immediately, a synchronous API call is simpler and more appropriate.
