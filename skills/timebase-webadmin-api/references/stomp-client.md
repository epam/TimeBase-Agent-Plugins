# STOMP client boundary

For a custom helper, require the deployment's STOMP/WebSocket URL and supported authentication mechanism as explicit configuration. Do not infer either from the REST host root or the browser frontend. Confirm whether the target server expects a raw access token or `Bearer <token>` in the STOMP `authorization` CONNECT header.

Model connection, subscription, broker `ERROR`, timeout, and disconnect as distinct outcomes. Follow [workflow state](client-lifecycle.md#workflow-state) when deriving operation results from events. For monitor subscriptions that can carry 64-bit JSON values, send `X-JSON-BigInt-Encoding: string` in STOMP `SUBSCRIBE` headers and retain those values as strings until parsed losslessly. Keep diagnostic history bounded.

## Connection ownership and cleanup

Apply [resource ownership and cleanup](client-lifecycle.md#resource-ownership-and-cleanup).
Each operation owns its subscriptions. On completion, failure, timeout, or
cancellation, unsubscribe those subscriptions and release their local handlers
and timers. Treat these as separate cleanup actions so a failed unsubscribe
does not retain local resources. Preserve unrelated subscriptions on the same
connection.

A standalone helper that creates a dedicated connection also closes it on every
exit path, including failed CONNECT. An operation borrowing a shared connection
leaves it open; the owning client or application controls shutdown. On a
connection-level failure, the owner closes the failed connection and notifies all
affected operations. Failure to notify or clean up one operation must not prevent
the others from being notified or the connection from being closed.
