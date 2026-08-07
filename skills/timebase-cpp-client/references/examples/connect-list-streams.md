# Connect And List Streams

```cpp
#include <dxapi/dxapi.h>
using namespace DxApi;

std::unique_ptr<TickDb> db(TickDb::createFromUrl("dxtick://localhost:8011"));
db->open(/* readOnlyMode */ true);

std::vector<TickStream *> streams = db->listStreams();
for (TickStream *stream : streams) {
    std::cout << stream->key() << " " << stream->name().get() << std::endl;
}

db->close();
```

See `connection-and-lifecycle.md` for connection URI schemes and auth, `stream-management.md` for `key()`/`name()` and other `TickStream` operations.
