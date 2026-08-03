# ORMs and the N+1 Query Problem

## What is an ORM?

An ORM (Object-Relational Mapper) lets backend code interact with a
relational database using objects and method calls instead of writing raw
SQL. Examples: **Prisma** and **TypeORM** (JavaScript/TypeScript),
**SQLAlchemy** (Python), **Hibernate** (Java), **Entity Framework** (.NET).

```python
# Raw SQL
cursor.execute("SELECT * FROM users WHERE id = ?", (42,))

# With an ORM (conceptually)
user = User.objects.get(id=42)
```

**Advantages:**
- Less boilerplate — no manually writing and parsing SQL for common
  operations.
- Database portability — many ORMs can target multiple database engines
  with the same code.
- Built-in protection against SQL injection, since queries are parameterized
  automatically.
- Schema migrations are often integrated (tracking and applying database
  schema changes over time).

**Disadvantages:**
- Can obscure what SQL is actually being run, making performance problems
  harder to spot (see N+1 below).
- Complex queries (multi-table joins, advanced aggregations) are sometimes
  easier to write in raw SQL than to express through an ORM's API.
- Adds a layer of abstraction and dependency to learn, on top of SQL itself.

## The N+1 query problem

This is the single most common ORM-related performance bug.

**The scenario:** you fetch a list of N records, then loop over them and
fetch a related record for each one individually.

```python
orders = Order.objects.all()        # 1 query: fetch all orders
for order in orders:
    print(order.customer.name)      # 1 query PER order to fetch its customer
```

If there are 100 orders, this runs **1 + 100 = 101 queries** instead of 2.
Each query has network round-trip overhead, so this can turn a fast page
load into a slow one as the dataset grows — and it's easy to introduce
accidentally, since the code *looks* like simple object access, not
database queries.

**The fix:** eager loading — fetch the related data upfront in a single
additional query (or a single join), instead of once per row.

```python
orders = Order.objects.select_related('customer').all()  # 1 query total,
                                                            # joins customers in
for order in orders:
    print(order.customer.name)      # no extra query — already loaded
```

Most ORMs provide this under names like `select_related`/`prefetch_related`
(Django), `include` (Prisma), or `JOIN FETCH` (Hibernate/JPA).

## Why this matters for backend engineers

N+1 problems are notoriously easy to write without noticing during
development (small datasets hide the issue) and only surface as real
performance problems in production once tables grow. Knowing to look for
this pattern — and how to check the actual SQL an ORM is generating — is a
core backend debugging skill.

## Free resources

- [Prisma documentation](https://www.prisma.io/docs)
- [SQLAlchemy documentation](https://docs.sqlalchemy.org/)
- [Django ORM: select_related and prefetch_related (official docs)](https://docs.djangoproject.com/en/stable/ref/models/querysets/#select-related)
