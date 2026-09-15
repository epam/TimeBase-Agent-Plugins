# Docs search

Use this path when the user needs concept, feature, configuration, or behavior documentation, or when `search_logs_kb` does not answer the real question.

## When to use it

Use docs search when:

- the user is really asking how a TimeBase concept works
- the next step depends on product behavior or configuration, not just on matching an issue signature
- the KB match is weak or empty and you need product context to continue
- TimeBase MCP is unavailable and the best next move is to point the user to the most relevant documentation

## What docs search is good for

The docs are strongest on product concepts and operational behavior, for example:

- cursors, loaders, connections, locks, and topics
- stream structure, schema, symbols, and spaces
- replication, configuration, security, and deployment behavior
- feature semantics and tradeoffs

It is not primarily an issue database. Do not treat docs search as a substitute for `search_logs_kb` when the real task is matching a known failure signature.

## Search URL shape

Use this URL form:

- `https://kb.timebase.info/docs/search?q=<search+query>`

## Query writing tips

Build the query from the concept or feature the user needs to understand.

Prefer:

- one product feature such as `loader`, `cursor`, `lock`, `replication`, or `stream spaces`
- one feature plus one specific behavior such as `cursor empty read`, `loader blocked`, or `replication lag`
- one config or deployment term when configuration is the likely issue

Use exception or class names only when they point to a clear product concept the docs are likely to explain.

Avoid:

- full log dumps
- generic words like `error`, `failed`, or `exception` by themselves
- several unrelated concepts in one query

## What to say to the user

If you did not actually open the docs, do not imply that you did.

Say something like:

- `I do not have a strong KB match here. The next useful step is docs search for <query> so we can confirm how this feature is supposed to behave.`
- `TimeBase MCP is unavailable, so I cannot use the logs KB tool. A targeted docs search for <query> is the next best step.`

## Relationship to the KB

Use docs search when the problem has shifted from "which known failure is this" to "how is this TimeBase feature supposed to work or be configured".

Use `search_logs_kb` first when the user already gave a good log excerpt and the main task is identifying a likely known issue.