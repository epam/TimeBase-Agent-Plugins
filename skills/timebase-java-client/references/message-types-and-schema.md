# Message Types And Schema

Use this reference when generating bound message classes, creating streams, or choosing raw vs bound reads/writes.

## Built-in message types

`deltix-timebase-api-messages` ships ready-made types such as `InstrumentMessage`, `BarMessage`, `TradeMessage`, and `BestBidOfferMessage`. Prefer these when the stream schema matches; do not invent custom POJOs unnecessarily.

## Three ways to get a schema, pick by what already exists

1. **Built-in message type** — no schema work needed; use the class directly (previous section).
2. **Introspection from an annotated POJO** — the class already exists (or is the natural shape of the domain object); derive the descriptor from it instead of hand-writing one. See below.
3. **Explicit `RecordClassDescriptor`** — no POJO exists yet, or the schema must be defined independently of any Java class (e.g. schema arrives from MCP `get_stream_schema` as field names/types only). See below.

Prefer (1), then (2), then (3) — don't hand-build a `RecordClassDescriptor` when a POJO could be introspected instead, and don't introspect a POJO that was itself invented without schema evidence.

## Custom bound POJOs via introspection

Introspection works on a plain POJO's public fields — `@SchemaElement` is **optional**, not required:

```java
import deltix.qsrv.hf.pub.InstrumentMessage;
import deltix.qsrv.hf.pub.md.RecordClassDescriptor;
import deltix.qsrv.hf.pub.md.Introspector;

public class MyBarMessage extends InstrumentMessage {
    public double closePrice;
    public double openPrice;
}

Introspector introspector = Introspector.createEmptyMessageIntrospector();
RecordClassDescriptor descriptor = introspector.introspectRecordClass(MyBarMessage.class);
```

