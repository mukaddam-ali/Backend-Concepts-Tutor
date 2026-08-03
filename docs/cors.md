# CORS (Cross-Origin Resource Sharing)

CORS is a browser security mechanism that controls whether JavaScript running on one website is allowed to make requests to a server on a different origin (a different domain, protocol, or port).

## The problem it addresses: the Same-Origin Policy

By default, browsers enforce the **Same-Origin Policy**: a script loaded from `https://app.example.com` cannot, by default, read the response from a request to `https://api.otherdomain.com`. This exists to prevent a malicious site from silently making authenticated requests to other sites on a user's behalf (e.g. using their logged-in banking session cookies).

This becomes a real obstacle for legitimate use cases too — a frontend hosted on `app.example.com` calling its own backend API at `api.example.com` is technically a cross-origin request, since the subdomain differs.

## How CORS works

CORS is the mechanism that lets a server explicitly say "requests from this other origin are allowed." The server includes response headers such as:

```
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
```

The browser checks these headers and only allows the requesting JavaScript to access the response if the server has explicitly permitted that origin.

## Preflight requests

For "non-simple" requests (e.g. anything using methods like `PUT`/`DELETE`, or custom headers like `Authorization`), the browser first sends an automatic `OPTIONS` request called a **preflight**, asking the server "would you allow this actual request?" before sending the real one. The server responds with the allowed origins/methods/headers, and only if that check passes does the browser send the real request.

## Common mistakes

- Setting `Access-Control-Allow-Origin: *` (allow any origin) on an endpoint that also uses cookies/credentials — browsers block this combination for security reasons; a specific origin must be named when credentials are involved.
- Forgetting to handle the `OPTIONS` preflight request on the server, causing the browser to block the real request even though the actual endpoint would have worked fine.
- Confusing CORS errors (a browser-enforced restriction) with actual server/network errors — a CORS-blocked request usually did reach the server and get a real response; the browser just refuses to hand that response to the JavaScript that requested it.

## Key point

CORS is enforced by the **browser**, not the server. It protects users of a website, not the server itself — a non-browser client (like `curl` or a mobile app) is not restricted by CORS at all, since there's no browser origin/security-policy enforcement happening.
