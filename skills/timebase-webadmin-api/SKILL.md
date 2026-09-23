---
name: timebase-webadmin-api
description: >-
  Use for TimeBase WebAdmin or Web Gateway REST API and STOMP integration:
  explain requests and authentication, build or debug custom clients, and work
  with streams, schemas, queries, stream imports and exports (including QSMSG),
  views, topics, playback, validation, and chart data.
---

# TimeBase WebAdmin API

## Route

Follow the user's requested deliverable:

1. Give request examples and connection guidance for an integration question that does not ask for code or execution.
2. Execute one requested API operation, such as exporting a stream, with an available client or a minimal local script when the user asks for the result.
3. Generate a focused REST/STOMP helper when the user asks for code for one workflow.
4. Build a reusable REST/STOMP client for an SDK, package, application client, or multiple WebAdmin domains.

For a bounded WebAdmin inspection request without an explicit API or client-code requirement, use an advertised WebAdmin MCP inspection tool when it can answer directly. See [MCP setup](https://github.com/epam/TimeBase-MCP/blob/main/docs/webadmin-setup.md) for its configuration.

## Complete the selected route

- For integration guidance, consult the relevant capability reference and provide the requested explanation or request examples. Finish with assumptions and deployment checks that the user will need before execution. Live discovery, login, and execution are unnecessary unless requested.
- For one-off execution, use the relevant capability reference, the target operation contract, and [authentication](references/authentication.md) if protected. Apply [HTTP request requirements](references/endpoint-contract.md#http-requests), [response validation](references/endpoint-contract.md#validate-responses), and [safe artifact downloads](references/exports-and-artifacts.md#safe-artifact-downloads) when applicable. For a state change, follow [authorization and execution](references/writes-and-confirmation.md). Report the result or blocker. An existing HTTP client with redirects disabled does not need a new helper or its regression suite.
- For a helper or reusable client, follow the client sections below.

## Client shape

- **Helper:** implement one workflow with explicit inputs, bounds, and artifact handling when applicable. Follow the [output rules](#output) for its result.
- **Reusable client:** read [`references/full-client-architecture.md`](references/full-client-architecture.md) before coding. Build shared transport and typed operations for the requested domains; add a STOMP boundary only when an included workflow needs it.

For both shapes, expose typed domain operations and keep low-level transport internal or explicitly marked advanced.

## Generated client workflow

1. [Select a live or supplied versioned contract](references/endpoint-contract.md#select-the-contract) and the relevant family references from the capability map. Verify each operation against that contract.
2. For protected operations, read [`references/authentication.md`](references/authentication.md) for discovery, mechanism selection, credential handling, and lifecycle.
3. Determine whether the operation changes server state, regardless of its HTTP verb or whether it produces an artifact or job. For any state change, follow [authorization and execution](references/writes-and-confirmation.md) when preparing the code and before live execution.
4. Generate the selected client shape in the requested language. Accept explicit connection, credential-provider, operation, and limit inputs. Apply the shared [HTTP request requirements](references/endpoint-contract.md#http-requests) and, for multi-stage or event-driven operations, [workflow state](references/client-lifecycle.md#workflow-state). For STOMP, read [`references/stomp-client.md`](references/stomp-client.md).
5. Validate responses using [the operation contract](references/endpoint-contract.md#validate-responses) before using their values in another request, publishing an artifact, or reporting success. Follow [resource ownership and cleanup](references/client-lifecycle.md#resource-ownership-and-cleanup) and, for downloads, [safe artifact downloads](references/exports-and-artifacts.md#safe-artifact-downloads). Present results using the [output rules](#output).
6. [Verify and deliver](#verify-and-deliver) the requested implementation, usage instructions, and validation results. If execution was requested, also report its result or exact blocker; generated code alone does not complete an execution request.

## Verify and deliver

- Implement the requested path through usable REST/STOMP transports or explicitly supplied providers. Identify dependencies the caller must supply. An unimplemented step is a delivery gap unless the user requested an outline or that extension point; name the remaining integration work.
- Exercise the generated CLI or public library method with contract-valid data and failures applicable to the operation. For JSON, test missing required fields only where the contract defines them and invalid nested types only for fields the workflow consumes. For credentialed HTTP, use synthetic credentials to verify that an untrusted destination receives none. Include relevant failure checks from the selected references and verify observable results; compilation or a successful-path demonstration alone does not complete verification. Shared behavior needs one check per implementation, not per endpoint.
- Check usage commands and configuration names against the generated or installed interface. Examples must follow the same request, output, and resource rules as the implementation.
- Report what was implemented, which checks ran, their results, and what remains unverified or blocked. Controlled responses establish client behavior. Claim deployment compatibility only for the deployment and operation verified live. Offline generation can finish with local checks and explicit pending deployment checks.

## Output

- Library methods return typed results and expose errors to the caller. The calling application owns printing and logging, including serialization of artifact metadata.
- A read CLI prints the requested validated data in the requested format, within byte and item limits. Include any truncation or incomplete status; a status-only manifest does not replace the requested data.
- An artifact CLI saves the payload locally and emits a compact JSON manifest with the operation, completion status, final artifact path only after publication, byte count when available, and warnings. Job and mutation CLIs report the operation result and any IDs needed for follow-up or cleanup.
- Keep credentials and tokens out of output. Errors contain a status when available and a redacted, size-bounded summary. CLI diagnostics go to stderr so stdout remains usable as data.

## Capability map

- [`references/platform-and-authentication.md`](references/platform-and-authentication.md): health, version, auth discovery, session actions, and capability calls.
- [`references/streams-and-schema.md`](references/streams-and-schema.md): streams, schemas, spaces, symbols, ranges, options, and data administration.
- [`references/query-selection-and-charting.md`](references/query-selection-and-charting.md): select/query/filter/compile/describe/functions, order-book snapshots, charts, and flowchart.
- [`references/exports-and-artifacts.md`](references/exports-and-artifacts.md): stream/QQL export preparation and bounded downloads.
- [`references/imports-and-stomp.md`](references/imports-and-stomp.md): CSV/QSMSG import workflows, chunks, artifacts, and STOMP progress.
- [`references/views-topics-and-playback.md`](references/views-topics-and-playback.md): query views, topics, monitoring, and playback controls.
- [`references/order-book-validation.md`](references/order-book-validation.md): validation, issue pages, and reports.
