# API-key authentication

Select this branch only when the deployment explicitly provides its API-key mode and configuration. `authInfo.provider_type` describes OAuth and does not establish API-key availability. 
Choose [basic signed requests](#basic-signed-requests) or [session keys](#session-api-keys), apply the shared [endpoint and token trust rules](authentication.md#endpoint-and-token-trust), and follow the
[verification scope](#verification-scope) for the requested setup or audit.

## Basic signed requests

### Setup and signing

Take the key name and API secret from the caller's private credential source.
Use this pair only for basic signed requests, not for session login.

Basic signed requests use `X-Deltix-ApiKey` and `X-Deltix-Signature`. The signature is Base64-encoded HMAC-SHA384 over the canonical request payload, using the API secret.

Confirm canonicalization against the target server before implementing a signer. Check method and path normalization, sorting of decoded query parameters and repeated values, and which request bodies enter the signature. Signing raw URL-encoded query text can disagree with a server that signs decoded parameters. Preserve the exact transmitted body and test repeated keys, empty values, case, Unicode, spaces, and percent encoding.

If the server sorts Java strings, match its UTF-16 ordering for parameter names
and repeated values; another language's default Unicode ordering can differ.
Verify canonical bytes and signatures against independently derived vectors,
including BMP and supplementary characters. Expected signatures must not come
from the signer under test.

Never log the key secret, signature, or canonical payload when it contains private data.

### Key lifecycle and rejection

Sign each request with the configured secret; basic mode has no negotiated
session to renew. After credential rotation, reload the client's configuration
and reconnect affected STOMP connections with the new secret.

Distinguish rejected signatures or unknown keys from insufficient permissions using the target server's error contract. Basic requests have no session nonce; replay protection and expiry require separate server policy or session mode.

### Basic-key STOMP

Send these native STOMP CONNECT headers: `X-Deltix-ApiKey`, `X-Deltix-Payload`, and `X-Deltix-Signature`. Use a fresh random payload string and calculate the signature as Base64 of HMAC-SHA384 over the UTF-8 string:

```text
CONNECTX-Deltix-Payload=<payload>&X-Deltix-ApiKey=<key-name>
```

Concatenate exactly as shown, without additional spaces. Use the API secret as the HMAC key. Read `CONNECTED` or `ERROR` before subscribing; the connection owner closes the socket if CONNECT fails or times out. Follow [connection ownership and cleanup](stomp-client.md#connection-ownership-and-cleanup) for subsequent operations. Omit the OAuth `authorization` header when selecting API-key authentication.

A random payload does not establish server-side replay protection. Verify CONNECT replay handling and authorization for each subscription separately.

## Session API keys

### Inputs and login root

Take the key name, matching RSA private key, and configured session login root
from the deployment. Keep the private key in a protected file or key store.
The session exchange needs the private key, not the basic API secret.

Use the deployment's configured session login root for its `attempt` and `confirm` routes. Do not infer the root from an example path; it can differ between deployments.

### Establish and use a session

The session flow signs a server challenge with the client's RSA private key, exchanges Diffie-Hellman public values, and signs subsequent requests using the derived session secret. Reuse a compatible client implementation instead of inventing a cryptographic protocol. Match the server's integer serialization and signature encoding.

Include `X-Deltix-Session-Id`, `X-Deltix-Nonce`, and `X-Deltix-Signature` on session requests. Serialize each session's complete request through response receipt so nonce order matches arrival order. Share that order with STOMP CONNECT requests using the session. Keep secret values and private-key contents out of logs.

### Session lifecycle and rejection

Use the advertised idle interval and the deployment's expiry rules to decide
when to reacquire a session. Renew or keep alive only through a verified server
operation. HTTP 400 or 401 can mean an invalid session or signature; return
the failed request's error and reacquire before the next request after
confirming the server's response contract. HTTP 403 reports permission denial
without discarding a valid session.

Use signed POST requests to `{login-root}/keepalive` and `{login-root}/logout` when the target contract supports those lifecycle actions. Server cleanup can lag the advertised idle deadline. Report failed confirmations without echoing their response bodies.

### Session-key STOMP

For STOMP CONNECT, sign `CONNECTX-Deltix-Nonce=<nonce>&X-Deltix-Session-Id=<session-id>` using Base64-encoded HMAC-SHA384 with the session secret. Send those two headers plus `X-Deltix-Signature`. Share the nonce sequence across REST and new STOMP connections that use the same session. Subscription authorization remains separate from CONNECT authentication.

## Verification scope

For routine setup, configure the supplied credentials and verify one bounded
protected read through the intended client. This completes setup
for that identity and operation; it does not establish other permissions or
deployment-wide security properties. If STOMP is part of the requested workflow,
also verify CONNECT and the intended subscription with bounded waiting and cleanup.

When implementing a signer or session client, add local checks for canonicalization,
tampering, nonce ordering, and failure handling as applicable. Controlled responses
can test client behavior but do not prove server enforcement. Code-only requests
can finish with these checks and an explicit statement that live compatibility
remains unverified.

For a requested deployment audit, test the applicable mechanisms with dedicated
test identities and sessions:

- Basic keys: invalid signatures, altered requests, explicit key authorities
  versus inherited user permissions, and old/new credentials after rotation.
- Session keys: replay rejection, concurrent nonce ordering, expiry and
  reacquisition, keepalive, and rejection of an old session after logout.
- STOMP, when included: CONNECT authentication, subscription permissions, and
  reconnection after rotation.

Report each audit check as passed, failed, or blocked with sanitized evidence.
Additional identities, server reconfiguration, rotation, and lifecycle probes
are audit requirements only when in scope, not prerequisites for routine setup.
