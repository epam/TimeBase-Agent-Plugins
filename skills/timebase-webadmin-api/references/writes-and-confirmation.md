# Authorized state changes

Use this branch for stream/schema/data administration, imports, view/topic lifecycle, playback controls, report deletion, session actions, and every legacy GET mutation.

## Prepare and authorize

Prepare the complete helper or client, including verification, cancellation, and cleanup, before requesting any required approval for live execution. Make the proposed operation reviewable by stating:

- host root and authentication profile identifier;
- exact operation, method, normalized path, and target identifiers;
- request inputs, source artifacts when relevant, and expected impact;
- verification and cancellation/cleanup actions.

Use the user's request and existing approvals to determine the authorized scope. Ask only for missing information or authorization, an approval the user explicitly reserved, or a change outside that scope. Obtain any required approval before the first live mutation. Code generation and local preparation can proceed before that approval.

Use saved plans only when the user or application requires them. Reusable clients leave authorization and any confirmation UI to the caller; their methods do not require conversational approval or expiring plan files. Use the configured identity with the required permissions and preserve server-side `TB_ALLOW_WRITE` as the enforcement layer.

## Execution

Execute only the authorized operations against the specified host and targets. Record server-assigned job and import IDs as they become available. Do not auto-retry non-idempotent calls. Capture a bounded operation result and verify it with a non-mutating read. If the server reports that the TimeBase connection is read-only, stop rather than attempting a fallback.

Include cancellation and cleanup of work started by the helper in the authorized workflow, such as stopping its chart request or releasing its import metadata. Run those actions on completion, failure, timeout, or cancellation as appropriate without a second approval. Follow [resource ownership and cleanup](client-lifecycle.md#resource-ownership-and-cleanup); stopping unrelated jobs or deleting pre-existing resources requires authorization covering those targets.

Test state-changing operations against a disposable target before their first production use.
