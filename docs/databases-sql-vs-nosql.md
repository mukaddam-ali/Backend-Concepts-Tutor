# SQL vs NoSQL Databases

Backend systems need to persist data, and the choice of database shapes almost every other design decision.

## SQL (relational) databases

Examples: PostgreSQL, MySQL, SQLite, SQL Server.

- Data is organized into **tables** with a fixed schema (columns and types defined up front).
- Relationships between tables are expressed with **foreign keys**, and joins combine data across tables.
- Strong support for **ACID transactions** (Atomicity, Consistency, Isolation, Durability) — a transaction either fully succeeds or fully fails, and concurrent transactions don't corrupt each other's data.
- Best when data is structured, relationships matter (e.g. orders belonging to customers), and you need strong consistency guarantees (e.g. financial data).

## NoSQL (non-relational) databases

Examples: MongoDB (document), Redis (key-value), Cassandra (wide-column), Neo4j (graph).

- **Document stores** (MongoDB) store flexible, JSON-like documents — good when your data doesn't fit a rigid schema or changes shape often.
- **Key-value stores** (Redis) store simple key → value pairs, optimized for extremely fast lookups (often used for caching, sessions).
- **Wide-column stores** (Cassandra) are built for massive write throughput and horizontal scale across many machines.
- **Graph databases** (Neo4j) are optimized for querying relationships (e.g. social networks, recommendation engines).
- Generally trade some consistency guarantees for horizontal scalability and schema flexibility.

## How to choose

- Need multi-row transactions, strict schema, and complex joins? → **SQL**.
- Need to scale writes across many servers, or your data is naturally document-shaped/schema-less? → **NoSQL**.
- Many real systems use both: a relational database as the source of truth, plus Redis for caching and session storage.

## SQLite specifically

SQLite is a special case: a serverless, single-file SQL database. There's no separate database server process — the whole database lives in one file on disk. This makes it ideal for local applications, embedded systems, mobile apps, and small-scale or offline tools, where running a full database server would be overkill.
