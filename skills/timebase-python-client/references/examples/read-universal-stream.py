# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

from datetime import datetime

import dxapi as tb


def main():
    # TimeBase URL specification, pattern is "dxtick://<host>:<port>"
    timebase = 'dxtick://localhost:8011'
    stream_key = 'universal'
    # Open TimeBase in read-only mode
    with tb.TickDb.openFromUrl(timebase, True) as db:

        print('Connected to ' + timebase)

        # Get stream from the timebase
        stream = db.getStream(stream_key)
        if stream is None:
            raise Exception('Stream ' + stream_key + ' not found, please create the stream first')

        with stream.trySelect(0, tb.SelectionOptions(), None, None) as cursor:
            for _ in range(20):
                if not cursor.next():
                    break

                message = cursor.getMessage()
                message_time = datetime.utcfromtimestamp(message.timestamp / 1e9)
                if message.typeName != 'deltix.timebase.api.messages.universal.PackageHeader':
                    continue

                print('================================================')
                print(
                    'PackageHeader timestamp: '
                    + str(message_time)
                    + ', symbol: '
                    + message.symbol
                    + ', package type: '
                    + str(message.packageType)
                )

                for entry in message.entries:
                    if entry.typeName == 'deltix.timebase.api.messages.universal.L2EntryNew':
                        print(
                            'NEW: '
                            + str(entry.level)
                            + ': '
                            + str(entry.side)
                            + ' '
                            + str(entry.size)
                            + ' @ '
                            + str(entry.price)
                            + ' ('
                            + str(entry.exchangeId)
                            + ')'
                        )
                    elif entry.typeName == 'deltix.timebase.api.messages.universal.L2EntryUpdate':
                        print(
                            'UPDATE ['
                            + str(entry.action)
                            + ']: '
                            + str(entry.level)
                            + ': '
                            + str(entry.side)
                            + ' '
                            + str(entry.size)
                            + ' @ '
                            + str(entry.price)
                            + ' ('
                            + str(entry.exchangeId)
                            + ')'
                        )
                    elif entry.typeName == 'deltix.timebase.api.messages.universal.L1Entry':
                        print(
                            'L1Entry: '
                            + str(entry.side)
                            + ' '
                            + str(entry.size)
                            + ' @ '
                            + str(entry.price)
                            + ' ('
                            + str(entry.exchangeId)
                            + ')'
                        )
                    elif entry.typeName == 'deltix.timebase.api.messages.universal.TradeEntry':
                        print(
                            'Trade: '
                            + str(entry.side)
                            + ' '
                            + str(entry.size)
                            + ' @ '
                            + str(entry.price)
                            + ' ('
                            + str(entry.exchangeId)
                            + ')'
                        )

if __name__ == '__main__':
    main()