# Order-book validation artifacts

## Run validation

`POST {hostRoot}/api/v0/{streamId}/validateOrderBook` accepts an optional JSON body. The path `streamId` is copied into the server-side request. Its request fields include `from`, `to`, `symbols`, `live`, tick parameters, depth parameters, and validation checks.

The completed JSON response can contain summary fields including `streamKey`, time range, counts, `downloadId`, `reportFileName`, and inline `issues`. Follow the target contract's completion behavior, keep the operation within the helper timeout, and check the reported failure state. Do not invent a polling endpoint.

Validate the report against the target response contract before reporting completion. Require a valid `downloadId` when downloading the report. Missing or malformed report fields do not establish a report with zero issues; preserve a valid empty issue list as such.

Use a finite `from`/`to` range and an explicit symbol subset where practical. Validate `from <= to`, positive `marketDepth`, and `0 <= minValidNumberOfLevels <= marketDepth` before sending. Decimal-valued tick and mispricing values are strings.

## Read issues tightly

`GET {hostRoot}/api/v0/orderBookValidation/report/{id}/issues` accepts optional `from`, `to`, `offset`, `rows`, `severity`, `sourceName`, and `symbol`.

Check the target contract's page-size limit. For a complete paginated result, require `offset`, `rows`, `hasMore`, and `inlineOnly`. Treat absent `issues` as an empty array only when the contract permits omission. Helpers should choose a smaller explicit page size, advance offset by the actual returned issue count, and stop at `hasMore == false`, the maximum pages, or the maximum issues.

Require non-negative integer `offset` and `rows` and boolean `hasMore` and `inlineOnly`. Reject null or non-array `issues` values when the field is present. Validate issue records and `warningMessage` when present. Check that the returned offset matches the requested page. If `hasMore` is true but no issues are returned, stop with an incomplete result instead of looping.

After consuming a valid page, check `hasMore` before treating a reached page or item limit as incomplete. Pagination is complete when `hasMore == false` and all returned issues were retained, even at exactly the limit. Report incomplete results when a limit stops traversal while `hasMore == true`, or when the item limit truncates the returned page. Preserve `inlineOnly` and `warningMessage` restrictions in either case.

## Download reports

`GET {hostRoot}/api/v0/orderBookValidation/report/{id}/download` streams an octet-stream report. The same `from`, `to`, `severity`, `sourceName`, and `symbol` filters are supported. The filtered server response is JSON Lines; use a `.jsonl` fallback name when the caller and response provide none. A missing report returns `404`.

Follow [safe artifact downloads](exports-and-artifacts.md#safe-artifact-downloads) for destination selection, temporary files, publication, cleanup, and result reporting. Delete via `DELETE /api/v0/orderBookValidation/report/{id}` is a state-changing operation; follow [`writes-and-confirmation.md`](writes-and-confirmation.md) and check the deployed contract. A read or download request alone does not authorize report deletion.
