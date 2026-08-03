# Database Types: Beyond SQL vs NoSQL

"SQL vs NoSQL" is the big-picture split, but "NoSQL" actually covers several
quite different categories of database, each suited to different problems.
Knowing the category names and real examples helps when picking the right
tool.

## Relational (SQL)

Structured tables with fixed schemas and strong relational integrity.
Examples: **PostgreSQL**, **MySQL**, **MariaDB**, **Microsoft SQL Server**,
**Oracle Database**. Best for structured data with clear relationships and
where transactional correctness matters (see the Transactions & ACID
document).

## Document databases

Store flexible, JSON-like documents rather than rigid rows. Examples:
**MongoDB**, **CouchDB**. Best when records don't share a uniform structure
or the schema changes frequently.

## Key-value stores

The simplest model: a key maps to a value, optimized for extremely fast
lookups. Examples: **Redis**, **Memcached**. Best for caching, session
storage, and anywhere raw lookup speed matters more than query flexibility.

## Graph databases

Optimized for traversing relationships between entities (friends-of-friends,
recommendation paths, fraud-detection networks). Examples: **Neo4j**,
**Amazon Neptune**. Best when the relationships between data points matter
as much as the data points themselves.

## Column-family (wide-column) databases

Store data in columns rather than rows, built for very high write
throughput across many machines. Examples: **Cassandra**, **ScyllaDB**.
Best for massive-scale, write-heavy workloads (e.g. logging, time-series
at extreme scale) where horizontal scalability matters more than
relational querying.

## Time-series databases

Purpose-built for data points indexed by time — metrics, sensor readings,
financial ticks. Examples: **InfluxDB**, **TimescaleDB**. Optimized for
fast writes of timestamped data and time-range queries (e.g. "average CPU
usage over the last hour").

## Search engines

Not a general-purpose database, but often used alongside one, specifically
for full-text search and fast filtering across large text datasets.
Examples: **Elasticsearch**, **Solr**. Common pattern: keep the source of
truth in a relational or document database, and sync a searchable copy into
a search engine for fast text queries.

## How to choose

Start by asking what shape your data actually is (rows and relationships?
flexible documents? simple key-value pairs? a graph of relationships?
time-stamped events?) and what you need to optimize for (transactional
correctness, raw lookup speed, write throughput, full-text search). Many
real systems use more than one: a relational database as the primary store,
Redis for caching, and Elasticsearch for search — each database doing the
one thing it's actually good at.

## Free resources

- [PostgreSQL documentation](https://www.postgresql.org/docs/)
- [MongoDB documentation](https://www.mongodb.com/docs/)
- [Redis documentation](https://redis.io/docs/)
- [roadmap.sh/backend](https://roadmap.sh/backend)
