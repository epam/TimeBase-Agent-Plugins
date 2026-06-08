# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

import matplotlib.pyplot as plt

import dxapi as tb
from dxapi import pandas_utils


def main():
    timebase = 'dxtick://localhost:8011'
    # Open TimeBase in read-only mode
    with tb.TickDb.openFromUrl(timebase, True) as db:

        # If native read_frame fails with NumPy array resize errors, see pandas-read-dicts.py.
        frame = pandas_utils.read_frame(
            db,
            streams=['Daily'],
            fields=['close'],
            tickers=['AAPL'],
            types=None,
            from_time_str='2001-01-01',
            to_time_str='2001-03-01',
        )

    frame = frame.sort_values('timestamp')
    frame.plot(x='timestamp', y='close', legend=False, title='AAPL close')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()