# Read/Write Raw (Custom Schema)

**Type:** fragment, assumes a stream with a custom schema that has no generated/bound Java class.

**When to use:** The schema was defined via an explicit `RecordClassDescriptor` and no matching POJO exists.

## Write

```java
import deltix.qsrv.hf.pub.RawMessage;
import deltix.qsrv.hf.pub.codec.*;
import deltix.qsrv.hf.tickdb.pub.*;
import deltix.util.memory.MemoryDataOutput;

LoadingOptions options = new LoadingOptions(true, LoadingOptions.WriteMode.REWRITE);

try (TickLoader loader = stream.createLoader(options)) {
    FixedUnboundEncoder encoder = CodecFactory.COMPILED.createFixedUnboundEncoder(descriptor);
    MemoryDataOutput out = new MemoryDataOutput();

    RawMessage msg = new RawMessage(descriptor);
    msg.setSymbol("AAPL");
    msg.setTimeStampMs(System.currentTimeMillis());

    encoder.beginWrite(out);
    encoder.nextField();
    encoder.writeDouble(100.0); // closePrice, in field-declaration order
    encoder.nextField();
    encoder.writeDouble(101.0); // openPrice
    encoder.endWrite(); // optional: validates NOT NULL fields weren't left unwritten

    msg.setBytes(out, 0);
    loader.send(msg);
}
```

Fields must be written in the exact order they appear in the `RecordClassDescriptor`. `encoder.endWrite()` is an optional validation step, it checks that non-nullable fields weren't skipped, worth calling after the last field, but not required for the encoding itself to be correct.

## Read

```java
import deltix.qsrv.hf.pub.RawMessage;
import deltix.qsrv.hf.pub.codec.*;
import deltix.qsrv.hf.pub.md.NonStaticFieldInfo;
import deltix.qsrv.hf.tickdb.pub.*;
import deltix.util.memory.MemoryDataInput;

SelectionOptions options = new SelectionOptions(true, false); // (raw, live)

String[] types = { descriptor.getName() };

try (TickCursor cursor = stream.select(Long.MIN_VALUE, options, types)) { // 3-arg form: no entity filter
    UnboundDecoder decoder = CodecFactory.COMPILED.createFixedUnboundDecoder(descriptor);
    MemoryDataInput in = new MemoryDataInput();

    while (cursor.next()) {
        RawMessage msg = (RawMessage) cursor.getMessage();
        in.setBytes(msg.data, msg.offset, msg.length);
        decoder.beginRead(in);

        while (decoder.nextField()) {
            NonStaticFieldInfo field = decoder.getField();
            System.out.println(field.getName() + ": " + decoder.getString());
        }
    }
}
```
