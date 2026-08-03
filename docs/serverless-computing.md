# Serverless Computing

"Serverless" doesn't mean there's no server — it means the backend
developer never has to provision, manage, or scale one. You write a
function, upload it, and the cloud provider handles running it, scaling it,
and shutting it down when it's not needed.

## How it works

You write a small unit of code — a **function** — that responds to a
trigger: an HTTP request, a message arriving in a queue, a file uploaded
to storage, a scheduled timer. The cloud provider (AWS Lambda, Google Cloud
Functions, Azure Functions are the major examples) runs that function only
when triggered, automatically scaling from zero instances to many in
response to demand, and you're typically billed per invocation and
execution time rather than for a server running continuously.

## Advantages

- **No server management**: no OS patching, no capacity planning, no
  scaling configuration to maintain.
- **Automatic scaling**: from handling zero requests to a sudden traffic
  spike, without any manual intervention.
- **Cost efficiency for spiky/infrequent workloads**: you pay for actual
  execution time, not for an idle server waiting for occasional traffic.
- **Fast to deploy small, independent pieces of functionality** — a good
  fit for event-driven tasks (resize an uploaded image, process a queue
  message, respond to a webhook).

## Disadvantages

- **Cold starts**: if a function hasn't run recently, the first invocation
  can be noticeably slower while the provider spins up an execution
  environment — a real concern for latency-sensitive APIs.
- **Execution time limits**: most providers cap how long a single function
  invocation can run, making serverless a poor fit for long-running
  processes.
- **Vendor lock-in risk**: serverless functions are often tightly coupled
  to a specific cloud provider's ecosystem and APIs, making migration
  between providers harder than with portable containers.
- **Harder local development/debugging**: testing the exact production
  environment locally is less straightforward than with a container you
  can run identically anywhere.
- **Not cost-effective for constant, high-volume traffic** — at that point,
  a continuously-running server (or a container/Kubernetes-based
  deployment) is often cheaper than paying per-invocation.

## Serverless vs containers

They're not mutually exclusive design choices for a whole system — many
real architectures use both: containers/Kubernetes for the core,
continuously-running application, and serverless functions for
event-driven side tasks (processing uploads, sending notifications,
scheduled cleanup jobs) that don't justify a continuously-running service
of their own.

## Free resources

- [AWS Lambda documentation](https://docs.aws.amazon.com/lambda/)
- [Google Cloud Functions documentation](https://cloud.google.com/functions/docs)
- [roadmap.sh/backend](https://roadmap.sh/backend)
