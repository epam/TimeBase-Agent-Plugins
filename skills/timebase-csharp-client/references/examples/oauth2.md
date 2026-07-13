# OAuth2 Connection

**Type:** fragment

**When to use:** Connect to OAuth2-protected TimeBase.

```csharp
using Deltix.Timebase.Api;
using Deltix.Timebase.Client;
using Microsoft.Identity.Client; // IdP may differ

// Uses client secret auth, other ways to retrieve the token may be used
var authority = Environment.GetEnvironmentVariable("OAUTH2_AUTHORITY")
    ?? throw new InvalidOperationException("OAUTH2_AUTHORITY required");
var clientId = Environment.GetEnvironmentVariable("OAUTH2_CLIENT_ID")
    ?? throw new InvalidOperationException("OAUTH2_CLIENT_ID required");
var clientSecret = Environment.GetEnvironmentVariable("OAUTH2_CLIENT_SECRET")
    ?? throw new InvalidOperationException("OAUTH2_CLIENT_SECRET required");
var scopes = (Environment.GetEnvironmentVariable("OAUTH2_SCOPES") ?? "")
    .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

var app = ConfidentialClientApplicationBuilder
    .Create(clientId).WithClientSecret(clientSecret).WithAuthority(authority).Build();
var token = await app.AcquireTokenForClient(scopes).ExecuteAsync();

ITickDb? db = null;
try
{
    // Username depends on TB server configuration. May be a client id, retrieved from the token or provided by the user
    db = TickDbFactory.CreateFromUrl(timebaseUrl, username, null)
        ?? throw new InvalidOperationException("TickDbFactory returned null.");
    db.AccessToken = token.AccessToken;
    db.Open(readOnly: true);
}
finally
{
    db?.Dispose();
}
```
