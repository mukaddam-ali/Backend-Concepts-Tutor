# Database Replication & Sharding

Application servers scale horizontally fairly easily because they're usually stateless (see horizontal vs vertical scaling). Databases hold state, which makes scaling them out much harder — replication and sharding are the two main techniques for doing it.

## Replication

Replication means keeping copies of the same data on multiple database servers.

- **Primary-replica (leader-follower) replication**: one server (the primary) handles all writes. Changes are copied to one or more replica servers, which handle read queries. This spreads read load across multiple machines while keeping writes simple and consistent (only one server accepts them).
- **Benefits**: read scalability (more replicas = more read capacity), and improved availability (if the primary fails, a replica can be promoted to take over).
- **Replication lag**: replicas typically apply changes slightly after the primary does. An application that writes data and immediately reads it back from a replica might briefly see stale data — a consideration when designing read-after-write flows.

## Sharding (horizontal partitioning)

Sharding means splitting a single logical database into multiple physical databases ("shards"), each holding a subset of the data — for example, users A–M on shard 1, users N–Z on shard 2.

- Unlike replication, sharding scales **write** capacity too, since different shards can accept writes independently and in parallel.
- A **shard key** determines which shard a given row lives on (e.g. `user_id % number_of_shards`, or a range of IDs). Choosing a good shard key that distributes data and load evenly is one of the hardest parts of sharding.
- **Cross-shard queries** (e.g. "find all orders across all users placed today") become much harder, since the data needed lives on multiple separate databases that must each be queried and the results merged.
- Resharding (changing the number of shards later) is a major operation, since it usually requires physically moving data between shards.

## Replication and sharding together

Large-scale systems commonly combine both: data is sharded across many databases for write scalability, and each shard is also replicated for read scalability and fault tolerance.

## When you actually need this

Replication for read scaling is common even at moderate scale, since it's relatively straightforward to add. Sharding is a significant architectural commitment that adds real complexity — most applications should exhaust simpler options first (better indexing, caching, vertical scaling, read replicas) before reaching for sharding, and only adopt it once a single database server's write throughput genuinely can't keep up.
