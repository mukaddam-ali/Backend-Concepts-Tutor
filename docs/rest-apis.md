# REST APIs

REST (Representational State Transfer) is an architectural style for designing networked applications. A REST API exposes resources (like `users` or `orders`) as URLs, and clients interact with those resources using standard HTTP methods.

## Core principles

- **Statelessness**: each request from a client contains all the information the server needs. The server does not store client session state between requests.
- **Resource-based URLs**: endpoints represent nouns, not actions. Use `/orders/42`, not `/getOrder?id=42`.
- **Standard HTTP methods**: `GET` reads a resource, `POST` creates one, `PUT`/`PATCH` update one, `DELETE` removes one.
- **Uniform interface**: consistent conventions for naming, status codes, and payload formats across the whole API.
- **Representations**: resources are typically returned as JSON, though REST does not mandate a specific format.

## Common HTTP status codes

- `200 OK` – request succeeded.
- `201 Created` – a new resource was created.
- `204 No Content` – succeeded, nothing to return (common for `DELETE`).
- `400 Bad Request` – the client sent invalid data.
- `401 Unauthorized` – the client is not authenticated.
- `403 Forbidden` – the client is authenticated but not allowed to do this.
- `404 Not Found` – the resource does not exist.
- `500 Internal Server Error` – something broke on the server.

## Example

```
GET /api/users/42        -> fetch user 42
POST /api/users          -> create a new user
PUT /api/users/42        -> replace user 42 entirely
PATCH /api/users/42      -> partially update user 42
DELETE /api/users/42     -> delete user 42
```

## Why statelessness matters

Because no session state is stored on the server between requests, any server instance can handle any request. This makes REST APIs easy to scale horizontally behind a load balancer — you can add more servers without worrying about which server "remembers" a particular client.
