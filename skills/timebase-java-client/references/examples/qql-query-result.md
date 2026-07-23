# QQL Query Result Binding

**Type:** fragment, assumes QQL text finalized (use qql-generator skill if not).

**When to use:** Execute QQL from Java and bind rows to a typed result.

## Result class for the projected field(s)

```java
import deltix.qsrv.hf.pub.InstrumentMessage;

public class CloseResult extends InstrumentMessage {
    public double close;
}
```

## Execute with an embedded filter, a bind parameter, and result binding

```java
import deltix.qsrv.hf.pub.SimpleTypeLoader;
import deltix.qsrv.hf.tickdb.pub.*;
import deltix.qsrv.hf.tickdb.pub.query.Parameter;

SelectionOptions options = new SelectionOptions();
options.raw = false;
options.typeLoader = new SimpleTypeLoader(null, CloseResult.class);

String qql = "select close from \"" + streamKey + "\" where symbol == $symbol";
Parameter symbol = Parameter.VARCHAR("$symbol", "GOOG");

try (InstrumentMessageSource cursor = db.executeQuery(qql, options, symbol)) {
    while (cursor.next()) {
        CloseResult msg = (CloseResult) cursor.getMessage();
        System.out.println(msg.getSymbol() + " close=" + msg.close);
    }
}
```

`options.typeLoader` binds the anonymous projection type QQL creates for `select close` to `CloseResult`, so its field is reachable as `msg.close`. Without it, the projected value isn't accessible from the returned message. Only needed for partial field lists, `select *` returns the underlying message type directly and doesn't need a `typeLoader`.

For queries spanning multiple streams or a time range, embed those filters in the QQL text (`(stream1 UNION stream2)`, `WHERE timestamp >= ...`) rather than using deprecated `executeQuery` overloads that take explicit stream/time arguments. See `qql-execution-from-java.md`.
