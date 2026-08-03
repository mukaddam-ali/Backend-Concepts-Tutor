# WebSockets & Real-Time Communication

Regular HTTP is a request-response protocol: the client asks, the server answers, and the connection typically closes. That model breaks down for features that need the server to push data to the client the instant something happens — chat messages, live notifications, multiplayer game state, stock tickers.

## The problem with plain HTTP for real-time

Before WebSockets, developers worked around HTTP's request-response limitation with:

- **Polling**: the client repeatedly asks "anything new?" every few seconds. Simple, but wasteful — most requests return nothing new, and there's always a delay up to the polling interval.
- **Long polling**: the client makes a request, and the server holds it open until there's actually new data to send, then responds. Reduces wasted requests but still has connection-management overhead, since a new request must be made after every response.

## WebSockets

A WebSocket is a persistent, full-duplex (two-way) connection between client and server. After an initial HTTP "handshake" upgrades the connection, both sides can send messages to each other at any time, with no need to open a new connection per message.

- **Full-duplex**: unlike HTTP, either side can send data at any time without waiting for a request.
- **Low overhead per message**: no need to repeat HTTP headers on every message once the connection is established.
- **Stateful connection**: the server keeps the connection open and tracks which clients are connected — a shift from the typical stateless REST model.

## When to use WebSockets vs REST

- Use **REST** for typical CRUD operations where the client initiates every interaction (fetch a user, submit a form).
- Use **WebSockets** when the server needs to push updates to the client without the client asking first (chat apps, live dashboards, collaborative editing, multiplayer games).

## Server-Sent Events (SSE) as a lighter alternative

If you only need one-way updates (server → client, not client → server), **Server-Sent Events** are a simpler alternative to WebSockets: a single long-lived HTTP connection where the server streams events to the client. Easier to implement than WebSockets, but only supports server-to-client push.

## Scaling considerations

Because WebSocket connections are stateful and long-lived, they don't fit the usual stateless-server-behind-a-load-balancer model as cleanly. Scaling a WebSocket service across multiple servers typically requires a way for those servers to share connection state or broadcast messages to each other (e.g. via a message queue or Redis pub/sub), so a message sent by a client connected to server A can reach another client connected to server B.
