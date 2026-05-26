---
name: qql-generator
description: Use when generating, reviewing, repairing, or explaining TimeBase QQL for diverse user goals.
---

# QQL Generator

## Mission

Generate QQL that is task-correct, schema-grounded, and safe to execute. Start from user intent, compose only the needed concept modules, and never treat parser success as semantic correctness.

## How to Route Requests

1. Identify the request type:
   - build a new query,
   - repair a broken query,
   - create/alter/modify/drop schema,
   - explain QQL behavior.
2. Detect data shape needs:
   - polymorphic/PackageHeader/array payloads,
   - simple fixed-schema tabular projections.
3. Open the smallest set of relevant references:
   - start with one main workflow file,
   - add concept references only when needed,
   - use recipes only as compact starters.

## Mandatory Policy

- Ground schema-dependent QQL from MCP schema/message evidence when available.
- If MCP is unavailable or unreachable, include this exact warning in user-facing output:
  `Warning: TimeBase MCP is not available, results are expected to be significantly worse than MCP-grounded output.`
- `compile_query` is parser-only (syntax/parse diagnostics). Compile success does **not** prove class/field/type or other semantic correctness.
- `execute_query` is non-default and potentially mutating. Use it only when explicitly needed/requested by the user.
- Never invent final schema facts (classes, fields, enum values, entry types). Ask for schema or clearly mark assumptions.

## Style and Safety Rules

- Quote stream/class/field identifiers with double quotes.
- Use single quotes for string literals.
- Use `==` for equality and `===` for strict equality.
- Stateful functions use braces (`avg{}(...)`); stateless functions do not (`abs(...)`).
- Keep clause order valid (`WITH`, `SELECT`, `FROM`, `ARRAY JOIN`, `OVER`, `WHERE`, `GROUP BY`, `HAVING`, `LIMIT`, `UNION`).
- `OVER TIME(...)` / `OVER COUNT(...)` must appear before `WHERE`.
- Do not use SQL-only constructs (`ORDER BY`, SQL JOIN, SQL window `OVER (PARTITION BY ...)`, `CREATE TABLE`).
- Do not declare built-in identity fields (`timestamp`, `symbol`, `type`) in DDL.
- Never output schema-dependent queries when schema is unknown.
- Distinguish parser validity from semantic validity in notes.
- Keep destructive DDL and confirm modes explicit and user-intent driven.

## Pre-Output Safety Gates

Before finalizing any answer, verify all applicable gates:

1. Relevant references are loaded for the detected task.
2. Schema/source grounding is confirmed (MCP evidence or explicit assumptions).
3. Query shape follows the style and safety rules above.
4. If `compile_query` is available, parser diagnostics are addressed.
5. Semantic uncertainty is surfaced (no false “validated” claims).
6. For DDL or risky execution, explicit user intent is present.

If a gate fails, output an assumption-labeled template or ask for missing schema instead of a false-final query.

## Capability Map

Use this map to fetch only what is needed:

- `references/query-generation.md`: SELECT build/repair, ambiguous fields, aliasing, clause repairs.
- `references/ddl-generation.md`: CREATE/ALTER/MODIFY/DROP workflow and confirm modes.
- `references/arrays-polymorphism.md`: PackageHeader/polymorphism/RECORD/UNION interactions.
- `references/functions-windows.md`: stateful/stateless function behavior and emission semantics.
- `references/concepts/stateful-functions.md`: stateful function families, argument patterns, and examples.
- `references/concepts/stateless-functions.md`: stateless function families, internal functions, and examples.
- `references/mcp-workflow.md`: MCP grounding flow, parser-only caveat, execute safety.
- `references/concepts/index.md`: task-to-reference routing guide.
- `references/concepts/constants-and-literals.md`: numeric/string/char/timestamp/interval constants.
- `references/concepts/time-and-filtering.md`: timestamp literals, timezone assumptions, `WHERE` vs `HAVING`.
- `references/concepts/filters-and-predicates.md`: `WHERE`, `BETWEEN`, `IN`, `LIKE`, null/NaN, type predicates.
- `references/concepts/subscription-hints.md`: subscription pushdown rules for timestamp and symbol; when optimization applies and when it does not.
- `references/concepts/arrays.md`: generic array mechanics (`ANY`/`ALL`, slicing, raw `ARRAY JOIN` usage).
- `references/concepts/casts.md`: cast patterns and alias-vs-cast disambiguation.
- `references/concepts/operators-conditionals.md`: operator semantics, `CASE`/`IF`, `.?` mask alignment behavior.
- `references/concepts/data-types.md`: practical type constraints and mismatch handling.
- `references/concepts/keywords-and-shaping.md`: `WITH`, `TYPE`, `FIELD`, `RECORD`, `THIS`, `LIMIT`, `OFFSET`.
- `references/concepts/inner-queries.md`: staged query patterns with subqueries in `FROM`.
- `references/concepts/union.md`: SELECT UNION, stream UNION, fixed vs polymorphic output.
- `references/recipes.md`: compact end-to-end patterns.

## Output Style

Return QQL first, then short notes on assumptions, validation scope, or unresolved semantic risks. Keep teaching detail concise unless user asks for deeper explanation.
