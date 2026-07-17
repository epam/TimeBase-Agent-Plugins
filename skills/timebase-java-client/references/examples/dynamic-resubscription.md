# Dynamic Resubscription

**Type:** fragment, assumes an open `TickCursor`.

**When to use:** Changing a cursor's subscription at runtime (e.g. a watchlist the user edits live) instead of tearing down and rebuilding the cursor. See `cursor-and-streams.md` for the full mutator method list.

```java
cursor.removeEntity(new InstrumentKey(InstrumentType.EQUITY, "AAPL"));
cursor.addEntity(new InstrumentKey(InstrumentType.EQUITY, "MSFT"));
cursor.addTypes(BarMessage.class.getName());
```
