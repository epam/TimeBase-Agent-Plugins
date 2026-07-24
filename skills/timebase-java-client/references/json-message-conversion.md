# JSON Message Conversion

Use this reference when the task needs to convert between arbitrary JSON and a TimeBase message, in either direction.

## JSON to message

Construct the JSON parser class directly from the target `RecordClassDescriptor[]` (e.g. `stream.getTypes()`) and call `.parse(jsonObject)` to get a `RawMessage` back, then hand it to whatever loader the caller already has, one message at a time, a batch, after inspection/filtering, whatever fits.

```java
FastJsonRawMessageParser parser = new FastJsonRawMessageParser(stream.getTypes(), "type"); // "type" is the default type-discriminator property name
RawMessage msg = parser.parse(jsonObject);
loader.send(msg);
```

See [`examples/json-message-conversion.md`](examples/json-message-conversion.md).

**Important**: `parse(...)` returns a reused internal buffer, valid only until the next `parse()` call on the same parser instance. Clone it before storing it anywhere, or sending it through a loader immediately is also safe since the loader consumes it before the next `parse()` call.

`JSONHelper.parseAndLoad(String jsonArray, DXTickStream stream)` is a narrower convenience wrapper: it parses a whole JSON array and writes every message straight into one specific stream via its own internally-created `TickLoader`, with no way to inspect, filter, or reuse an existing loader. Only reach for it when the entire use case really is "load this whole array into this one stream," nothing more.

## Message to JSON

`JSONRawMessagePrinter` is the inverse operation, format a `RawMessage` to a JSON string:

```java
RawMessage raw = ...;
StringBuilder sb = new StringBuilder();
new JSONRawMessagePrinter().append(raw, sb);
System.out.println(sb.toString());
```

## Caller-facing details

- `symbol` and `timestamp` (plus `instrumentType` on Enterprise Edition, `nanoTime` on Community Edition) are read as reserved top-level JSON properties before generic field dispatch, a real schema field sharing one of those names would collide. `timestamp` must be a parseable timestamp string, not an arbitrary format.
- The type-discriminator property name must match what the parser was constructed with. For a polymorphic stream, every JSON object needs that property naming its fully qualified schema type so the parser can resolve the concrete `RecordClassDescriptor`.

## Package roots

`JSONHelper`, `JSONRawMessagePrinter`, and their package root follow the usual mechanical swap (`deltix.qsrv.util.json` on Enterprise Edition, `com.epam.deltix.qsrv.util.json` on Community Edition). The parser class itself is a genuine non-mechanical exception: Enterprise Edition's is `FastJsonRawMessageParser` (built on `com.alibaba.fastjson2`, `JSONObject`/`JSONArray`), Community Edition's is `JSONRawMessageParser` (built on Gson, `JsonObject`/`JsonArray`), different class name and constructor input type, not just a renamed package. Community Edition's parser also has no `parseCopy(...)` convenience method, use `RawMessage.clone()` there instead when retaining a parsed message.

## Common mistakes

- Storing the `RawMessage` returned by `parse(...)` without cloning it first, it's a reused buffer that gets overwritten on the next `parse()` call.
- Reaching for `JSONHelper.parseAndLoad` when per-message control is actually needed, construct the parser class directly instead.
- Letting a real schema field collide with a reserved top-level property name (`symbol`, `timestamp`, `instrumentType`, `nanoTime`, the type discriminator).
- Assuming the type-discriminator property name is always `"$type"`, it defaults to `"type"` on the parser class itself, `"$type"` is only what `JSONHelper` happens to configure internally.
