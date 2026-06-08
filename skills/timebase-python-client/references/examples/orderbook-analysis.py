# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

from datetime import datetime, timezone

import dxapi as tb
from dxapi import pandas_utils


def epoch_ms(value):
    return int(datetime.fromisoformat(value).astimezone(timezone.utc).timestamp() * 1000)


def main():
    timebase = 'dxtick://localhost:8102'
    stream_key = 'KRAKEN_TEST'
    symbol = 'BTC/USDT'
    depth = 5
    from_time = '2024-01-12T08:13:27+00:00'

    ts = epoch_ms(from_time)

    query = f'''
WITH
    orderbook{{maxDepth: {depth}}}(this.packageType, this.entries) AS book
SELECT RUNNING
    book_entry.exchangeId AS 'exchangeId',
    book_entry.price AS 'price',
    book_entry.size AS 'size',
    book_entry.level AS 'level',
    book_entry.side AS 'side'
FROM "{stream_key}"
ARRAY JOIN (book AS array(L2EntryNew)) AS book_entry
WHERE symbol == '{symbol}' AND timestamp > {ts}
GROUP BY symbol
'''

    # Open TimeBase in read-only mode
    with tb.TickDb.openFromUrl(timebase, True) as db:

        # pandas_utils does not flatten nested order book entries directly,
        # so use QQL to project them into a rectangular result first.
        fields = ['exchangeId', 'price', 'size', 'level', 'side']
        # If native read_frame fails with NumPy array resize errors, see pandas-read-dicts.py.
        frame = pandas_utils.read_frame(db, query=query, fields=fields)

    print(frame.head())
    frame.to_csv('orderbook_flat.csv', index=False)


if __name__ == '__main__':
    main()