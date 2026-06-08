# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

import dxapi as tb


def main():
    # TimeBase URL specification, pattern is "dxtick://<host>:<port>"
    timebase = 'dxtick://localhost:8011'
    stream_key = '1min.bars'
    # Open TimeBase in read-only mode
    with tb.TickDb.openFromUrl(timebase, True) as db:

        print('Connected to ' + timebase)

        # Define query
        query = f'select * from "{stream_key}" where volume > MIN_VOLUME'

        # Execute query with parameter 200
        with db.tryExecuteQuery(
            query=query,
            options=tb.SelectionOptions(),
            params=[tb.QueryParameter('MIN_VOLUME', 'INT64', '200')],
        ) as cursor:
            while cursor.next():
                print(cursor.getMessage())

        # Execute query with parameter 1000
        with db.tryExecuteQuery(
            query=query,
            options=tb.SelectionOptions(),
            params=[tb.QueryParameter('MIN_VOLUME', 'INT64', '1000')],
        ) as cursor:
            while cursor.next():
                print(cursor.getMessage())


if __name__ == '__main__':
    main()