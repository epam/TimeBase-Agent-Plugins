# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

import dxapi as tb
from dxapi import pandas_utils


def main():
    timebase = 'dxtick://localhost:8011'
    source_stream_key = 'Daily'
    target_stream_key = 'Daily_copy'
    # Open TimeBase in read-write mode
    with tb.TickDb.openFromUrl(timebase, False) as db:

        fields = ['open', 'close', 'high', 'low']
        symbols = ['IBM', 'AAPL']  # Use None for all symbols
        types = None  # Use None for all types

        # If native read_frame fails with NumPy array resize errors, see pandas-read-dicts.py.
        frame = pandas_utils.read_frame(
            db,
            streams=[source_stream_key],
            fields=fields,
            tickers=symbols,
            types=types,
            from_time_str='2001-01-01',
            to_time_str='2001-05-02',
        )

        # Write DataFrame to target stream
        binding = pandas_utils.bind_frame(db, target_stream_key, frame)
        pandas_utils.write_frame(db, binding, frame)
        print(f'Wrote {len(frame)} rows to {target_stream_key}')


if __name__ == '__main__':
    main()