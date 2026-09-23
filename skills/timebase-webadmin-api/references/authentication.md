# Authentication for custom clients

Before a protected request, read `GET {hostRoot}/api/v0/authInfo` and the deployment's API access contract. Public health and version routes need no token. `provider_type` identifies the server's OAuth provider, but does not establish its grants, token audience, client registration, or client-authentication method. API keys are configured separately and may coexist with any OAuth provider.

| Available mechanism | Client inputs and path |
| --- | --- |
| `BUILT_IN_OAUTH` password grant | WebAdmin root, username, and password; stock client credentials and scope or deployment overrides. Follow [built-in password](#built-in-password). |
| Basic API key | Key name and secret. Follow [signed requests](api-keys.md#basic-signed-requests). |
| Session API key | Key name and RSA private key. Follow [session keys](api-keys.md#session-api-keys). |
| `SSO`, `SSO_BFF`, or `EXTERNAL_OAUTH` | Use [native PKCE](#native-browser-sign-in), [client credentials](#client-credentials), or an [externally managed token](#externally-managed-bearer-tokens) only when the deployment supports that grant and accepts its API bearer token. |

## Endpoint and token trust

Take the API root from the caller's explicit configuration. Trust an OAuth issuer, token endpoint, and client registration only after matching them to the deployment contract. If using issuer metadata, require the expected issuer and validate the authorization and token endpoint URLs before sending credentials or codes. Do not infer that a missing `config_url` forbids OAuth, or that a present URL authorizes every grant. Resolve conflicts between discovery and explicit configuration before login. Use HTTPS for remote credentialed endpoints; allow HTTP only for an explicitly configured loopback development endpoint. Disable automatic cross-origin redirects for credentialed requests.

Use an access token whose audience, issuer, expiry, and roles or scopes WebAdmin accepts. An ID token or Microsoft Graph token is not an API token. For OAuth token acquisition and refresh, require a string `token_type` equal to `Bearer` without regard to case before attaching the access token to an API request. Reject a missing or unsupported type instead of assuming Bearer. Externally managed bearer tokens follow their caller's verified token contract. Verify a bounded protected read before claiming API compatibility. Keep tokens, passwords, client secrets, cookies, and authorization headers out of source, command arguments, logs, and results.

Treat the entire response body from token acquisition or refresh as secret-bearing, including error responses and malformed successes. An identity provider can echo submitted credentials or tokens. Report a failed exchange with its HTTP status when available and a fixed, safe error category; do not copy response text or parsed server messages into exceptions, logs, or CLI diagnostics. In a local check, inject a synthetic secret into a failed token response and confirm it is absent from the exception and all captured output.

## Built-in password

Use this grant only when `authInfo.provider_type` is `BUILT_IN_OAUTH` and the deployment enables it.

The stock built-in client uses ID `web`, secret `secret`, and scope `trust`. Use deployment overrides when configured. `authInfo.scopes` may list OIDC scopes such as `openid` and `profile`; it does not establish the password grant's scope. Do not substitute those values for `trust` without checking the deployment's token contract.

1. Resolve `token_endpoint` from `authInfo`, using `oauth_server` as its base when supplied and otherwise the configured WebAdmin root. A typical endpoint is `/oauth/token`, outside `/api/v0`. Require the resolved URL to stay on the configured WebAdmin origin. Reject redirects before sending credentials.
2. POST `application/x-www-form-urlencoded` with `grant_type=password`, `username`, `password`, and the selected scope. Send OAuth client credentials in `Authorization: Basic <base64(client_id:client_secret)>`. The client credentials are distinct from the user's password.
3. Require HTTP 200 and a bounded JSON object with a non-empty `access_token` and the [supported token type](#endpoint-and-token-trust). If present, `expires_in` must be a finite positive number, not a boolean or numeric string. Send `Authorization: Bearer <access_token>` on protected requests.

Reuse the token until its verified renewal deadline. Derive that deadline from `expires_in` using a monotonic clock and a bounded margin. If lifetime is absent, reacquire before the next request unless the deployment supplies another verified policy. Test repeated reads, expiry, invalid credentials, and malformed token responses with controlled HTTP responses.

## Native browser sign-in

For a supported delegated API grant, register a native public client with a loopback redirect. Use the system browser and authorization code with S256 PKCE. Verify state on the callback, exchange the code at the trusted token endpoint, and use the resulting API access token after checking its token type. The user completes sign-in and MFA; a client need not extract tokens from browser storage. Use a maintained OAuth/OIDC library. Handle denial, state mismatch, callback timeout, refresh-token expiry, and listener cleanup. Store tokens in memory or an existing secure credential store.

For Entra, choose either one registration for WebAdmin's frontend and API or separate frontend and API registrations. The registration representing the API owns the delegated scope and `TB_ALLOW_READ`/`TB_ALLOW_WRITE` roles; assign users or groups on its enterprise application. The native client's registration owns the loopback redirect and requests permission to that API scope. It may be a third registration; the API owner can preauthorize it. Use the native registration's client ID as the OAuth `client_id` and the API registration's identifier in the requested scope and token audience. In the combined layout, that API identifier belongs to the shared frontend/API registration. A native public client has no client secret.

The provider enum does not promise PKCE, refresh tokens, or API bearer acceptance. Verify the issuer metadata, redirect registration, scope and consent, token audience, and a protected API read for the target deployment. Refresh near expiry when supported; otherwise repeat browser sign-in when a token is needed. Keep browser-session behavior separate from API-token renewal.

### BFF browser sessions

`SSO_BFF` may authenticate a frontend through a browser cookie. Its login, session refresh, and logout belong to that browser session. They do not prove that a standalone REST or STOMP client can use cookies or a bearer token. A portable client needs a separately verified API bearer path, such as native PKCE, an approved service grant, or an externally supplied token. If the deployment provides only a browser-session path, report that limit instead of extracting cookies or claiming headless access.

## Unattended clients

### Client credentials

Use this grant only for an approved service identity and a deployment that accepts its access token. Obtain the trusted HTTPS token URL, client ID, client authentication method and secret or key, scope or audience, and API roles from the IdP and WebAdmin configuration. POST `grant_type=client_credentials` with the required scope or audience, using the IdP's registered client-authentication method. Do not assume `client_secret_post` or any other method from `provider_type`. Require HTTP 200 and a bounded, valid access-token response with the [supported token type](#endpoint-and-token-trust) before a protected read. Entra service identities need API application roles and consent; delegated user permissions do not suffice. Reacquire on expiry or rejected renewal without opening a browser.

### Externally managed bearer tokens

Accept an API access token from the caller's token provider or a private, atomically replaced file when another component owns acquisition and rotation. The client reads the current token when needed and never attempts to mint or refresh it. Bound token size, reject empty or malformed input, and avoid caching a file token past the manager's replacement policy. A protected read verifies that the supplied token is accepted; recovery from rejection requires the manager to provide a usable token.

## Token lifecycle and rejection

Keep token state separate for each API root, identity, audience, and acquisition configuration. Coordinate concurrent acquisition or refresh so simultaneous requests do not trigger repeated browser logins or grants. A response using an old token must not clear a newer token or a replacement credential provider. On HTTP 401, invalidate only the token and provider used by that failed request if they are still current; return that request's error and let the next call acquire or load a usable token. HTTP 403 reports insufficient permission and must not discard the credential. Do not silently retry a state-changing operation after authentication failure.

Apply the shared [HTTP request requirements](endpoint-contract.md#http-requests) to acquisition and API calls. For STOMP, follow [stomp-client.md](stomp-client.md) and verify the deployment's CONNECT authentication separately from REST. API-key rejection behavior is in [api-keys.md](api-keys.md).
