# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

import calendar
from datetime import datetime

import dxapi as tb


def main():
    # TimeBase URL specification, pattern is "dxtick://<host>:<port>"
    timebase = 'dxtick://localhost:8011'
    stream_key = 'trade_bbo'
    # Open TimeBase in read-only mode
    with tb.TickDb.openFromUrl(timebase, True) as db:

        print('Connected to ' + timebase)

        # Get stream from the timebase
        stream = db.getStream(stream_key)
        if stream is None:
            raise Exception('Stream ' + stream_key + ' not found, please, create stream')

        entities = [
            tb.InstrumentIdentity(tb.InstrumentType.BOND, 'USGG5YR'),
            tb.InstrumentIdentity(tb.InstrumentType.EQUITY, 'AAPL'),
        ]

        types = [
            'deltix.timebase.api.messages.TradeMessage',
            'deltix.timebase.api.messages.BestBidOfferMessage',
        ]

        # Define subscription start time
        start = datetime(2010, 1, 1, 0, 0)
        start_time = calendar.timegm(start.timetuple()) * 1000

        with stream.trySelect(start_time, tb.SelectionOptions(), types, entities) as cursor:
            while cursor.next():
                message = cursor.getMessage()
                print(message.typeName, message.symbol)


if __name__ == '__main__':
    main()