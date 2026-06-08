# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

import dxapi as tb
from dxapi import pandas_utils


def main():
    timebase = 'dxtick://localhost:8011'
    stream_key = 'Daily'
    # Open TimeBase in read-only mode
    with tb.TickDb.openFromUrl(timebase, True) as db:

        fields = ['open', 'close', 'high', 'low']
        symbols = ['IBM', 'AAPL']  # Use None for all symbols
        types = None  # Use None for all types

        # Use the Python-side fallback when native read_frame is unstable.
        frame = pandas_utils.read_frame_dicts(
            db,
            streams=[stream_key],
            fields=fields,
            tickers=symbols,
            types=types,
            from_time_str='2001-01-01',
            to_time_str='2001-05-02',
        )
        print(frame)


if __name__ == '__main__':
    main()