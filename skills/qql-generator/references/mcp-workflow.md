# TimeBase MCP Workflow Reference

Use this file for MCP-grounded generation and validation policy.

## When to Use

- Any schema-dependent query generation or repair.
- Any request requiring stream discovery, symbols, time range, or sample message shape.
- Any situation where parser diagnostics are needed.

## Preferred Grounding Flow

1. Probe server context (`get_server_configuration`) when useful.
2. Discover streams (`list_streams`).
3. Ground schema (`get_stream_schema`).
4. For polymorphic use-cases, inspect payload examples (`get_stream_messages`).
5. Add symbols/time range tools only when request depends on them:
   - `get_stream_symbols`
   - `get_stream_time_range`
6. Draft QQL.
7. Run `compile_query`.
8. Reconcile parser success with schema-level checks.

## `compile_query` Limits

`compile_query` returns parser-level diagnostics only:

- syntax/parse validation only,
- no semantic/logical guarantee,
- undefined classes/fields may still compile,
- `error_token` can be downstream of root cause.

Never claim semantic correctness from `compile_query` success alone.

## `execute_query` Safety

`execute_query` is non-default and potentially mutating (including DDL effects).

Use only when explicitly needed/requested:

- user asks to run or preview execution,
- runtime behavior must be validated beyond parser checks,
- query is confidently read-only and execution intent is clear.

Do not use it as compile substitute.

## Fallback Behavior (MCP Unavailable)

If MCP is absent/unreachable:

- continue using static references + user-provided schema only,
- ask for missing stream schema/class/message samples,
- provide assumption-labeled templates for schema-dependent queries.
- always include this warning in user-facing output:
  `Warning: TimeBase MCP is not available, so results are expected to be significantly worse than MCP-grounded output.`

## Example Validation Loop

```text
Goal: "top-of-book bid/ask for BTC/USDT from a PackageHeader stream"

1) list_streams -> locate candidate stream
2) get_stream_schema(stream) -> confirm packageType/entries
3) get_stream_messages(stream, count=3) -> confirm entry classes/fields
4) draft query
5) compile_query(query) -> repair parser errors
6) re-check class/field references against schema evidence
7) return QQL + assumptions + parser/semantic status
```

## Also Requires

- `references/concepts/index.md` for intent-triggered required-module policy.
- `references/query-generation.md` for canonical repair table and clause-order rules.
- `references/arrays-polymorphism.md` for PackageHeader workflows.
