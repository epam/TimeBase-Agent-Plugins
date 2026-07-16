# Authentication

Use this reference for OAuth2 / cloud TimeBase connections. Authentication is a separate bootstrap concern from stream access.

## Java client model

OAuth2 is configured through the concrete `TickDBClient` implementation (cast `DXTickDB` to it), not the base interface. Build an `Oauth2ClientConfig`, wrap it in an `Oauth2Client`, and set it on the client **before** calling `open(...)`.

## Client credentials flow

```java
import deltix.qsrv.hf.tickdb.comm.client.TickDBClient;
import deltix.qsrv.hf.tickdb.pub.DXTickDB;
import deltix.qsrv.hf.tickdb.pub.TickDBFactory;
import deltix.util.oauth.Oauth2Client;
import deltix.util.oauth.Oauth2ClientConfig;

DXTickDB db = TickDBFactory.createFromUrl(timebaseUrl);

Oauth2ClientConfig config = Oauth2ClientConfig.builder()
    .withUrl(oauth2TokenUrl)
    .withClientCredentials(clientId, clientSecret)
    .withParameter("scope", scope)
    .build();

((TickDBClient) db).setOauth2Client(Oauth2Client.create(config));

db.open(true);
```

## Auto-resolving the config from the server

Instead of hardcoding the token URL, `Oauth2ConfigProvider` can resolve it from the target server, given only a client secret:

```java
import deltix.qsrv.hf.tickdb.pub.oauth.Oauth2ConfigProvider;

TickDBClient client = (TickDBClient) TickDBFactory.createFromUrl(timebaseUrl);

Oauth2ClientConfig config = new Oauth2ConfigProvider()
    .withClient(client)
    .withClientSecret(clientSecret)
    .buildConfig();

client.setOauth2Client(Oauth2Client.create(config));
client.open(true);
```

## URL-embedded credentials (SSO)

For client-credentials flow with no code changes at all, embed the credential in the connection URL and use `openFromUrl`:

```java
String url = timebaseUrl + "?sso=true&secret=" + clientSecret;
DXTickDB db = TickDBFactory.openFromUrl(url, true);
```

Only use this when the secret can safely live in a URL string for the environment in question (e.g. sourced from a secret manager at runtime, never hardcoded/committed).

## Application code (browser) flow

For interactive user login (as opposed to a service's client-credentials flow), `Oauth2CodeConnectionManager` opens a browser for the user to authenticate:

```java
import deltix.qsrv.hf.tickdb.pub.oauth.Oauth2CodeConnectionManager;

TickDBClient client = (TickDBClient) TickDBFactory.createFromUrl(timebaseUrl);
Oauth2CodeConnectionManager.getInstance().login(client);

client.open(true);
// ...
client.close();
Oauth2CodeConnectionManager.getInstance().close(); // release the manager when fully done
```

## Secrets and configuration

- Never hardcode `clientSecret` or other credential material in generated code — load it from environment variables or the project's existing secret-management convention.
- Prefer the auto-resolving `Oauth2ConfigProvider` over hardcoding the OAuth2 token URL when the target server supports it.
- Do not commit secrets to source control.

## Common mistakes

- Inventing an OAuth2 API shape from memory (e.g. a `setOauth2Client(issuer, clientId, secret, scope)` signature) — always build an `Oauth2ClientConfig` and pass a single `Oauth2Client` to `setOauth2Client`.
- Assuming OAuth2 configuration is available directly on `DXTickDB` — it requires casting to `TickDBClient`.
- Calling `open(...)` before `setOauth2Client(...)`/`login(...)`.
- Embedding client secrets directly in generated source rather than reading them from environment/config.

See [`examples/oauth2.md`](examples/oauth2.md) for a fuller pattern.
