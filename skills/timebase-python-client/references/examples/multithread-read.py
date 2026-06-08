# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

import threading

import dxapi as tb


TIMEBASE = 'dxtick://localhost:8011'


def read_cursor(stream_key, start_time):
    # Open TimeBase in read-only mode
    with tb.TickDb.openFromUrl(TIMEBASE, True) as db:

        print('Connected to ' + TIMEBASE + ' for ' + stream_key)

        # Get stream from the timebase
        stream = db.getStream(stream_key)
        if stream is None:
            raise Exception('Stream ' + stream_key + ' not found, please create the stream first')

        options = tb.SelectionOptions()
        count = 0
        with stream.trySelect(start_time, options, None, None) as cursor:
            while cursor.next():
                message = cursor.getMessage()
                count += 1
                if count % 10 == 0:
                    print('Read ' + str(count) + ' messages from ' + stream_key)
                    print(str(message))


def main():
    thread_1 = threading.Thread(target=read_cursor, args=('trade_bbo', 0))
    thread_2 = threading.Thread(target=read_cursor, args=('universal', 0))

    thread_1.start()
    thread_2.start()

    thread_1.join()
    thread_2.join()


if __name__ == '__main__':
    main()