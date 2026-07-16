# OAuth2 Connection

**Type:** fragment

**When to use:** Connect to OAuth2-protected TimeBase via the client-credentials flow.

```java
import deltix.qsrv.hf.tickdb.comm.client.TickDBClient;
import deltix.qsrv.hf.tickdb.pub.DXTickDB;
import deltix.qsrv.hf.tickdb.pub.TickDBFactory;
import deltix.util.oauth.Oauth2Client;
import deltix.util.oauth.Oauth2ClientConfig;

String oauth2TokenUrl = System.getenv("OAUTH2_TOKEN_URL");
String clientId = System.getenv("OAUTH2_CLIENT_ID");
String clientSecret = System.getenv("OAUTH2_CLIENT_SECRET");
String scope = System.getenv("OAUTH2_SCOPE");

if (oauth2TokenUrl == null || clientId == null || clientSecret == null) {
    throw new IllegalStateException("OAUTH2_TOKEN_URL, OAUTH2_CLIENT_ID, OAUTH2_CLIENT_SECRET are required");
}

try (DXTickDB db = TickDBFactory.createFromUrl(timebaseUrl)) {
    Oauth2ClientConfig.Builder configBuilder = Oauth2ClientConfig.builder()
        .withUrl(oauth2TokenUrl)
        .withClientCredentials(clientId, clientSecret);
    if (scope != null) {
        configBuilder.withParameter("scope", scope);
    }

    ((TickDBClient) db).setOauth2Client(Oauth2Client.create(configBuilder.build()));

    db.open(true); // readOnly
    // use db
}
```

Never hardcode `clientSecret` or other credential material; load it from environment variables or your organization's secret manager. See `authentication.md` for the auto-resolving-config, URL-embedded, and browser-login variants.
