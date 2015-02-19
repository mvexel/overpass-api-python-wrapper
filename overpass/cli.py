# -*- coding: utf-8 -*-
import click
import geojson

import overpass


@click.command()
@click.option('--timeout', default=25, help='Timeout in seconds')
@click.option('--endpoint', default='http://overpass-api.de/api/interpreter',
    help='URL of your prefered API')
@click.argument('query', type=str)
@click.argument('output_file', type=click.Path())
def cli(timeout, endpoint, query, output_file):
    """Run query and save the result in output_file"""

    api = overpass.API(timeout=timeout, endpoint=endpoint)
    result = api.Get(query, asGeoJSON=True)
    with open(output_file, 'w') as f:
        geojson.dump(result, f, indent=2, sort_keys=True)
