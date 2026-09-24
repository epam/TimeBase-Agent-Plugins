# Endpoint contract

## Select the contract

For live work, fetch `{hostRoot}/api/v0/docs/rest/ui/openapi.json` and record the
server version from `/api/v0/v`. For code generation without a reachable server,
use a supplied or previously captured OpenAPI document with its recorded server
version. Record the contract's source and version; an OpenAPI placeholder version
alone does not identify a compatible build.

Generate and test against that contract's paths, methods, parameters, and media
types. Use [contract mappings](#map-contract-types) for client models. Keep discovery
and authentication in the client's runtime path; offline generation needs no live
credentials or login. Compare the contract and version with the target before
live execution. Report compatibility evidence through the
[verification and delivery criteria](../SKILL.md#verify-and-deliver).

## Resolve contract differences

1. If an operation, request detail, or response schema is missing or incomplete, consult documentation or source for the recorded server version. If the required contract remains unresolved, identify the affected operation as blocked and continue independent work. Do not invent missing fields or claim a complete client for a blocked workflow.
2. Store each correction with the affected operation, server version, and supporting evidence. A source-backed correction can be implemented and tested locally; mark live confirmation pending until a bounded request against a disposable target verifies it.

## Map contract types

Preserve serialized field names, types, required fields, and nullability from the
selected contract. Language-specific member names may differ only through an
explicit serialization mapping. Apply the same rule to nested records and request
bodies; a valid top-level object does not establish a valid model.

Requiredness, nullability, and type are separate constraints. An optional field
may be absent; when present, validate its type and accept null only when allowed.
Examples do not make fields required. Match JSON types even when the implementation
language treats booleans as numbers.

Check mappings with representative populated payloads from the contract or
independent version-matched evidence, valid empty values, and omitted optional
fields. Also check rejection of invalid field types and missing required fields
where the selected contract defines them, including nested records. Derive
expected payloads from the contract rather than the client model being tested.
Resolve missing or contradictory definitions through
[contract differences](#resolve-contract-differences).

## HTTP requests

Apply these requirements to discovery, authentication, protected operations, and
downloads. Reusable clients implement them in shared transport.

- Resolve the target against the configured base URL or explicitly trusted authentication endpoint before attaching credentials. Use HTTPS for credentials except on explicitly configured local development connections. See [authentication](authentication.md) for mechanism-specific destination rules.
- Disable automatic redirects. A workflow that requires a redirect must verify the destination, operation, and credential scope before issuing another request; never forward credentials to an untrusted origin.
- Accept the operation's declared success statuses or an operation-specific correction verified against the target server and response shape. A matching response body alone does not authorize arbitrary 2xx statuses. A partial response does not establish a complete result; handle it only through a verified workflow that checks the required ranges and completeness.
- Bound network waits and enforce a total deadline for the response. Honor cancellation during waits and reads. Count bytes while reading, before buffering or decoding the full body, even without `Content-Length`. Bound decompressed data when decoding expands it, and bound error bodies too. Item and page limits constrain traversal and retained results; they do not replace byte limits.
- Close responses on every exit path. Apply [resource ownership and cleanup](client-lifecycle.md#resource-ownership-and-cleanup) when releasing request resources or cancelling work.

For a newly built reusable authenticated HTTP transport, exercise a redirect to
an untrusted second local test origin with synthetic credentials. Verify that
origin receives no authentication headers and the client reports the redirect
as rejected. Exercise the transport's actual HTTP stack so its default redirect
behavior is covered.

## Validate responses

A declared success status is only the first check. Validate responses at the client boundary before returning typed results or using them in subsequent workflow steps:

- Check the expected media type and complete transfer within the [HTTP bounds](#http-requests). Validate response framing and declared length when available. Malformed JSON, invalid streaming frames, and interrupted responses are failures even with HTTP 200.
- Validate the top-level shape, required fields, field types, and nullability against the verified operation contract. Validate nested records that the workflow consumes. Static type declarations or casts alone do not validate network data. Accept additional fields unless the contract forbids them.
- Preserve valid empty collections, zero counts, false booleans, and nullable fields. Accept an empty body when the operation permits one. Never replace missing or malformed required values with successful defaults such as `[]`, `{}`, `0`, or `false`.
- Validate identifiers before using them in follow-up requests. For paged results, validate pagination metadata and require progress while more results remain. Report incomplete results if traversal stalls or a limit leaves results unread or discarded. Reaching a limit exactly on a fully retained final page is successful exhaustion.
- Check any operation-level failure or completion fields defined by the contract. A body reporting failed work is not a successful workflow merely because the HTTP request succeeded. Report a bounded, redacted validation error and stop dependent steps on failure.

## Request and response caveats

- Body-required flags can omit required fields. Validate the complete request shape before execution.
- Confirm whether array query parameters use repeated keys or comma-separated values.
- Check streaming response framing for selection, queries, and charts. Bound rows and bytes.
- Prefer `/api/v0/v` for version discovery; the `/api/v0/` alias can have different access requirements.
- Space deletion, space renaming, and background-task abort can use `GET`. Handle them as state changes.
- Confirm timestamp units and precision for each request field.
- Declared success statuses can disagree with a deployed server. Resolve each affected operation separately before accepting an undeclared status.
- If `CreateTopicRequest` omits fields required by the server, obtain the complete request shape before creating a topic.
