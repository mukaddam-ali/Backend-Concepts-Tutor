# Database Indexing

An index is a data structure that lets a database find rows matching a query without scanning every row in a table.

## The problem indexes solve

Without an index, a query like `SELECT * FROM users WHERE email = 'a@b.com'` requires the database to check every single row in the `users` table — a **full table scan**. On a table with millions of rows, this is slow.

## How an index works (conceptually)

Most indexes use a **B-tree** structure: a balanced tree that keeps values sorted, letting the database jump directly to matching rows in roughly logarithmic time instead of scanning linearly. Think of it like the index at the back of a book — instead of reading every page to find a topic, you jump straight to the right page number.

When you create an index on a column (e.g. `CREATE INDEX idx_users_email ON users(email);`), the database maintains this sorted structure automatically as rows are inserted, updated, or deleted.

## Trade-offs

Indexes are not free:

- **Faster reads**: queries filtering or sorting on an indexed column become much faster.
- **Slower writes**: every `INSERT`, `UPDATE`, or `DELETE` must also update every index on that table, adding overhead.
- **Extra storage**: each index takes additional disk space.

Because of this trade-off, you shouldn't index every column — only columns that are frequently used in `WHERE` clauses, `JOIN` conditions, or `ORDER BY` clauses.

## Types of indexes

- **Single-column index**: indexes one column (most common).
- **Composite (multi-column) index**: indexes a combination of columns together, useful when queries frequently filter on the same combination (e.g. `(last_name, first_name)`).
- **Unique index**: like a normal index, but also enforces that no two rows have the same value (commonly used for things like `email`).
- **Primary key**: nearly every database automatically creates a unique index on the primary key column.

## Practical guidance

A good starting point: index foreign keys, columns frequently used in `WHERE` filters, and columns used to sort results. Avoid over-indexing tables with heavy write traffic, since each additional index slows down every insert and update.
