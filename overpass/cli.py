# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import geojson

import overpass


@click.command()
@click.option('--timeout', default=25, help='Timeout in seconds.')
@click.option('--endpoint', default='http://overpass-api.de/api/interpreter',
    help='URL of your prefered API.')
@click.option('--responseformat', default='geojson', help="""Format to save the data.
    Options are 'geojson' and 'osm'. Default format is geojson.""")
@click.argument('query', type=str)
@click.argument('output_file', type=click.Path())
def cli(timeout, endpoint, responseformat, query, output_file):
    """Run query and save the result in output_file"""

    api = overpass.API(timeout=timeout, endpoint=endpoint)

    if responseformat not in api.SUPPORTED_FORMATS:
        print("format {} not supported. Supported formats: {}".format(
            responseformat,
            api.SUPPORTED_FORMATS.join(", ")))
    result = api.Get(query, responseformat=responseformat)
    with open(output_file, 'w') as f:
        if responseformat=="geojson":
            geojson.dump(result, f, indent=2, sort_keys=True)
        else:
            f.write(result.encode('utf-8'))
        f.close()
    print('File saved at %s.' % output_file)