# Read/Write Bound

**Type:** fragment, assumes a stream already exists with a matching schema.

**When to use:** Typed round trip using a built-in or generated message class.

## Write

```java
import deltix.qsrv.hf.tickdb.pub.TickLoader;
import deltix.timebase.api.messages.BarMessage;

try (TickLoader loader = stream.createLoader()) {
    BarMessage msg = new BarMessage();
    msg.setSymbol("AAPL");
    msg.setTimeStampMs(System.currentTimeMillis());
    msg.setOpen(100.0);
    msg.setClose(101.0);
    loader.send(msg);
}
```

## Read

```java
import deltix.qsrv.hf.pub.InstrumentMessage;
import deltix.qsrv.hf.tickdb.pub.*;
import deltix.timebase.api.messages.BarMessage;

SelectionOptions options = new SelectionOptions();
options.raw = false;

String[] types = { BarMessage.class.getName() };

try (TickCursor cursor = stream.select(Long.MIN_VALUE, options, types)) { // 3-arg form: no entity filter
    while (cursor.next()) {
        InstrumentMessage msg = cursor.getMessage();
        if (msg instanceof BarMessage) {
            BarMessage bar = (BarMessage) msg;
            System.out.println(bar.getSymbol() + " close=" + bar.getClose());
        }
    }
}
```
