# Architectural Patterns: Twelve-Factor Apps, SOA, and Service Mesh

Beyond the monolith-vs-microservices choice (covered in its own document),
a few architectural patterns and methodologies come up repeatedly in
backend system design.

## The Twelve-Factor App

A widely referenced methodology for building software-as-a-service apps
that are portable, scalable, and easy to deploy consistently across
environments. Selected principles:

- **Config in the environment**: store configuration (database URLs,
  API keys) in environment variables, not hardcoded in code — the same
  build can run in dev/staging/production with different config.
- **Stateless processes**: application processes should be stateless and
  share nothing (see the REST APIs document on statelessness) — any
  persistent state lives in a backing service (database, cache), not in
  the process's memory.
- **Disposability**: processes should start up fast and shut down
  gracefully, supporting fast scaling and robust deployments.
- **Dev/prod parity**: keep development, staging, and production as
  similar as possible, to catch environment-specific bugs early.
- **Logs as event streams**: write logs to stdout as a stream of events,
  and let the execution environment handle routing/storage — don't manage
  log files inside the app itself.

These principles underpin a lot of modern cloud-native and containerized
application design (see the Containerization/Docker and CI/CD documents).

## Service-Oriented Architecture (SOA)

A predecessor/relative of microservices: an architecture where
functionality is divided into distinct, reusable services that
communicate over a network — often via an **Enterprise Service Bus (ESB)**
that handles routing and message transformation between services. SOA
tends to involve larger, more coarse-grained services and heavier
middleware than typical modern microservices, which favor lighter,
more independent services with less centralized orchestration.

## Service Mesh

A dedicated infrastructure layer for managing service-to-service
communication in a microservices architecture, typically implemented via
lightweight network proxies ("sidecars") deployed alongside each service
instance. A service mesh handles cross-cutting concerns like:

- Load balancing between service instances.
- Retries and timeouts for failed calls.
- Encryption between services (mutual TLS).
- Observability (automatically capturing metrics and traces for
  service-to-service calls — see the Observability document).

The value proposition: without a service mesh, every microservice has to
implement this networking logic itself; with one, it's handled uniformly
at the infrastructure layer, and application code stays focused on
business logic. Common implementations include Istio and Linkerd, usually
deployed on top of Kubernetes.

## Why this matters

As a system grows past a simple monolith, these patterns provide proven
answers to recurring problems: how to configure an app consistently
(twelve-factor), how to structure inter-service communication (SOA), and
how to manage the operational complexity that comes with many
communicating services (service mesh).

## Free resources

- [The Twelve-Factor App (free, official)](https://12factor.net/)
- [Istio documentation](https://istio.io/latest/docs/)
- [roadmap.sh/backend](https://roadmap.sh/backend)
