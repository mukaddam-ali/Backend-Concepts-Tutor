# Authentication vs Authorization

These two terms are often confused, but they answer different questions.

- **Authentication** answers: "Who are you?" It's the process of verifying a user's identity (e.g. checking a password, validating a token).
- **Authorization** answers: "What are you allowed to do?" It's the process of checking whether an authenticated user has permission to perform a specific action or access a specific resource.

A request is typically authenticated first, then authorized.

## Common authentication methods

- **Session-based auth**: after login, the server creates a session and stores it (in memory, a database, or Redis), then gives the client a session ID cookie. Each request includes the cookie, and the server looks up the session.
- **Token-based auth (JWT)**: after login, the server issues a signed JSON Web Token (JWT) containing user info and an expiration. The client sends this token (usually in an `Authorization: Bearer <token>` header) with every request. The server verifies the signature without needing to look anything up in a database, which makes JWTs popular for stateless APIs.
- **OAuth 2.0**: a standard protocol for delegated authorization, most commonly used for "Sign in with Google/GitHub/etc." A third-party provider authenticates the user and issues a token your backend can trust.
- **API keys**: a simple long-lived secret string a client includes with requests, common for server-to-server or third-party API access.

## Common authorization models

- **Role-Based Access Control (RBAC)**: users are assigned roles (e.g. `admin`, `editor`, `viewer`), and permissions are attached to roles rather than individual users.
- **Attribute-Based Access Control (ABAC)**: access decisions are based on attributes of the user, resource, and context (e.g. "editors can edit documents they own during business hours").
- **Access Control Lists (ACLs)**: permissions are attached directly to individual resources, listing which users/roles can do what.

## Security notes

- Never store plaintext passwords — always hash them with a slow, purpose-built algorithm like bcrypt or Argon2.
- Tokens should have short expirations and be sent over HTTPS only.
- Always check authorization on the server, even if the UI hides certain actions — a client-side check is not a security boundary.
