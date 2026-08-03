# Web Security Fundamentals

Beyond authentication/authorization and CORS (covered in their own
documents), a few foundational security concepts come up constantly in
backend work.

## HTTPS and TLS/SSL

**HTTPS** is HTTP layered on top of **TLS** (Transport Layer Security, the
modern successor to SSL) — it encrypts traffic between client and server so
it can't be read or tampered with in transit. Without it, anyone on the
network path (a public Wi-Fi network, an ISP, an attacker) could read
passwords, tokens, and data in plain text. Certificates (issued by a
Certificate Authority) let a client verify it's actually talking to the
real server, not an impersonator. HTTPS is table stakes for any production
backend today, not an optional extra.

## Hashing algorithms

Hashing converts input data into a fixed-size output in a one-way
(non-reversible) manner — critical for storing passwords safely.

- **MD5 and SHA-1**: fast, but considered broken/weak for security purposes
  (fast hashing is bad for password storage — it makes brute-force
  guessing cheap — and both have known cryptographic weaknesses). Still
  fine for non-security uses like checksums.
- **bcrypt and scrypt**: purpose-built for password hashing — deliberately
  slow and configurable (a "work factor"), making brute-force attacks
  computationally expensive even if a password database leaks. This is
  what you should actually use to store passwords.

Never store passwords in plain text, and never use fast general-purpose
hashes like MD5/SHA for passwords — use bcrypt, scrypt, or Argon2.

## OWASP and common risks

**OWASP** (Open Web Application Security Project) publishes a well-known,
regularly updated "Top 10" list of the most critical web application
security risks. Recurring themes across editions include:

- **Injection** (e.g. SQL injection — untrusted input executed as code
  or query logic; parameterized queries and ORMs largely prevent this,
  see the ORMs document).
- **Broken authentication** (weak session handling, credential stuffing).
- **Sensitive data exposure** (not encrypting data in transit or at rest).
- **Broken access control** (failing to check authorization on every
  request — see the Authentication & Authorization document).
- **Security misconfiguration** (default credentials, verbose error
  messages leaking internals, unnecessary exposed services).

## CSP (Content Security Policy)

A response header that tells the browser which sources of content
(scripts, styles, images) are allowed to load on a page, primarily as a
defense against **Cross-Site Scripting (XSS)** — where an attacker injects
malicious script into a page. A strict CSP can prevent injected scripts
from executing even if an XSS vulnerability exists elsewhere.

## Server security basics

- Keep dependencies and the OS/runtime patched — many real-world breaches
  exploit known, already-patched vulnerabilities in outdated software.
- Run services with the least privilege necessary (a web app process
  shouldn't run as root, a database user for an app shouldn't have
  admin rights it doesn't need).
- Don't expose internal services (databases, admin panels, debug
  endpoints) directly to the public internet.

## Free resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/) — free, official, industry-standard.
- [MDN: Transport Layer Security (TLS)](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Transport_Layer_Security)
- [MDN: Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)
