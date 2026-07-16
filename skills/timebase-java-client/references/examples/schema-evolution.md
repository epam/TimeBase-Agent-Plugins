# Schema Evolution

**Type:** fragment, assumes a write-capable `DXTickDB` connection and an existing stream.

**When to use:** Changing the schema of an existing stream in place. See `schema-evolution.md` for when this applies and the background/synchronous distinction.

## Apply a schema change

```java
import deltix.qsrv.hf.tickdb.schema.*;
import deltix.qsrv.hf.tickdb.pub.task.SchemaChangeTask;

RecordClassSet in = new RecordClassSet();
in.addContentClasses(stream.getFixedType());

RecordClassSet out = new RecordClassSet();
out.addContentClasses(newDescriptor); // new RecordClassDescriptor with the desired fields

StreamMetaDataChange change = SchemaAnalyzer.DEFAULT.getChanges(
    in, MetaDataChange.ContentType.Fixed,
    out, MetaDataChange.ContentType.Fixed);

stream.execute(new SchemaChangeTask(change));
```

## Worked example 1: adding new fields (extend a message type)

```java
import deltix.timebase.api.SchemaElement;
import deltix.timebase.api.SchemaType;
import deltix.timebase.api.SchemaDataType;

@SchemaElement(title = "Extended Bar")
public class BarMessageEx extends BarMessage {
    protected int objectSize;

    @SchemaElement(name = "objectSize")
    @SchemaType(dataType = SchemaDataType.INTEGER, encoding = "INT32")
    public int getObjectSize() { return objectSize; }
    public void setObjectSize(int v) { objectSize = v; }
}
```

```java
RecordClassDescriptor currentDescriptor = stream.getFixedType();
RecordClassDescriptor extendedDescriptor = new RecordClassDescriptor(
    BarMessageEx.class.getName(), "Extended Bar", false,
    currentDescriptor, // parent — the new type extends the current one
    new NonStaticDataField("objectSize", "Object Size",
        new IntegerDataType(IntegerDataType.ENCODING_INT32, true))
);

RecordClassSet in = new RecordClassSet();
in.addContentClasses(currentDescriptor);
RecordClassSet out = new RecordClassSet();
out.addContentClasses(extendedDescriptor);

StreamMetaDataChange change = SchemaAnalyzer.DEFAULT.getChanges(
    in, MetaDataChange.ContentType.Fixed, out, MetaDataChange.ContentType.Fixed);
stream.execute(new SchemaChangeTask(change));
```

## Worked example 2: changing a field's encoding

```java
RecordClassDescriptor current = stream.getFixedType();
RecordClassDescriptor changed = new RecordClassDescriptor(
    current.getName(), current.getTitle(), false, current.getParent(),
    new NonStaticDataField("close", "Close", new FloatDataType(FloatDataType.ENCODING_FIXED_FLOAT, true))
    // ... redefine the other fields the same way, same names, new encoding ...
);

RecordClassSet in = new RecordClassSet();
in.addContentClasses(current);
RecordClassSet out = new RecordClassSet();
out.addContentClasses(changed);

StreamMetaDataChange change = SchemaAnalyzer.DEFAULT.getChanges(
    in, MetaDataChange.ContentType.Fixed, out, MetaDataChange.ContentType.Fixed);
stream.execute(new SchemaChangeTask(change));
```

## Walking a schema recursively (for inspection/debugging)

```java
void printClassDescriptor(RecordClassDescriptor cd) {
    if (cd.getParent() != null) {
        printClassDescriptor(cd.getParent()); // print inherited fields first
    }
    for (DataField field : cd.getFields()) {
        DataType type = field.getType();
        if (type instanceof ClassDataType) {
            ClassDataType cdt = (ClassDataType) type;
            for (RecordClassDescriptor nested : cdt.isFixed()
                    ? new RecordClassDescriptor[]{cdt.getFixedDescriptor()}
                    : cdt.getDescriptors()) {
                printClassDescriptor(nested); // recurse into nested/polymorphic object fields
            }
        } else if (type instanceof ArrayDataType) {
            // recurse into ((ArrayDataType) type).getElementDataType()
        } else if (type instanceof EnumDataType) {
            // ((EnumDataType) type).getDescriptor().getValues() for the enum's symbol/value pairs
        }
    }
}
```
