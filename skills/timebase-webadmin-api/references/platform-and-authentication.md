# Platform and authentication

Read [`authentication.md`](authentication.md) before an executable protected request and [`endpoint-contract.md`](endpoint-contract.md) when resolving contract differences.

## Operations

| Purpose | Operations | Class |
| --- | --- | --- |
| Health | `GET /ping` | read |
| Version | `GET` or `POST /api/v0/v`; duplicate `/api/v0/` | discovery |
| Authentication discovery | `GET /api/v0/authInfo` | discovery |
| Session activity | `POST /api/v0/login`, `POST /api/v0/logout` | state change |
| Write capability | `GET /api/v0/writable` | discovery |
| Request correlation | `GET /api/v0/correlationId` | discovery |
| BFF refresh | `GET /oauth/refresh` | deployment-specific session flow |

`authInfo`, version, docs, and health are public server routes; most other API routes are authenticated. `writable` needs write authority. Treat login/logout and refresh as identity/session operations, not generic REST helpers. Select client authentication and lifecycle behavior from [the authentication reference](authentication.md), which also defines the BFF browser-session boundary.

Use the inventory for exact declared media types and response codes. For local user sign-in, follow [native PKCE setup and lifecycle](authentication.md#native-browser-sign-in).
