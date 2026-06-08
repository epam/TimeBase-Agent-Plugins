# QQL Concepts Index

Use this file to quickly pick which references to open for a request.

## Quick Routing by Task

### Build a SELECT query

Open:

- `references/query-generation.md`

Add when needed:

- `references/concepts/constants-and-literals.md`
- `references/concepts/time-and-filtering.md`
- `references/concepts/filters-and-predicates.md`
- `references/concepts/operators-conditionals.md`
- `references/concepts/keywords-and-shaping.md`
- `references/functions-windows.md`
- `references/concepts/subscription-hints.md` — when user mentions performance, large streams, or is filtering on `timestamp`/`symbol`.

### Repair a broken query

Open:

- `references/query-generation.md`
- `references/mcp-workflow.md`

Add the matching concept file for the failing construct:

- `references/concepts/casts.md`
- `references/concepts/arrays.md`
- `references/concepts/inner-queries.md`
- `references/concepts/time-and-filtering.md`
- `references/concepts/filters-and-predicates.md`
- `references/concepts/operators-conditionals.md`
- `references/concepts/stateless-functions.md` when the error is about an unknown or unsupported function, or when the user asks what functions the connected server supports.

### Work with polymorphic or PackageHeader data

Open:

- `references/arrays-polymorphism.md`
- `references/query-generation.md`
- `references/mcp-workflow.md`

Add when needed:

- `references/concepts/arrays.md`
- `references/concepts/casts.md`
- `references/functions-windows.md`
- `references/concepts/union.md`

### Create/alter/modify/drop schema (DDL)

Open:

- `references/ddl-generation.md`
- `references/mcp-workflow.md`

Add when needed:

- `references/concepts/data-types.md`

### Work with constants, predicates, or literals

Open:

- `references/concepts/constants-and-literals.md`
- `references/concepts/filters-and-predicates.md`

Add when needed:

- `references/concepts/data-types.md`
- `references/concepts/time-and-filtering.md`
- `references/concepts/operators-conditionals.md`

### Explain syntax or behavior

Open:

- the requested concept file from the list below,
- `references/query-generation.md` for core syntax/invariants.

If the question is specifically about available functions on the connected server, also open:

- `references/concepts/stateless-functions.md`

### Optimize or explain query performance

Open:

- `references/concepts/subscription-hints.md`
- `references/query-generation.md`

Add when needed:

- `references/concepts/time-and-filtering.md`
- `references/concepts/filters-and-predicates.md`

## Common Combined Cases

### Polymorphic analytical query

Use:

- `references/arrays-polymorphism.md`
- `references/query-generation.md`
- `references/functions-windows.md`
- `references/concepts/arrays.md`
- `references/concepts/casts.md`
- `references/concepts/union.md`

### Broken polymorphic query

Use:

- `references/query-generation.md`
- `references/mcp-workflow.md`
- `references/arrays-polymorphism.md`

## Concept File List

- `references/concepts/time-and-filtering.md`
- `references/concepts/constants-and-literals.md`
- `references/concepts/filters-and-predicates.md`
- `references/concepts/subscription-hints.md`
- `references/concepts/arrays.md`
- `references/concepts/casts.md`
- `references/concepts/operators-conditionals.md`
- `references/concepts/data-types.md`
- `references/concepts/keywords-and-shaping.md`
- `references/concepts/inner-queries.md`
- `references/concepts/stateful-functions.md`
- `references/concepts/stateless-functions.md`
- `references/concepts/union.md`
