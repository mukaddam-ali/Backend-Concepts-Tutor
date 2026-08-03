# Database Normalization

Normalization is the process of organizing a relational database's tables
to reduce data redundancy and avoid update anomalies — situations where the
same fact is stored in multiple places and can become inconsistent.

## The problem it solves

Imagine one big table storing orders with the customer's name and email
repeated on every single order row. If a customer changes their email, you
now have to update it in every order row — miss one, and your data is
inconsistent. Normalization splits this into a `customers` table and an
`orders` table linked by a `customer_id` foreign key, so the email exists
in exactly one place.

## Normal forms (the common ones)

- **First Normal Form (1NF)**: each column holds a single, atomic value (no
  lists or repeated groups crammed into one field), and each row is unique.
- **Second Normal Form (2NF)**: builds on 1NF; every non-key column depends
  on the *entire* primary key, not just part of it (relevant for tables with
  composite keys).
- **Third Normal Form (3NF)**: builds on 2NF; no non-key column depends on
  another non-key column (eliminates "transitive" dependencies — e.g. storing
  both `zip_code` and `city` when city can be derived from zip code).

Most production schemas aim for 3NF as a practical baseline.

## Denormalization: the deliberate trade-off

Sometimes data is *intentionally* duplicated (denormalized) to avoid
expensive joins on frequently-read data — trading some redundancy for read
performance. For example, storing a `product_name` directly on an
`order_item` row (in addition to a `product_id` foreign key) so historical
orders still show the product name even if the product is later renamed or
deleted, and so displaying order history doesn't require a join.

## Normalization vs denormalization: how to choose

- **Normalize** when data consistency matters most, writes are frequent,
  and storage/join cost is secondary — the typical default for transactional
  systems (see the Transactions & ACID document).
- **Denormalize** selectively when read performance is critical and the
  duplicated data either changes rarely or the historical snapshot is
  actually desired (like the order-item example above). This is a common
  pattern in reporting tables, caches, and read-optimized views.

Real systems often do both: a normalized primary schema, with specific
denormalized tables or cached views built for particular high-traffic read
patterns.

## Free resources

- [PostgreSQL documentation: Data Definition](https://www.postgresql.org/docs/current/ddl.html)
- [roadmap.sh/backend](https://roadmap.sh/backend)
