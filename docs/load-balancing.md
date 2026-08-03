# Load Balancing

A load balancer sits in front of multiple backend servers and distributes incoming requests across them, so no single server is overwhelmed.

## Why load balance

- **Scalability**: instead of one powerful (and expensive) server, you run several smaller ones and spread traffic across them.
- **Availability**: if one server crashes, the load balancer stops sending it traffic and routes requests to the remaining healthy servers — users don't notice.
- **Zero-downtime deployments**: you can update servers one at a time while the load balancer keeps routing traffic to the others.

## Common algorithms

- **Round robin**: requests are distributed to servers in rotating order.
- **Least connections**: send the next request to whichever server currently has the fewest active connections.
- **IP hash**: route a given client's requests consistently to the same server, based on a hash of their IP (useful when some state is still tied to a specific server).
- **Weighted**: give more powerful servers a proportionally larger share of traffic.

## Layers of load balancing

- **Layer 4 (transport layer)**: routes based on IP address and port, without inspecting the actual HTTP request. Very fast, but less flexible.
- **Layer 7 (application layer)**: inspects the actual HTTP request (URL path, headers, cookies) and can make smarter routing decisions, e.g. sending `/api/*` to one set of servers and `/images/*` to another.

## Health checks

Load balancers regularly ping each backend server (e.g. hitting a `/health` endpoint) to confirm it's still responsive. Servers that fail health checks are temporarily removed from the rotation until they recover.

## Relationship to statelessness

Load balancing works best when backend servers are stateless (see REST APIs / session handling) — since any server can handle any request, the load balancer is free to route traffic wherever is most efficient, without worrying about "stickiness" to a particular server.
