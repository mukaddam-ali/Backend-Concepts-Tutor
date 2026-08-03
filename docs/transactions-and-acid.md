# Database Transactions & ACID

A transaction groups multiple database operations into a single unit: either all of them succeed and are saved, or none of them are. This matters any time an operation involves more than one change that must stay consistent together.

## A motivating example

Consider transferring money between two bank accounts: subtract $100 from Account A, add $100 to Account B. If the subtract succeeds but the server crashes before the add happens, $100 has vanished. Wrapping both operations in a transaction guarantees that either both happen or neither does.

```sql
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 'A';
UPDATE accounts SET balance = balance + 100 WHERE id = 'B';
COMMIT;
```

If anything goes wrong partway through, the database can `ROLLBACK` and undo everything in the transaction, as if it never happened.

## ACID properties

Relational databases describe strong transactional guarantees with the acronym ACID:

- **Atomicity**: a transaction's operations either all succeed or all fail together — no partial results.
- **Consistency**: a transaction moves the database from one valid state to another, never violating defined rules (e.g. constraints, foreign keys).
- **Isolation**: concurrent transactions don't interfere with each other — it should look as if transactions ran one at a time, even if they actually overlapped.
- **Durability**: once a transaction is committed, it survives a crash or power loss — the change is permanently saved.

## Isolation levels

Full isolation (transactions never see each other's in-progress changes) can hurt performance under heavy concurrent load, so databases offer tunable **isolation levels** that trade some correctness guarantees for speed:

- **Read Uncommitted**: transactions can see other transactions' uncommitted changes (rarely used — allows "dirty reads").
- **Read Committed**: only committed changes are visible to other transactions (a common default).
- **Repeatable Read**: a transaction sees a consistent snapshot for its whole duration, even if other transactions commit changes meanwhile.
- **Serializable**: the strictest level — transactions behave as if they ran one after another, with no overlap effects at all.

## Why this matters for backend design

Any operation that touches multiple related rows or tables that must stay consistent (placing an order and decrementing inventory, transferring funds, updating a user and logging an audit record) should be wrapped in a transaction. Without one, a crash or concurrent request at the wrong moment can leave your data in an inconsistent state that's hard to detect and fix later.
