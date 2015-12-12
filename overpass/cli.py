# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import geojson

import overpass


@click.command()
@click.option('--timeout', default=25, help='Timeout in seconds.')
@click.option('--endpoint', default='http://overpass-api.de/api/interpreter',
    help='URL of your prefered API.')
@click.option('--format', default='geojson', help="""Format to save the data.
    Options are 'geojson' and 'osm'. Default format is geojson.""")
@click.argument('query', type=str)
@click.argument('output_file', type=click.Path())
def cli(timeout, endpoint, format, query, output_file):
    """Run query and save the result in output_file"""

    api = overpass.API(timeout=timeout, endpoint=endpoint)
    if format == 'geojson':
        result = api.Get(query, asGeoJSON=True)
        with open(output_file, 'w') as f:
            geojson.dump(result, f, indent=2, sort_keys=True)
        print('File saved at %s.' % output_file)
    elif format == 'osm':
        result = api.Get(query, asGeoJSON=False)
        with open(output_file, 'wb') as f:
            f.write(result.encode('utf-8'))
            f.close()
        print('File saved at %s.' % output_file)
    else:
        print('The format you typed is not supported.')
