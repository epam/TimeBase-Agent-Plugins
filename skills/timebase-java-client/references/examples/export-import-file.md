# Export/Import File Archives

**Type:** fragment, assumes a write-capable `DXTickDB` connection.

**When to use:** Bulk-exporting a stream to a local file or archive, or importing one back. See [`import-export.md`](../import-export.md) for when this workflow applies.

## Creating a new stream from a file's own schema

```java
MessageFileHeader header = Protocol.readHeader(file);
RecordClassDescriptor[] types = header.getTypes();

RecordClassSet set = new RecordClassSet();
for (RecordClassDescriptor type : types) {
    set.addContentClasses(type);
}

StreamOptions options = new StreamOptions();
options.name = streamName;
options.setMetaData(set.getContentClasses().length > 1, set);
DXTickStream stream = db.createStream(streamName, options);
```

## Export to a single message file

`MessageWriter2.create(...)` declares both `IOException` and `ClassNotFoundException`, declare or catch both.

```java
import deltix.qsrv.hf.stream.MessageWriter2;
import deltix.qsrv.hf.pub.RawMessage;

void exportToFile(DXTickStream stream, File file) throws IOException, ClassNotFoundException {
    RecordClassDescriptor[] descriptors = stream.isFixedType()
        ? new RecordClassDescriptor[] { stream.getFixedType() }
        : stream.getPolymorphicDescriptors();

    SelectionOptions options = new SelectionOptions(true, false); // raw, not live
    MessageWriter2 writer = MessageWriter2.create(file, null, null, descriptors);

    try (InstrumentMessageSource source = stream.select(Long.MIN_VALUE, options)) {
        while (source.next()) {
            writer.send((RawMessage) source.getMessage());
        }
    } finally {
        writer.close();
    }
}
```

## Export to a per-space zip archive

The `MessageWriter2` constructor also declares both `IOException` and `ClassNotFoundException`.

```java
void exportToArchive(DXTickStream stream, RecordClassDescriptor[] descriptors, File file) throws IOException, ClassNotFoundException {
    try (ZipOutputStream zip = new ZipOutputStream(new FileOutputStream(file))) {
        for (String space : stream.listSpaces()) {
            zip.putNextEntry(new ZipEntry(SimpleStringCodec.DEFAULT_INSTANCE.encode(space) + ".qsmsg"));
            GZIPOutputStream gz = new GZIPOutputStream(zip);

            MessageWriter2 writer = new MessageWriter2(gz, null, null, descriptors);
            SelectionOptions options = new SelectionOptions(true, false);
            options.withSpace(space);

            try (InstrumentMessageSource source = stream.select(Long.MIN_VALUE, options)) {
                while (source.next()) {
                    writer.send((RawMessage) source.getMessage());
                }
            } finally {
                writer.flush(); // do not close the writer, it wraps a shared zip stream
                gz.finish();
                zip.closeEntry();
            }
        }
    }
}
```

## Import, with schema mapping between the file's types and the target stream's types

`SchemaUpdater`/`ClassMappings` below are Enterprise Edition only, see [`import-export.md`](../import-export.md) for what to do instead on Community Edition.

```java
import deltix.qsrv.hf.tickdb.schema.*;
import deltix.qsrv.hf.pub.md.SchemaUpdater;
import deltix.timebase.api.ClassMappings;

RecordClassDescriptor[] outTypes = stream.isFixedType()
    ? new RecordClassDescriptor[] { stream.getFixedType() }
    : stream.getPolymorphicDescriptors();

MessageFileHeader header = Protocol.readHeader(file);
RecordClassDescriptor[] inTypes = header.getTypes();

SchemaUpdater updater = new SchemaUpdater(new ClassMappings());
SchemaMapping mapping = updater.buildMapping(null, inTypes, outTypes);

// Find the current stream type that corresponds to a given file type, honoring
// any rename recorded in ClassMappings, without this the converter would map a
// type to itself and never actually bridge a schema change.
ClassMappings classMappings = new ClassMappings();
RecordClassDescriptor findOutType(RecordClassDescriptor fileType) {
    String renamedTo = classMappings.getClassName(fileType.getName());
    for (RecordClassDescriptor candidate : outTypes) {
        if (fileType.getName().equals(candidate.getName())
                || (renamedTo != null && renamedTo.equals(candidate.getName()))) {
            return candidate;
        }
    }
    return null;
}

LoadingOptions loadingOptions = new LoadingOptions(true, LoadingOptions.WriteMode.INSERT);

try (TickLoader loader = stream.createLoader(loadingOptions);
     ConsumableMessageSource<InstrumentMessage> reader = MessageReader2.createRaw(file)) {

    SchemaAnalyzer analyzer = new SchemaAnalyzer(mapping);
    Map<RecordClassDescriptor, SchemaConverter> converters = new HashMap<>();

    while (reader.next()) {
        RawMessage message = (RawMessage) reader.getMessage();
        SchemaConverter converter = converters.computeIfAbsent(message.type, fileType -> {
            RecordClassDescriptor outType = findOutType(fileType);
            if (outType == null) {
                return null;
            }
            MetaDataChange change = analyzer.getChanges(
                new RecordClassSet(new RecordClassDescriptor[]{fileType}), MetaDataChange.ContentType.Fixed,
                new RecordClassSet(new RecordClassDescriptor[]{outType}), MetaDataChange.ContentType.Fixed);
            return new SchemaConverter(change);
        });
        
        if (converter != null) {
            loader.send(converter.convert(message));
        }
    }
}
```
