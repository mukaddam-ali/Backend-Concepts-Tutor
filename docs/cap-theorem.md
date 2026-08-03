# CAP Theorem

CAP theorem describes a fundamental trade-off in distributed databases —
systems where data is spread across multiple machines connected by a
network that can fail.

## The three properties

- **Consistency (C)**: every read receives the most recent write, or an
  error. All nodes see the same data at the same time.
- **Availability (A)**: every request receives a (non-error) response,
  without guaranteeing it's the most recent data.
- **Partition tolerance (P)**: the system keeps working even if network
  communication between nodes is lost or delayed (a "partition").

## The actual claim

CAP theorem states that when a network partition happens (nodes can't talk
to each other), a distributed system must choose between **Consistency**
and **Availability** — it cannot guarantee both at that moment.

Since network partitions are a real, unavoidable possibility in any
distributed system (network cables get unplugged, data centers lose
connectivity, requests time out), **partition tolerance isn't really
optional** for a distributed system — so in practice, CAP theorem is
mostly about choosing between **CP** (consistent but may reject requests
during a partition) and **AP** (available but may return stale data during
a partition).

## CP vs AP in practice

- **CP systems**: prioritize correctness over uptime during a partition.
  If a node can't confirm it has the latest data, it refuses the request
  rather than risk returning wrong data. Traditional relational databases
  configured for strong consistency, and systems like Google Spanner or
  etcd (used for distributed coordination), lean CP.
- **AP systems**: prioritize staying responsive over strict correctness
  during a partition. Every node answers requests even if it might be
  slightly out of date, and the system reconciles inconsistencies later
  (a strategy called "eventual consistency"). Cassandra and DynamoDB,
  configured in typical usage, lean AP.

## Why this matters for backend engineers

CAP theorem explains *why* different databases make different default
trade-offs, and helps frame the right question when picking a data store
for a distributed system: "if the network partitions, do I need this data
to always be correct, or do I need this system to always respond?" A
banking ledger typically needs correctness (CP); a social media "like
count" can tolerate being briefly stale in exchange for the app never
appearing down (AP).

This connects directly to the trade-offs discussed in the Database
Replication & Sharding document — replicated systems are exactly where CAP
theorem's trade-offs become concrete engineering decisions.

## Free resources

- [roadmap.sh/backend](https://roadmap.sh/backend)
- [IBM: What is the CAP theorem?](https://www.ibm.com/topics/cap-theorem) — free overview.
