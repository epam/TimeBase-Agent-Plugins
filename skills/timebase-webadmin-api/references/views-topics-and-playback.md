# Views, topics, and playback

## Views and topics

`/api/v0/timebase/views*` provides view list/get/create/delete and lifecycle actions. `/api/v0/topics*` provides topic list, structure, schema, create, delete, and rename. Listing/structure/schema are reads; creation, deletion, and lifecycle are state changes. Verify that topic rename is implemented before offering it; a declared route can still reject the operation.

Topic monitoring uses STOMP at `/user/topic/monitor-topic/{topicId}`. Subscribe with a timeout and explicit close behavior; do not substitute REST polling.

Topics require Aeron on the TimeBase server. An empty topic list does not prove topic support. Verify schema and, when authorized, creation on a disposable topic before claiming compatibility.

## Playback

`/api/v0/playback` creates/lists jobs, and `/api/v0/playback/{close,pause,play,resume,skip,speed,stop,permanent}` changes a job. Check the target contract and authorization before automating an operation. Playback progress/status uses STOMP at `/user/topic/playback/{id}`.

Check playback listing permissions on the target server. For request-body timestamps, check the target parser's precision requirement; UTC with milliseconds, such as `2026-01-01T00:00:00.000Z`, is one accepted shape.

Specify the requested stream/source, playback job, rate, and control action, and follow [`writes-and-confirmation.md`](writes-and-confirmation.md) for authorization. Preserve the returned job ID in the operation result, subscribe before starting work where progress matters, and stop at the helper timeout. Include stopping a job created by the helper in the authorized timeout cleanup; preserve unrelated jobs.

Read [`stomp-client.md`](stomp-client.md) for connection configuration and cleanup.
