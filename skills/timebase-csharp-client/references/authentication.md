# Authentication

Use this reference for OAuth2 / cloud TimeBase connections. Authentication is a separate bootstrap concern from stream access.

## .NET client model

The .NET TimeBase client does not acquire OAuth2 tokens internally like some other language clients. Acquire a token with MSAL or another IdP client, then apply both the account username and bearer token to the TimeBase connection.

## Minimum viable OAuth checklist

1. Fetch and inspect `/tb/oauthinfo` from the target TimeBase server.
2. Resolve `issuer`, `clientid`, and `scope` from the live payload instead of inventing them.
3. Acquire a bearer token with the appropriate IdP client for that issuer. MSAL is one option, not a requirement.
4. Capture both the access token and the account username associated with the authenticated principal.
5. Apply the username in `TickDbFactory.CreateFromUrl(..., username, ...)` and set `db.AccessToken` to the bearer token.
6. Validate the connection with `db.Open(...)`.

## Client credentials flow

```csharp
using Deltix.Timebase.Api;
using Deltix.Timebase.Client;
using Microsoft.Identity.Client;

var app = ConfidentialClientApplicationBuilder
    .Create(clientId)
    .WithClientSecret(clientSecret)
    .WithAuthority(authority)
    .Build();

var authResult = await app
    .AcquireTokenForClient(scopes)
    .ExecuteAsync(cancellationToken);

ITickDb? db = null;
try
{
    db = TickDbFactory.CreateFromUrl(timebaseUrl, username, null)
        ?? throw new InvalidOperationException("TickDbFactory returned null");

    db.AccessToken = authResult.AccessToken;
    db.Open(readOnly: true);

    var streams = db.ListStreams();
    Console.WriteLine($"Connected. Found {streams.Length} streams.");
}
finally
{
    db?.Dispose();
}
```

## Secrets and configuration

- Load `issuer`, `clientId`, `scope`, username, and any client secret or credential material from live `/tb/oauthinfo` plus secure local configuration. Never hardcode production secrets.
- Suggested configuration inputs include `TIMEBASE_URL`, OAuth issuer/authority, client ID, scope, username, and any IdP-specific secret material.
- Do not commit secrets to source control.

## Long-lived services

The client does not refresh tokens automatically. For daemons and background workers:

1. Track token expiry from MSAL `ExpiresOn`.
2. Refresh before expiry with a safety buffer (for example 5 minutes).
3. Update `db.AccessToken` with the new token.

See `examples/oauth2.md` for a fuller pattern.

## Common mistakes

- Skipping `/tb/oauthinfo` discovery and guessing issuer, client ID, or scope.
- Expecting built-in OAuth2 support in the .NET client without an external IdP client.
- Passing only a bearer token without the corresponding username.
- Embedding client secrets in generated code.
- Opening the connection before setting `AccessToken`.
