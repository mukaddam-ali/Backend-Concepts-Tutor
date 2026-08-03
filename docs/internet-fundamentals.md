# Internet Fundamentals: HTTP, DNS, and Hosting

Before building backends, it helps to know what actually happens when a
browser loads a web page — the layer every API call and server response
sits on top of.

## How a request travels

1. A user types a domain name (`example.com`) into their browser.
2. **DNS (Domain Name System)** translates that human-readable domain into
   an IP address (e.g. `93.184.216.34`) — the actual address of a server on
   the internet. DNS works like a distributed phone book, resolved through a
   chain of DNS servers (root → TLD → authoritative).
3. The browser opens a connection to that IP address and sends an **HTTP
   request**.
4. The server (wherever it's **hosted** — a physical or virtual machine
   somewhere) processes the request and sends back an **HTTP response**.
5. The browser renders the response.

## What is HTTP?

HTTP (HyperText Transfer Protocol) is the request-response protocol that
defines how clients and servers communicate on the web: a client sends a
request with a method (`GET`, `POST`, etc.), headers, and optionally a body;
the server replies with a status code, headers, and a body. Nearly
everything in backend web development — REST APIs, browsers loading pages,
mobile apps calling servers — runs over HTTP.

## What is a domain name?

A domain name (`example.com`) is a human-readable label for a server,
registered through a domain registrar and pointed at a specific IP address
via DNS records (most commonly an **A record** for IPv4 or a **CNAME**
pointing to another domain).

## What is hosting?

Hosting is renting or provisioning a server (physical or virtual) that runs
your application and is reachable over the internet. Options range from a
single virtual machine (e.g. a cloud VM), to managed platform-as-a-service
hosting (e.g. Heroku-style platforms), to serverless functions, to
container orchestration platforms like Kubernetes.

## How browsers work, briefly

A browser is itself a complex client: it parses HTML/CSS/JavaScript,
constructs a page layout, and — relevant to backend work — is the most
common HTTP client making requests to your API. Understanding that the
browser enforces things like the Same-Origin Policy (see the CORS document)
matters directly for backend API design.

## Free resources

- [MDN: How does the Internet work?](https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/How_does_the_Internet_work) — Mozilla's free, official explainer.
- [MDN: An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [roadmap.sh/backend](https://roadmap.sh/backend) — free interactive roadmap this knowledge base topic list is based on.
