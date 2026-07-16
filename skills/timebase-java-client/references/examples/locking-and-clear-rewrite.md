# Locking And Clear-Rewrite

**Type:** fragment, assumes a write-capable `DXTickDB` connection and an existing stream.

**When to use:** Bulk-updating a reference-data stream (e.g. securities) that other applications also read. See `locking-and-securities-update.md` for the rationale.

## Basic lock/release

```java
import deltix.qsrv.hf.tickdb.pub.lock.*;

DBLock lock = null;
try {
    lock = stream.tryLock(LockType.WRITE, 30_000); // timeout in ms; call must be inside the try
    // ... exclusive work ...
} catch (StreamLockedException ex) {
    System.out.println("Cannot lock stream: " + ex);
} finally {
    if (lock != null) {
        lock.release();
    }
}
```

## Clear-and-rewrite with a bound cache

```java
DBLock lock = null;
try {
    lock = stream.tryLock(LockType.WRITE, 30_000); // call must be inside the try to be caught/released correctly

    Map<InstrumentIdentity, InstrumentMessage> cache = new HashMap<>();

    try (TickCursor cursor = stream.select(Long.MIN_VALUE, new SelectionOptions())) {
        while (cursor.next()) {
            InstrumentMessage msg = cursor.getMessage().clone(); // deep copy before caching
            cache.put(new InstrumentKey(msg.getInstrumentType(), msg.getSymbol()), msg);
        }
    }

    // ... mutate cache in memory, e.g. cache.get(new InstrumentKey(InstrumentType.EQUITY, "MSFT")) ...

    stream.clear();

    try (TickLoader loader = stream.createLoader()) {
        for (InstrumentMessage msg : cache.values()) {
            loader.send(msg);
        }
    }
} finally {
    if (lock != null) {
        lock.release();
    }
}
```

## Raw variant with a generic field editor

```java
public boolean editField(InstrumentMessage idAndTime, RecordClassDescriptor type,
                          String fieldName, ReadableValue in, WritableValue out) {
    if (fieldName.equals("brokerID")) {
        out.writeString("TRADE." + idAndTime.getSymbol());
        return true; // true = edited; false = caller should copy the value unchanged
    }
    return false;
}

static void move(DataType type, ReadableValue in, WritableValue out) {
    if (in.isNull()) {
        out.writeNull();
    } else if (type instanceof DateTimeDataType || type instanceof IntegerDataType || type instanceof TimeOfDayDataType) {
        out.writeLong(in.getLong());
    } else if (type instanceof FloatDataType) {
        FloatDataType ft = (FloatDataType) type;
        if (ft.isFloat()) out.writeFloat(in.getFloat());
        else out.writeDouble(in.getDouble());
    } else if (type instanceof BooleanDataType) {
        out.writeBoolean(in.getBoolean());
    } else {
        out.writeString(in.getString());
    }
}
```

```java
while (decoder.nextField()) {
    boolean encoderHasNext = encoder.nextField(); // always true here — same descriptor drives both
    String fieldName = decoder.getField().getName();
    if (!editField(idAndTime, type, fieldName, decoder, encoder)) {
        move(decoder.getField().getType(), decoder, encoder);
    }
}
```