This derives field names/types directly from the public fields by reflection. Add `@SchemaElement` only when the schema name must differ from the Java identifier (e.g. a schema field name that isn't a valid Java field name, or a different display title):

```java
@SchemaElement(name = "myapp.messages.BarMessage", title = "Bar Message")
public class MyBarMessage extends InstrumentMessage {

    @SchemaElement(name = "closePrice", title = "Close Price")
    public double closePrice;

    public double openPrice; // no annotation needed if the field name already matches the schema
}
```

Ground field names from MCP `get_stream_schema` or user-provided schema when the POJO doesn't already exist. If schema is unknown, label the POJO as illustrative and tell the user to confirm field names before production use.

When a class encapsulates state behind getters/setters instead of exposing public fields, pair `@SchemaElement` with `@SchemaType(dataType = ..., encoding = ...)` on the getter instead — see `schema-evolution.md` for a worked example extending a message type this way.

`Introspector.introspectSingleClass(MyBarMessage.class)` is an equivalent shorthand for the two-line `createEmptyMessageIntrospector().introspectRecordClass(...)` form above — it returns the base `ClassDescriptor` type, so cast to `RecordClassDescriptor` when you need the more specific type. Either form is fine; prefer whichever the surrounding code already uses.

`introspectRecordClass` (and the `introspectSingleClass` shorthand) declare `Introspector.IntrospectionException` — catch it or let it propagate; don't swallow it silently.

## Explicit schema without a POJO

Build a `RecordClassDescriptor` directly from `DataField`s when no POJO exists or introspection is insufficient:

```java
import deltix.qsrv.hf.pub.md.*;

DataField[] fields = {
    new NonStaticDataField("closePrice", "Close Price",
        new FloatDataType(FloatDataType.ENCODING_FIXED_DOUBLE, true)),
    new StaticDataField("exchange", "Exchange Code",
        new VarcharDataType("ALPHANUMERIC(10)", true, false), "XNAS")
};

RecordClassDescriptor descriptor = new RecordClassDescriptor(
    "myapp.messages.BarMessage", "Bar Message", false, null, fields);
```

`NonStaticDataField` varies per message; `StaticDataField` takes a constant value shared by every message of that type (the last constructor argument above, `"XNAS"`) — use it for values that never change within a type, such as a fixed exchange code.

`DataType` cheat sheet: `IntegerDataType`, `FloatDataType`, `VarcharDataType`, `DateTimeDataType`, `BooleanDataType`, `ArrayDataType` (element type nested inside), `ClassDataType` (polymorphic/nested object), `EnumDataType`.

## Raw vs bound

- **Bound**: a generated/annotated Java class maps directly to the schema. Read with `SelectionOptions.raw = false`; `cursor.getMessage()` returns the typed `InstrumentMessage` subclass. Write with `TickLoader.send(InstrumentMessage)`.
- **Raw**: required for schemas that have no generated/bound Java class. Set `SelectionOptions.raw = true` (reads) and `new LoadingOptions(true, ...)` (writes). Reads return `RawMessage`; decode fields with `UnboundDecoder` from `CodecFactory`. Writes encode fields with `FixedUnboundEncoder` from `CodecFactory` into a `RawMessage`. Once all fields are written, `encoder.endWrite()` is an optional validation step (checks non-nullable fields weren't left unwritten) — not required for the encoding to be valid, but cheap insurance.

`SelectionOptions` has convenience constructors beyond the no-arg default + field assignment shown above: `new SelectionOptions(raw, live)`, `(raw, live, reversed)`, `(raw, live, reversed, shiftOffset)`, and `(raw, live, ChannelQualityOfService)`. Prefer whichever form (no-arg + assignment, or a convenience constructor) matches the surrounding code's existing style; both are equally correct.

## Custom type binding: `SimpleTypeLoader` vs a `TypeLoaderImpl` subclass

Both `SelectionOptions.typeLoader` and `LoadingOptions.typeLoader` accept a `TypeLoader` to map a schema type to a Java class:

- `SimpleTypeLoader(name1, Class1, name2, Class2, ...)` — a fixed name→class lookup table (see `qql-execution-from-java.md` for the `null`-name/anonymous-projection case). Use it when the set of type names to bind is known and static.
- A `TypeLoaderImpl` subclass overriding `load(ClassDescriptor)` — use when the mapping needs logic (conditionally choosing a class, falling back to a default for unknown types via `super.load(cd)`) rather than a static table:

  ```java
  LoadingOptions options = new LoadingOptions(false, LoadingOptions.WriteMode.REWRITE);
  options.typeLoader = new TypeLoaderImpl() {
      @Override
      public Class<?> load(ClassDescriptor cd) throws ClassNotFoundException {
          if (MY_CLASS_DESCRIPTOR.getName().equals(cd.getName())) {
              return MyMessage.class;
          }
          return super.load(cd); // fall back to default resolution
      }
  };
  ```

Do not claim every read path needs a custom decoder — bound mode with a matching POJO is simpler and should be preferred whenever a class is available.

## Stream creation

```java
import deltix.qsrv.hf.tickdb.pub.*;

StreamOptions options = StreamOptions.fixedType(
    StreamScope.DURABLE, streamKey, "Bar Messages Stream",
    0 /* distributionFactor */, descriptor);

DXTickStream stream = db.createStream(streamKey, options);
```

For streams carrying more than one message type, use `StreamOptions.polymorphic(scope, key, title, distributionFactor, descriptor1, descriptor2, ...)` instead of `fixedType`. See `stream-management.md` for the full comparison of stream-creation paths (including the two-step `createStream` + `setFixedType`/`setPolymorphic` form) and `StreamScope` choice.

## Polymorphic reads

For streams with multiple message types, branch on runtime type:

```java
while (cursor.next()) {
    InstrumentMessage msg = cursor.getMessage();
    if (msg instanceof BestBidOfferMessage) {
        // handle BBO
    } else if (msg instanceof BarMessage) {
        // handle bar
    }
}
```

Inspect schema before writing polymorphic logic. See [`examples/schema-introspection.md`](examples/schema-introspection.md).

## Common mistakes

- Assuming `@SchemaElement` is required for introspection — it isn't; add it only to override a name/title that would otherwise come from the Java field itself.
- Inventing `@SchemaElement` names without schema evidence.
- Using bound `InstrumentMessage` subclasses with `SelectionOptions.raw = true`, or vice versa.
- Forgetting `LoadingOptions(true, ...)`/`SelectionOptions.raw = true` for custom schemas without generated classes.
