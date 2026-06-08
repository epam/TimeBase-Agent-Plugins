# Enterprise default imports; replace dxapi with dxapi_ce for Community Edition.

import dxapi as tb


def main():
    # TimeBase URL specification, pattern is "dxtick://<host>:<port>"
    timebase = 'dxtick://localhost:8011'
    # Open TimeBase in read-only mode
    with tb.TickDb.openFromUrl(timebase, True) as db:
        print('Connected to ' + timebase)

        streams = db.listStreams()
        for stream in streams:
            options = stream.options()
            print(stream.key())
            print('   Name: ' + str(options.name()))
            print('   Scope: ' + str(options.scope))
            print('   DF: ' + str(options.distributionFactor))
            print('   Description: ' + str(options.description()))

if __name__ == '__main__':
    main()