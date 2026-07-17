# Reconnect Handling

**Type:** fragment, assumes an open, writable `DXTickDB` connection, an existing `DXTickStream`, and a constructed `InstrumentMessage` to send.

**When to use:** The task needs to survive a mid-session disconnect from the TimeBase server, not just an initial connection failure.

```java
import deltix.qsrv.hf.pub.InstrumentMessage;
import deltix.qsrv.hf.spi.conn.DisconnectEventListener;
import deltix.qsrv.hf.spi.conn.Disconnectable;
import deltix.qsrv.hf.tickdb.pub.*;

public class ResilientWriter implements DisconnectEventListener {

    private final Object lock = new Object();
    private volatile boolean connected = true;

    public void run(DXTickStream stream, InstrumentMessage msg) throws InterruptedException {
        for (;;) {
            awaitConnected();

            try (TickLoader loader = stream.createLoader()) {
                for (;;) {
                    loader.send(msg);
                    Thread.sleep(1000);
                }
            } catch (Exception ex) {
                ex.printStackTrace(System.out);
                // loop back around: re-check connection state before retrying
            }
        }
    }

    private void awaitConnected() throws InterruptedException {
        synchronized (lock) {
            while (!connected) {
                lock.wait(5000);
            }
        }
    }

    @Override
    public void onDisconnected() {
        synchronized (lock) {
            connected = false;
            lock.notifyAll();
        }
    }

    @Override
    public void onReconnected() {
        synchronized (lock) {
            connected = true;
            lock.notifyAll();
        }
    }

    // db is an already-open, writable DXTickDB connection
    public static void wire(DXTickDB db, DXTickStream stream, InstrumentMessage msg) throws Exception {
        ResilientWriter writer = new ResilientWriter();
        ((Disconnectable) db).addDisconnectEventListener(writer);
        try {
            writer.run(stream, msg);
        } finally {
            ((Disconnectable) db).removeDisconnectEventListener(writer);
        }
    }
}
```

The core idea: block the write/read loop while disconnected instead of letting it spin or throw repeatedly, and resume once `onReconnected()` fires. Only reach for this when the task explicitly calls for a resilient long-running process.
