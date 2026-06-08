# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

import calendar
from datetime import datetime

import dxapi as tb


class PriceInfo:
    def __init__(self, symbol):
        self.symbol = symbol
        self.bid_price = float('nan')
        self.bid_size = 0
        self.offer_price = float('nan')
        self.offer_size = 0


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
            raise Exception('Stream ' + stream_key + ' not found, please create the stream first')

        options = tb.SelectionOptions()
        options.reverse = True

        types = ['deltix.timebase.api.messages.BestBidOfferMessage']

        # Define subscription start time
        start = datetime(2030, 1, 1, 0, 0)
        start_time = calendar.timegm(start.timetuple()) * 1000

        prices = {}
        with stream.trySelect(start_time, options, types, None) as cursor:
            while cursor.next():
                message = cursor.getMessage()

                latest = prices.get(message.symbol)
                if latest is None:
                    latest = PriceInfo(message.symbol)
                    prices[message.symbol] = latest

                latest.bid_price = message.bidPrice
                latest.bid_size = message.bidSize
                latest.offer_price = message.offerPrice
                latest.offer_size = message.offerSize

                cursor.removeSymbols([message.symbol])

        for symbol, latest in prices.items():
            print('Latest bidPrice [' + symbol + '] ' + str(latest.bid_price))
            print('Latest askPrice [' + symbol + '] ' + str(latest.offer_price))

if __name__ == '__main__':
    main()