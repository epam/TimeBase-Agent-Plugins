# JSON Message Conversion

**Type:** fragment, assumes a write-capable `DXTickDB` connection and an existing `DXTickStream`.

**When to use:** Converting user-supplied JSON into a TimeBase message to write, or formatting an existing message back to JSON. See `json-message-conversion.md` for the details and pitfalls.

## JSON to message

```java
// Enterprise Edition example, Community Edition uses `JSONRawMessageParser` instead of `FastJsonRawMessageParser` and Gson instead of FastJSON
import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONObject;
import deltix.qsrv.hf.pub.RawMessage;
import deltix.qsrv.hf.tickdb.pub.*;
import deltix.qsrv.util.json.FastJsonRawMessageParser;

FastJsonRawMessageParser parser = new FastJsonRawMessageParser(stream.getTypes(), "type");

JSONObject jsonObject = JSON.parseObject(json); // json is one message object, e.g. {"type": "...", "symbol": "AAPL", "timestamp": "...", ...}
RawMessage msg = parser.parse(jsonObject);

try (TickLoader loader = stream.createLoader()) {
    loader.send(msg); // safe to send immediately, the loader consumes it before the next parse() call
}
```

## Message to JSON

```java
// Enterprise Edition example, Community Edition package root is `com.epam.deltix.qsrv.util.json` instead of `deltix.qsrv.util.json`
import deltix.qsrv.hf.pub.RawMessage;
import deltix.qsrv.util.json.JSONRawMessagePrinter;

RawMessage raw = ...; // e.g. from cursor.getMessage() with SelectionOptions.raw = true
StringBuilder sb = new StringBuilder();
new JSONRawMessagePrinter().append(raw, sb);
String json = sb.toString();
```
