# Web Servers and Reverse Proxies

A web server is software that listens for HTTP requests and serves
responses — an essential layer between the internet and your application
code.

## Popular web servers

- **Nginx**: extremely popular, known for high performance and low memory
  usage, especially good at serving static files and acting as a reverse
  proxy or load balancer.
- **Apache HTTP Server**: one of the oldest and most widely deployed,
  highly configurable via modules.
- **Caddy**: modern, notable for automatic HTTPS certificate provisioning
  out of the box.
- **Microsoft IIS**: the standard web server on Windows Server
  environments, tightly integrated with .NET applications.

## Serving static files vs application code

Web servers serve **static files** (HTML, CSS, JS, images) directly and
efficiently. For **dynamic content** (your actual application logic), the
web server typically doesn't run your code directly — instead it forwards
the request to an application server or process running your backend code
(e.g. a Python/Node.js/Java process), then returns that response to the
client. This split lets the web server handle what it's optimized for
(fast static serving, TLS termination, connection handling) while your
application focuses on business logic.

## Reverse proxies

A reverse proxy sits in front of one or more backend servers and forwards
client requests to them, then returns the response back to the client —
the client only ever talks to the proxy, never directly to the backend
servers. Nginx and Caddy are commonly deployed this way. Common reasons to
use one:

- **Load balancing**: distribute requests across multiple backend
  instances (see the Load Balancing document — a reverse proxy is often
  literally how load balancing is implemented).
- **TLS termination**: handle HTTPS encryption/decryption at the proxy,
  so backend application servers can run plain HTTP internally, simplifying
  certificate management to one place.
- **Serving static assets directly**: let the proxy handle images/CSS/JS
  without ever forwarding those requests to the application.
- **Security**: hide backend server details from the internet, and
  centralize rate limiting or request filtering at one layer (see the
  Rate Limiting document).

## Forward proxy vs reverse proxy

A **forward proxy** sits in front of clients, forwarding their requests
outward and hiding the client's identity from the destination server
(e.g. a corporate proxy, or a VPN-like service). A **reverse proxy** sits
in front of servers, hiding the servers' details from the client. They
solve related but distinct problems — forward proxies protect/represent
the client, reverse proxies protect/represent the server.

## Free resources

- [Nginx documentation](https://nginx.org/en/docs/)
- [Caddy documentation](https://caddyserver.com/docs/)
- [MDN: Proxy servers and tunneling](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Proxy_servers_and_tunneling)
