# Imports and STOMP progress

CSV operations live under `/api/v0/import/csv/*`; QSMSG import uses `/api/v0/initImport`, `/api/v0/importChunk/{id}`, and `/api/v0/import/schema/{id}`. Consult the [selected contract](endpoint-contract.md#select-the-contract) for every setup, preview, mapping, schema, setting, upload, completion, cancellation, and log route.

All import setup and upload operations require write authority. Follow [`writes-and-confirmation.md`](writes-and-confirmation.md) before live setup, uploads, or chunk requests. Prepare the helper and inspect local input before requesting any missing approval. Keep source files local, limit accepted bytes/chunks, calculate a source hash, and specify the stream target, format, and request parameters. Record the server-assigned import ID after initialization, use it for subsequent steps and cleanup, and include it in the operation result.

Import completion and progress are STOMP workflows, not REST polling:

- `/user/topic/initImport/csv/{id}` and `/user/topic/startImport/csv/{id}`;
- `/user/topic/initImport/qsmsg/{id}` and `/user/topic/startImport/qsmsg/{id}`.

Subscribing to `initImport` keeps the upload active; subscribing to `startImport` **starts the import**. Treat that subscription as a write. Verify the exact STOMP destination with the target server before starting an import; follow the [contract correction rules](endpoint-contract.md#resolve-contract-differences) if its parser differs from the documented destination.

Bound the wait and apply [workflow state](client-lifecycle.md#workflow-state) to import events and bounded progress/error history. Record `FINISHED` and prior errors independently of retained messages. A `FINISHED` event alone is insufficient: check the accumulated error state and verify the imported schema and rows. Follow the [output rules](../SKILL.md#output); persist a log only when requested by the caller. Preserve the `.gz` extension for gzip exports because the importer selects decompression by filename. If STOMP is unavailable, stop with an incomplete status; do not invent a REST status endpoint. CSV log downloads follow [safe artifact downloads](exports-and-artifacts.md#safe-artifact-downloads).

Read [`stomp-client.md`](stomp-client.md) for connection configuration and cleanup.

For CSV, initialize the import and upload a preview before requesting default settings. Set the timezone explicitly; generated settings can contain `timeZone: null` and fail validation unchanged. Validate mappings and data, save settings, reserve the upload process with its total size, then upload the file. Schema inference reads the uploaded file, so `/csv/schema/{id}` is not a preview-only operation. Start via the STOMP subscription and verify imported rows. `/api/v0/import/finish/{id}` releases import metadata; it does not start the import.
