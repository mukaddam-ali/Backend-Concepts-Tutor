# Testing Fundamentals: Unit, Integration, and Functional Tests

Automated tests catch bugs before they reach users and let developers
change code with confidence that they haven't broken something else.
Different test types check different things.

## Unit testing

Tests a single, small unit of code (usually one function or method) in
isolation, with any dependencies replaced by mocks/stubs. Fast to run
(often thousands per second) and pinpoint exactly what broke.

```python
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
```

**Best for:** business logic, calculations, edge cases in a single function
— the bulk of a healthy test suite is usually unit tests.

## Integration testing

Tests how multiple components work together — e.g. does the code that
writes to the database actually produce the correct rows, does an API
endpoint correctly call the service layer which correctly calls the
database. Slower than unit tests (often involves a real or realistic
database, not a mock) but catches bugs unit tests can't — like two
correctly-unit-tested components that don't actually fit together
correctly.

```python
def test_create_user_endpoint(test_client, test_db):
    response = test_client.post("/api/users", json={"name": "Alice"})
    assert response.status_code == 201
    assert test_db.query(User).filter_by(name="Alice").first() is not None
```

## Functional testing

Tests a complete feature from the user's perspective, verifying the system
behaves correctly against its requirements — often black-box (not
concerned with internal implementation, just correct input → output
behavior). Overlaps conceptually with integration testing but is framed
around user-facing behavior/requirements rather than internal component
interaction. In a backend context, this often looks like hitting real API
endpoints end-to-end and checking the full response matches expectations.

## The testing pyramid

A common mental model: **many** fast unit tests at the base, **fewer**
integration tests in the middle, and a **small number** of slow, full
end-to-end/functional tests at the top. This balances fast feedback (unit
tests catch most bugs quickly) against confidence that the whole system
actually works together (a smaller number of slower, broader tests).

## Why backend engineers should care

- Tests catch regressions automatically — changing one part of a codebase
  without accidentally breaking another.
- They document expected behavior in a way that stays up to date (unlike
  comments, which can silently go stale) — a failing test is a strong
  signal that either the code or the assumption behind it changed.
- Well-tested code is easier to refactor confidently, since you'll know
  immediately if a change broke something.

## Free resources

- [Python: unittest documentation](https://docs.python.org/3/library/unittest.html)
- [pytest documentation](https://docs.pytest.org/) — a widely used, free Python testing framework.
- [Martin Fowler: TestPyramid](https://martinfowler.com/bliki/TestPyramid.html) — free, widely referenced article on the testing pyramid concept.
