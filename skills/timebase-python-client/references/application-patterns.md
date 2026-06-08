# Application Patterns

Use this reference when the user is not asking for a one-off script, but for a reusable app, service, worker, or component.

## Default structure

Split responsibilities instead of emitting one monolithic file:

1. configuration and bootstrap
2. TimeBase client creation and lifecycle
3. stream or query access layer
4. transformation or analysis layer
5. delivery layer such as CLI, API, background worker, or visualization

## TimeBase-specific guidance

- Keep stream names, symbols, and schemas out of business logic when they can be configured.
- Isolate edition-dependent behavior near bootstrap or dependency wiring.
- If MCP was used for discovery, treat that as development-time grounding, not as proof that runtime code can skip validation.
- Reuse bundled examples as low-level building blocks, not as the full app shape.

## Good defaults

- Use a small settings object or config module for URLs, stream keys, symbols, and time bounds.
- Wrap `TickDb` creation in one place so connection policy is consistent.
- Keep analysis code independent from transport code when possible.
- If the user wants a single file, still separate the logic into functions.

## When to mention edition

Only surface CE vs EE explicitly when:

- the user asked,
- the environment shows a package or protocol mismatch,
- the requested feature is clearly gated,
- installation guidance depends on it.

Otherwise, keep the answer focused on the application design itself.