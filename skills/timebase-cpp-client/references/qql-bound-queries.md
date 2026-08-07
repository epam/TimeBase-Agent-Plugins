# Parameterized QQL

`TickDb::executeQuery` has overloads that accept `QueryParameter`s for parameterized QQL, and `compileQuery` for validating QQL text without executing it. There is no real usage anywhere available with a populated parameter vector or an inspected `compileQuery` result, treat any populated example as illustrative, not as a verified worked pattern.

## `QueryParameter`

```cpp
struct QueryParameter {
    std::string name;
    std::string type;             // base type as text, e.g. "STRING", "INTEGER"
    Nullable<std::string> value;

    QueryParameter(name, type, value);
    QueryParameter(name, type); // no value, e.g. for compileQuery-only usage
};
```

Ground the parameter names/types against the actual QQL text (from the QQL generator skill) rather than inventing them.

## `executeQuery` overloads

```cpp
TickCursor * executeQuery(const std::string &qql, const std::vector<QueryParameter> &params);
TickCursor * executeQuery(const std::string &qql, const SelectionOptions &options, const std::vector<QueryParameter> &params);
TickCursor * executeQuery(const std::string &qql, const SelectionOptions &options, TimestampMs time, const std::vector<QueryParameter> &params);
TickCursor * executeQuery(const std::string &qql, const SelectionOptions &options, TimestampMs time, const std::vector<std::string> *symbols, const std::vector<QueryParameter> &params);
TickCursor * executeQuery(const std::string &qql, const SelectionOptions &options, TimestampMs time, const std::vector<InstrumentIdentity> *instruments, const std::vector<QueryParameter> &params);
```

Pick the narrowest overload that already carries the constraints the task needs (time bound, symbol/instrument filter), rather than embedding those constraints in the QQL text when a dedicated parameter exists.

## `compileQuery`

```cpp
struct QueryToken {
    std::string type;
    int64_t location; // encoded span: bits 48-63 start line, 32-47 start column, 16-31 end line, 0-15 end column
};
```

`db->compileQuery(qql, tokens)` throws `DxApi::TickDbException` on invalid QQL (with an encoded error location), otherwise fills `tokens`. Use it to validate QQL text before executing it when the task needs early error feedback (e.g. checking user-supplied QQL), it doesn't return a cursor or execute anything.

See [`examples/qql-query-result.md`](examples/qql-query-result.md) for the full call patterns.
