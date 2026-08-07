# Dynamic Resubscription

Changing a live cursor's entity subscription mid-poll, without closing and recreating the cursor.

```cpp
std::unique_ptr<TickCursor> cursor(stream->createCursor(SelectionOptions()));
cursor->reset(startTime);
DataReader &reader = cursor->getReader();
InstrumentMessage header;

// Start narrow, then widen once some other condition is met.
cursor->addEntity(InstrumentIdentity("AAPL"));

bool addedMore = false;
while (true) {
    bool hasNext = cursor->nextIfAvailable(&header);
    if (header.cursorState >= 2) {
        break;
    }
    if (hasNext) {
        // ... decode fields via reader

        if (!addedMore /* && some task-specific condition */) {
            std::vector<InstrumentIdentity> more = {InstrumentIdentity("MSFT"), InstrumentIdentity("GOOG")};
            cursor->addEntities(more);
            cursor->removeEntity(InstrumentIdentity("AAPL"));
            addedMore = true;
        }
    }
}
cursor->close();
```

`subscribeToAllEntities()`/`subscribeToAllTypes()` switch the cursor to receiving every entity/type instead of an explicit list, use them instead of enumerating identities when the task genuinely needs "everything", not as a default.

See `cursor-and-streams.md` for the underlying API and the `cursorState` end-of-cursor caveat, [`live-cursor.md`](live-cursor.md) for the base live-poll pattern this extends.
