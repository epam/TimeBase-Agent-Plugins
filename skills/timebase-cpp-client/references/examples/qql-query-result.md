# Bound QQL Query Result

Illustrative only, see `qql-bound-queries.md` for the "no real usage exists" caveat.

```cpp
std::vector<QueryParameter> params = {
    QueryParameter("symbol", "STRING", "AAPL"),
};
std::unique_ptr<TickCursor> cursor(db->executeQuery(qql, params));
```

See `qql-bound-queries.md` for the full overload list and parameter-grounding rule.

## Validating QQL without executing it

```cpp
std::vector<QueryToken> tokens;
db->compileQuery(qql, tokens); // throws DxApi::TickDbException on invalid QQL, with an encoded error location
```

See `qql-bound-queries.md` for what `compileQuery` does and doesn't do.
