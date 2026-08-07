# Authentication

Use this reference for connecting to TimeBase, protected or not.

## Connection entry points

`TickDBFactory` exposes several ways to obtain a `DXTickDB`:

| Entry point | Use when |
| --- | --- |
| `TickDBFactory.createFromUrl(url)` | Default choice. URL carries scheme/host/port and optionally embedded auth query params. |
| `TickDBFactory.createFromUrl(url, user, pass)` | Same as above, with explicit basic-auth credentials instead of embedding them in the URL. |
| `TickDBFactory.connect(host, port, enableSSL)` / `connect(host, port, enableSSL, user, pass)` | Building the connection from discrete host/port/SSL fields rather than a URL string. Returns `RemoteTickDB` directly. |
| `TickDBFactory.openFromUrl(url, readOnly)` | Combines `createFromUrl` + `open` in one call. |
| `TickDBFactory.create(File... paths)` | Embedded/local DB over on-disk files, primarily for standalone tools/tests. |

```java
import deltix.qsrv.hf.tickdb.pub.DXTickDB;
import deltix.qsrv.hf.tickdb.pub.TickDBFactory;

try (DXTickDB db = TickDBFactory.createFromUrl(connectionUrl)) {
    db.open(true); // readOnly
    // use db
}
```

## Capability comparison

| Capability | Enterprise Edition | Community Edition |
| --- | --- | --- |
| Username/password | Yes | Yes |
| OAuth2 client credentials | Yes | Yes, same shape |
| OAuth2 auto-resolving config | Yes, `withClientSecret(secret).buildConfig()` | Yes, `discover(secret)` instead |
| OAuth2 URL-embedded SSO | Yes | No |
| OAuth2 browser login | Yes | No |

Note: OAuth2 is available on recent Community Edition releases (6.2+), check the target project's Community Edition version if OAuth2 support is in question.

## Username/password

```java
String user = System.getenv("TIMEBASE_USER");
String pass = System.getenv("TIMEBASE_PASSWORD");

DXTickDB db = TickDBFactory.createFromUrl(timebaseUrl, user, pass);
db.open(true);
```

Credentials can also be embedded in the URL (`dxtick://user:pass@host:port`). Never hardcode credentials, load them from environment variables or the project's existing secret convention.

## OAuth2 client credentials

Cast `DXTickDB` to `TickDBClient` and set the OAuth2 client before calling `open(...)`. Same shape on both editions, only the package root differs.

```java
import deltix.qsrv.hf.tickdb.comm.client.TickDBClient;
import deltix.qsrv.hf.tickdb.pub.DXTickDB;
import deltix.qsrv.hf.tickdb.pub.TickDBFactory;
import deltix.util.oauth.Oauth2Client;
import deltix.util.oauth.Oauth2ClientConfig;

String oauth2TokenUrl = System.getenv("OAUTH2_TOKEN_URL");
String clientId = System.getenv("OAUTH2_CLIENT_ID");
String clientSecret = System.getenv("OAUTH2_CLIENT_SECRET");

try (DXTickDB db = TickDBFactory.createFromUrl(timebaseUrl)) {
    Oauth2ClientConfig config = Oauth2ClientConfig.builder()
        .withUrl(oauth2TokenUrl)
        .withClientCredentials(clientId, clientSecret)
        .build();

    ((TickDBClient) db).setOauth2Client(Oauth2Client.create(config));
    db.open(true);
}
```

## OAuth2 auto-resolving config

`Oauth2ConfigProvider` resolves the token URL from the server instead of hardcoding it. The method chain differs by edition.

Enterprise Edition:

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

Community Edition, one call instead of two:

```java
import com.epam.deltix.util.oauth.Oauth2ConfigProvider;

TickDBClient client = (TickDBClient) TickDBFactory.createFromUrl(timebaseUrl);
Oauth2ClientConfig config = new Oauth2ConfigProvider()
    .withClient(client)
    .discover(clientSecret);

client.setOauth2Client(Oauth2Client.create(config));
client.open(true);
```

## URL-embedded SSO (Enterprise Edition only)

```java
String url = timebaseUrl + "?sso=true&secret=" + clientSecret;
DXTickDB db = TickDBFactory.openFromUrl(url, true);
```

Only use this when the secret can safely live in a URL string.

## Browser login (Enterprise Edition only)

`Oauth2CodeConnectionManager` opens a browser for interactive user login. This is an OAuth2 authorization-code grant, so it needs a browser on the same machine, don't use it in a headless or server-side app.

```java
import deltix.qsrv.hf.tickdb.pub.oauth.Oauth2CodeConnectionManager;

TickDBClient client = (TickDBClient) TickDBFactory.createFromUrl(timebaseUrl);
Oauth2CodeConnectionManager.getInstance().login(client);
client.open(true);
// ...
client.close();
Oauth2CodeConnectionManager.getInstance().close();
```

## Common mistakes

- Assuming OAuth2 is available directly on `DXTickDB`. It requires casting to `TickDBClient`.
- Calling `open(...)` before `setOauth2Client(...)`/`login(...)`.
- Hardcoding credentials instead of reading them from protected sources.
