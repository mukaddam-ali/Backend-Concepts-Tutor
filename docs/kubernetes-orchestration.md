# Kubernetes and Container Orchestration

Docker (see the Containerization document) solves "how do I package and run
one container consistently." Kubernetes solves the next problem: "how do I
run hundreds of containers, across many machines, reliably, at scale."

## What container orchestration solves

Running a handful of containers by hand is manageable. Running a
production system with dozens of services, each needing multiple instances
for redundancy, scaled up and down based on load, restarted automatically
on failure, and deployed without downtime — that requires automation. An
**orchestrator** handles this automatically instead of requiring a human to
manage it manually.

## Core Kubernetes concepts

- **Pod**: the smallest deployable unit — one or more tightly-coupled
  containers that are scheduled together on the same machine.
- **Node**: a physical or virtual machine that runs pods.
- **Cluster**: a set of nodes managed together by Kubernetes.
- **Deployment**: describes the desired state for a set of pods (e.g. "run
  5 replicas of this API service") — Kubernetes continuously works to make
  reality match this desired state.
- **Service**: a stable network address for a set of pods, since
  individual pods are ephemeral (they get created and destroyed, and their
  IP addresses change) — a Service provides a consistent way to reach
  "whichever pods are currently running this."
- **ConfigMap / Secret**: externalized configuration and sensitive values
  (API keys, credentials) kept separate from the container image itself —
  consistent with the Twelve-Factor App principle of config in the
  environment (see the Architectural Patterns document).

## What Kubernetes actually does for you

- **Self-healing**: if a pod crashes or a node fails, Kubernetes
  automatically restarts or reschedules it elsewhere.
- **Scaling**: manually or automatically adjust the number of running
  instances of a service based on load (horizontal scaling — see that
  document).
- **Rolling updates and rollbacks**: deploy a new version gradually,
  monitoring for failures, and roll back automatically if something goes
  wrong — directly supporting the deployment strategies described in the
  CI/CD document (rolling, canary deployments).
- **Load balancing**: automatically distributes traffic across healthy
  pod instances for a service.
- **Service discovery**: pods can find and talk to other services by a
  stable name, without needing to know specific IP addresses that change
  as pods are recreated.

## When you actually need it

Kubernetes solves real problems, but it's genuinely complex to operate —
many small applications and teams are well served by simpler deployment
approaches (a single server, a managed platform-as-a-service, or a handful
of plain Docker containers behind a load balancer) long before Kubernetes'
capabilities are actually needed. It becomes valuable once you're running
enough services, at enough scale, that manual container management is
genuinely no longer feasible.

## Free resources

- [Kubernetes documentation (free, official)](https://kubernetes.io/docs/home/)
- [Kubernetes Basics interactive tutorial (free, official)](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
