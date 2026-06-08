# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

import dxapi as tb


def print_schema(stream):
    print(f'Schema of {stream.key()}')
    print('----------------------')

    schema = stream.metadata()
    for message_type in schema.types:
        parent = f' parent: {message_type.parent};' if message_type.parent is not None else ''
        print(f'Type: {message_type.name};{parent}')
        for field in message_type.fields:
            field_type = field.type
            encoding = field_type.encoding if field_type.encoding is not None else ''
            nullable = 'NOT NULL' if not field_type.nullable else ''
            print(f'    field: {field.name} {field_type.name} {encoding} {nullable}')

    print('----------------------')


def main():
    # TimeBase URL specification, pattern is "dxtick://<host>:<port>"
    timebase = 'dxtick://localhost:8011'

    # Open TimeBase in read-only mode
    with tb.TickDb.openFromUrl(timebase, True) as db:
        print('Connected to ' + timebase)

        streams = db.listStreams()
        for stream in streams:
            print_schema(stream)


if __name__ == '__main__':
    main()