# Stream Spaces Read/Write

## Writing into a space

```cpp
LoadingOptions options;
options.writeMode = WriteMode::APPEND; // the default is REWRITE (destructive), always set this explicitly
options.space = "Hello";
std::unique_ptr<TickLoader> loader(stream->createLoader(options));
```

## Reading from spaces

```cpp
SelectionOptions options;
options.space = "Hello"; // single space
```

```cpp
SelectionOptions options;
std::vector<std::string> spaceList = {"Hello", "World"};
options.withSpaces(&spaceList); // multiple spaces at once
```

## Managing spaces

```cpp
std::vector<std::string> spaces = stream->listSpaces();

stream->renameSpace(newName, oldName);

stream->deleteSpaces({"Hello"}); // destructive, deletes all data in the named space(s)
```

See `stream-spaces.md` for the grounding and destructive-operation notes on these calls.

## Space-scoped time range

```cpp
TimestampMs range[2];
bool success = stream->getTimeRange(range, "Hello");
```
