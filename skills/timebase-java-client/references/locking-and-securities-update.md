# Locking And Reference-Data Update

Use this reference when the task needs to safely update a reference-data-style stream (e.g. a securities stream) that other applications also read, or otherwise needs explicit stream locking.

## Why lock

`DXTickStream` supports advisory locking via `LockType.READ`/`LockType.WRITE`. Locking a stream before a bulk update does two things. It prevents other writers from corrupting the data mid-update. And releasing the lock emits a system `EventMessage` on the `TickDBFactory.EVENTS_STREAM_NAME` stream, which is how other applications learn the data changed and should reload their caches. Only lock when the update genuinely needs to be atomic/exclusive from the perspective of other consumers, not for routine single-message writes.

`stream.tryLock(type, timeoutMs)` always throws `StreamLockedException` if the lock isn't acquired within the timeout, it never just returns. `stream.lock(type)` has no timeout parameter and is non-blocking: it throws the same `StreamLockedException` immediately if the stream is already locked, rather than waiting. Use `tryLock` when the caller should wait up to a timeout instead of failing fast. See [`examples/locking-and-clear-rewrite.md`](examples/locking-and-clear-rewrite.md) for the acquire/release pattern.

**Important**: the `tryLock(...)` call must be made *inside* the `try` block, with the `DBLock` variable declared beforehand as `null`. Not before it, otherwise a thrown `StreamLockedException` bypasses the `catch`/`finally` entirely. If `tryLock` throws, `lock` stays `null` and `finally` correctly skips `release()`. Either catch the exception locally or declare `throws StreamLockedException` on the enclosing method and let the caller decide how to handle a lock failure. Don't silently swallow it.

## No in-place update, clear then rewrite

TimeBase streams have no in-place update. The idiom for editing a reference-data stream (small enough to fit in memory, e.g. instrument metadata) is:

1. Lock the stream (`WRITE`).
2. Read all existing records into memory.
3. `stream.clear()` (a varargs `clear(InstrumentIdentity... ids)` method, an empty call clears every entity, so it removes all data).
4. Write the edited copies back via a loader.
5. Release the lock in a `finally` block.

`InstrumentKey` and `ConstantInstrumentKey` are both concrete `InstrumentIdentity` implementations (symbol + `InstrumentType`), but `InstrumentKey` is mutable and its own javadoc warns it must not be used as a `java.util.Map` key. Use `ConstantInstrumentKey` for caching records by instrument.

**Important**: always clone messages (`message.clone()`) before storing them in a collection. The cursor reuses its internal message buffer, so a stored reference without cloning will be silently overwritten on the next `cursor.next()`.

## Raw variant with a generic field editor

When editing without a bound Java class, decode/re-encode field-by-field with a pluggable per-field edit hook instead of a fixed POJO. A caller-supplied `editField(...)` hook gets first refusal on each field, falling back to a generic type-dispatching copy (`move(type, in, out)`) when the hook declines. The caller iterates `decoder.nextField()`/`encoder.nextField()` in lockstep, they always align since both are built from the same `RecordClassDescriptor`. Only reach for this raw approach when there's no bound class to edit directly, or the same edit logic must apply generically across many field types. See `examples/locking-and-clear-rewrite.md` for both the bound and raw variants.

## Common mistakes

- Skipping the lock on a bulk reference-data rewrite that other applications also read.
- Storing cursor messages in a collection without cloning them first.
- Forgetting that `stream.clear()` removes *all* data, never call it without first having a complete in-memory copy (or explicit user confirmation that data loss is intended).
- Treating this as the pattern for routine single-message writes, it's for bulk rewrites of small reference-data streams only.
- Calling `tryLock(...)` before entering the `try` block instead of inside it.
- Assuming `tryLock(...)` can return `null` or otherwise fail silently on timeout, it always throws `StreamLockedException`.
