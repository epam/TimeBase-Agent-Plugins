# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

import calendar
from datetime import datetime

import dxapi as tb


def main():
    # TimeBase URL specification, pattern is "dxtick://<host>:<port>"
    timebase = 'dxtick://localhost:8011'
    stream_key = 'bars'
    # Open TimeBase in read-only mode
    with tb.TickDb.openFromUrl(timebase, True) as db:

        print('Connected to ' + timebase)

        # Get stream from the timebase
        stream = db.getStream(stream_key)
        if stream is None:
            raise Exception('Stream ' + stream_key + ' not found, please create the stream first')

        # List of message types to subscribe (if None, all stream types will be used)
        types = ['deltix.timebase.api.messages.BarMessage']

        # List of entities to subscribe (if None, all stream entities will be used)
        entities = [
            tb.InstrumentIdentity(tb.InstrumentType.EQUITY, 'MSFT'),
            tb.InstrumentIdentity(tb.InstrumentType.EQUITY, 'AAPL'),
        ]

        # Define subscription start time
        start = datetime(2010, 1, 1, 0, 0)
        start_time = calendar.timegm(start.timetuple()) * 1000

        # Create cursor using defined message types and entities
        with stream.trySelect(start_time, tb.SelectionOptions(), types, entities) as cursor:
            while cursor.next():
                message = cursor.getMessage()
                if message.typeName == 'deltix.timebase.api.messages.BarMessage':
                    print('Bar ' + message.symbol + ' close price: ' + str(message.close))

if __name__ == '__main__':
    main()