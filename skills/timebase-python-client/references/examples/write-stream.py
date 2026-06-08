# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

import dxapi as tb


def create_stream(db, stream_key):
    schema = db.generateSchema(['deltix.timebase.api.messages.BarMessage'])

    options = tb.StreamOptions()
    options.schema(schema)

    stream = db.createStream(stream_key, options)
    print('Stream ' + stream_key + ' created')
    return stream


def main():
    # TimeBase URL specification, pattern is "dxtick://<host>:<port>"
    timebase = 'dxtick://localhost:8011'
    stream_key = 'bars_generated'
    # Open TimeBase in read-write mode
    with tb.TickDb.openFromUrl(timebase, False) as db:

        print('Connected to ' + timebase)

        # Get stream from the timebase
        stream = db.getStream(stream_key)
        if stream is None:
            stream = create_stream(db, stream_key)

        # Create a Message Loader for the selected stream and provide loading options
        with stream.tryLoader(tb.LoadingOptions()) as loader:
            bar_message = tb.InstrumentMessage()
            bar_message.typeName = 'deltix.timebase.api.messages.BarMessage'

            print('Start loading to ' + stream_key)

            for index in range(10):
                bar_message.instrumentType = 'EQUITY'
                bar_message.symbol = 'AAPL' if index % 2 == 0 else 'MSFT'
                bar_message.originalTimestamp = 0
                bar_message.currencyCode = 999
                bar_message.exchangeId = 'NYSE'
                bar_message.open = 10.0 + index * 2.2
                bar_message.close = 20.0 + index * 3.3
                bar_message.high = 30.0 + index * 4.4
                bar_message.low = 40.0 + index * 5.5
                bar_message.volume = 60.0 + index * 6.6
                loader.send(bar_message)


if __name__ == '__main__':
    main()