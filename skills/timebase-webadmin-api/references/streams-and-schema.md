# Streams, schemas, and data administration

## Read surface

The family covers stream inventory and metadata: `/api/v0/streams`, `/{streamId}/describe`, `/schema`, `/{streamId}/schema`, `/{streamId}/options`, `/{streamId}/spaces`, `/{streamId}/symbols`, `/{streamId}/range`, `/datatypes`, `/currencies`, `/instruments/{id}/info`, `/settings`, and tree-structure requests.

Use `GET /api/v0/{streamId}/schema` for normal schema reads. Although
`GET /api/v0/schema?key={streamKey}` also reads schema, but its authorization
can differ from `GET /api/v0/{streamId}/schema`. Verify the target deployment's
permissions before using the key-based route as a read-only substitute.

Tree construction uses POST but is read semantics. Keep stream, symbol, and page bounds explicit. Consult the [selected contract](endpoint-contract.md#select-the-contract) for exact path variants and parameters.

## State changes

`POST /createStream`, `POST /{streamId}/changeSchema`, `PUT /{streamId}/options`, stream delete/rename/purge/truncate, space and symbol operations, writes, message updates, data deletion, periodicity changes, and background-task abort are state changes. They require `TB_ALLOW_WRITE`; many also reject a read-only TimeBase connection.

Follow [`writes-and-confirmation.md`](writes-and-confirmation.md) when preparing state-changing helpers. Legacy `GET` endpoints for deleting or renaming a space and aborting a background task are still state changes. Never prefetch, retry, cache, or follow them automatically.

## Input limits

The OpenAPI body-required flags are unreliable. When it omits a required body or serialization detail, resolve the request shape using documentation or source for the target version, then test it against a disposable target. Validate stream and symbol identifiers before execution, and use a disposable server to verify timestamp units and array serialization. For bulk writes and deletions, specify the target set and expected impact before execution.
