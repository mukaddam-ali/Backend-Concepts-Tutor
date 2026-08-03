# Horizontal vs Vertical Scaling

When a backend system needs to handle more traffic or data than it currently can, there are two fundamentally different ways to add capacity.

## Vertical scaling ("scaling up")

Vertical scaling means making a single server more powerful: more CPU cores, more RAM, faster disks.

**Advantages:**
- Simple — no architectural changes needed, the application code doesn't need to know anything changed.
- No added complexity from coordinating multiple servers.

**Disadvantages:**
- There's a hard ceiling — eventually you run out of bigger hardware to buy, or it becomes extremely expensive.
- A single point of failure — if that one (now very expensive) server goes down, everything is down.
- Usually requires downtime to resize (e.g. rebooting into a bigger instance size in the cloud).

## Horizontal scaling ("scaling out")

Horizontal scaling means adding more servers and distributing load across all of them (typically via a load balancer, see the load balancing document).

**Advantages:**
- Essentially unlimited scaling — need more capacity? Add more servers.
- Better fault tolerance — if one server fails, the others keep serving traffic.
- Can scale down during low-traffic periods to save cost (elastic scaling), especially in the cloud.

**Disadvantages:**
- Requires the application to be designed for it — typically means keeping servers stateless (see the REST API document on statelessness), since a load balancer might route any request to any server.
- Adds operational complexity: service discovery, distributed data consistency, and coordinating deployments across many instances.
- Data storage is harder to scale horizontally than stateless application servers — this is where database replication and sharding come in.

## Which to choose

Vertical scaling is often the pragmatic first move for a young or simple application, since it requires zero architectural changes. Horizontal scaling becomes necessary once you either hit vertical scaling's ceiling, or need high availability (no single server whose failure takes down the whole system). Most large-scale systems ultimately rely primarily on horizontal scaling for their application layer, sometimes combined with vertical scaling for components (like a primary database) that are harder to split across multiple machines.
