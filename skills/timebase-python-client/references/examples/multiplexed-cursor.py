# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

import dxapi as tb


def main():
    # TimeBase URL specification, pattern is "dxtick://<host>:<port>"
    timebase = 'dxtick://localhost:8011'
    # Open TimeBase in read-only mode
    with tb.TickDb.openFromUrl(timebase, True) as db:

        print('Connected to ' + timebase)

        subscription = tb.MultiplexerSubscription()

        streams = [db.getStream('BINANCE'), db.getStream('KRAKEN')]
        if any(stream is None for stream in streams):
            raise Exception('BINANCE or KRAKEN stream not found, please create the streams first')

        entities = [
            tb.InstrumentIdentity(tb.InstrumentType.FX, 'BTC/USDT'),
            tb.InstrumentIdentity(tb.InstrumentType.FX, 'ETH/BTC'),
        ]

        subscription.subscribe_streams(
            streams=streams,
            timestamp=0,
            entities=entities,
            types=None,
        )
        subscription.subscribe_qql(qql='select * from "Bars1"')

        options = tb.SelectionOptions()
        options.reverse = False
        options.live = False

        # Create multiplexed cursor
        with db.tryMultiplexedCursor(subscription, options=options) as cursor:
            while cursor.next():
                message = cursor.getMessage()
                print(message)


if __name__ == '__main__':
    main()