# Array Fields And Custom Codecs

**Type:** fragment, assumes a custom (raw) schema with an array-typed field.

**When to use:** Encoding/decoding an array-typed field in a custom schema, or writing a generic debug-print helper over raw fields. See `array-fields-and-codecs.md` for the rationale.

## Schema: an array field

```java
new NonStaticDataField("prices", "Prices",
    new ArrayDataType(true, new FloatDataType(FloatDataType.ENCODING_FIXED_DOUBLE, true)))
```

## Writing an array field (raw encode)

```java
encoder.nextField(); // positions the encoder at the array field
DataType type = encoder.getField().getType();
writeArray(values, (ArrayDataType) type, encoder);

void writeArray(double[] values, ArrayDataType type, WritableValue uenc) {
    uenc.setArrayLength(values.length);
    for (double v : values) {
        if (Double.isNaN(v) && type.getElementDataType().isNullable()) {
            continue; // skip nulls in a nullable array element type
        }
        uenc.nextWritableElement().writeDouble(v);
    }
}
```

The same pattern applies to `long[]` (skip `IntegerDataType.INT64_NULL` instead of `NaN`) or any other element type.

## Reading an array field (raw decode)

```java
while (decoder.nextField()) {
    DataType type = decoder.getField().getType();
    if (type instanceof ArrayDataType) {
        int len = decoder.getArrayLength();
        for (int i = 0; i < len; i++) {
            ReadableValue element = decoder.nextReadableElement();
            double v = element.getDouble(); // or getLong(), getString(), etc. based on element type
        }
    }
}
```

## A reusable debug-print helper for raw fields (including arrays and nested objects)

```java
// Generic: dump all field/value pairs of a (possibly nested) object.
static String toString(ReadableValue udec) {
    UnboundDecoder decoder = udec.getFieldDecoder(); // steps into the nested object's own field decoder
    StringBuilder sb = new StringBuilder(decoder.getClassInfo().getDescriptor().getName()).append(":[");
    while (decoder.nextField()) {
        sb.append(decoder.getField().getName()).append('=');
        try {
            sb.append(decoder.getString());
        } catch (NullValueException e) {
            sb.append("null");
        }
        sb.append(',');
    }
    return sb.append(']').toString();
}

// Array-specific: dump each element, recursing into toString(ReadableValue) for nested-object elements.
static String toString(ArrayDataType type, ReadableValue udec) {
    StringBuilder sb = new StringBuilder("[");
    int len = udec.getArrayLength();
    DataType elementType = type.getElementDataType();

    for (int i = 0; i < len; i++) {
        ReadableValue rv = udec.nextReadableElement();
        if (elementType instanceof FloatDataType) sb.append(rv.getDouble());
        else if (elementType instanceof IntegerDataType) sb.append(rv.getLong());
        else if (elementType instanceof ClassDataType) sb.append(toString(rv)); // recurse into nested object
        sb.append(',');
    }
    return sb.append(']').toString();
}
```
