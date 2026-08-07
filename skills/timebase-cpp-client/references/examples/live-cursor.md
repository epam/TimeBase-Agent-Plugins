# Live / Resettable Cursor

```cpp
std::unique_ptr<TickCursor> cursor(stream->createCursor(SelectionOptions()));
cursor->reset(startTime);
DataReader &reader = cursor->getReader();
InstrumentMessage header;
while (true) {
    bool hasNext = cursor->nextIfAvailable(&header);
    if (header.cursorState >= 2) {
        break; // cursor truly ended, not just "nothing ready yet"
    }
    if (hasNext) {
        // ... decode fields via reader
    }
    // else: nothing available yet, poll again
}
cursor->close();
```

See `cursor-and-streams.md` (Live / resettable cursor) for why `nextIfAvailable` and `header.cursorState` need to be checked this way, and for the `SelectionOptions::live` caveat.
