# Live Cursor

**Type:** fragment

**When to use:** Consume live messages as they arrive. MCP-ground the stream key.

```java
import deltix.qsrv.hf.pub.util.LiveCursorWatcher;
import deltix.qsrv.hf.tickdb.pub.*;
import deltix.timebase.api.messages.BarMessage;

SelectionOptions options = new SelectionOptions();
options.raw = false;
options.live = true;

String[] types = { BarMessage.class.getName() };

TickCursor cursor = stream.select(System.currentTimeMillis(), options, types); // 3-arg form: no entity filter
LiveCursorWatcher watcher = new LiveCursorWatcher(cursor, msg -> {
    if (msg instanceof BarMessage) {
        BarMessage bar = (BarMessage) msg;
        System.out.println("[LIVE] " + bar.getSymbol() + " close=" + bar.getClose());
    }
});

// ... produce or wait for data ...
watcher.close();
cursor.close();
```

Close the watcher and the cursor on shutdown.
