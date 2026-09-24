# Reusable client architecture

Read this branch when the user asks for a reusable WebAdmin client, SDK, package,
or application integration rather than one workflow helper.

Implement the requested domains and their workflow dependencies. Use the
capability map to select references, not as a list of modules to generate.
A REST-only package for one domain can be a complete reusable client.

## Contract-first build

1. [Select a live or supplied versioned contract](endpoint-contract.md#select-the-contract)
   and [map its serialized types](endpoint-contract.md#map-contract-types) for the
   included operations. Keep generated contract types separate from handwritten
   transport and workflow code.
2. Implement the shared [HTTP request requirements](endpoint-contract.md#http-requests),
   authentication, default headers, and request IDs in one transport boundary.
3. Expose typed operations grouped by the included domains. Each domain owns
   its request/response types and any pagination or artifact behavior.
   Validate decoded responses at runtime using
   [the response contract](endpoint-contract.md#validate-responses) before
   returning typed results; generated types alone are insufficient.
4. If an included workflow uses STOMP, provide a separately configured client
   following [stomp-client.md](stomp-client.md). It owns connection state,
   subscriptions, broker errors, reconnect policy, and cleanup. REST-only
   workflows need no broker configuration or socket dependencies.
5. Check the included workflows using the [compatibility suite](#compatibility-suite)
   and the shared [verification and delivery criteria](../SKILL.md#verify-and-deliver).

## Public API shape

Group domain methods by their purpose, for example `streams.list`,
`exports.prepare`, `downloads.save`, and `imports.waitForCompletion`.

Follow the [output rules](../SKILL.md#output) for library returns and CLI presentation.

Every method declares its timeout, cancellation behavior, applicable pagination/artifact
limits, and result type. Preserve 64-bit JSON values as strings where
`X-JSON-BigInt-Encoding: string` applies. Use one shared implementation of
[safe artifact downloads](exports-and-artifacts.md#safe-artifact-downloads)
for streamed artifacts.

## Authentication and sessions

Inject credential providers using [authentication and lifecycle](authentication.md).
Keep any deployment-specific browser-session adapter separate from portable API
authentication and enable it only after verification against the target.

## State-changing methods

Separate read/artifact modules from administrative methods. Follow
[authorized state changes](writes-and-confirmation.md) for the caller's policy,
confirmation UI, retry restrictions, and live execution.

## Compatibility suite

Apply the [verification criteria](../SKILL.md#verify-and-deliver) to the public
operations. Use a disposable target for live state changes. Cover the applicable
cases below; add artifact, STOMP, and state-change checks only for workflows
that use those features:

- OpenAPI and server-version capture;
- authentication discovery and configured credential provider;
- path normalization and declared success/error handling;
- malformed successful responses, required fields, and pagination consistency;
- valid empty collections, nullable fields, and permitted empty bodies;
- multi-stage ordering and completion/failure state when diagnostic history is truncated;
- 64-bit REST and STOMP values;
- paging and artifact byte limits;
- interrupted downloads, cancellation, disk errors, and temporary-file cleanup;
- destination preservation and atomic publication, including destination conflicts;
- authorized targets and ownership limits for state changes and cleanup.

Keep deployment-specific proxy paths, broker URLs, BFF behavior, token scopes,
and download authorization in client configuration or compatibility fixtures,
not in hard-coded defaults.
