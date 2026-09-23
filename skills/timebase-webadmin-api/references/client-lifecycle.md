# Client workflow and resource lifecycle

Use these rules for focused helpers and reusable clients. Apply workflow state
to multi-stage or event-driven operations, and resource ownership to requests,
files, subscriptions, and jobs.

## Workflow state

For multi-stage operations, identify each stage's prerequisites, transitions,
and completion conditions from the selected API contract. Record identifiers
and ownership when resources are acquired, before dependent steps run.

Keep current state, completion and failure facts, and owned resource identifiers
separate from bounded progress or diagnostic history. Process events into state
even when their details cannot be retained. Trimming history must not change the
outcome or lose information needed for cleanup. Determine success from the
contract's completion conditions and required result verification, rather than
the last retained message.

## Resource ownership and cleanup

Track resources as they are acquired, distinguishing those owned by the operation
from borrowed resources and requested outputs. Release only resources owned by
the operation or covered by the caller's cleanup authorization.

On every exit path, attempt all required cleanup within bounded waits, even if
one action fails. Make cleanup safe to repeat and safe after disconnection or
partial setup. Preserve the original operation failure and report cleanup
failures separately, including any resources left behind. Retain requested
outputs unless their removal is authorized.

For a generated workflow that owns multiple resources, inject a failure into one
cleanup action. Verify that the remaining actions still run, borrowed resources
stay usable, and repeated cleanup leaves no resources silently abandoned. Check
that the caller receives both the operation failure and any cleanup failures.
