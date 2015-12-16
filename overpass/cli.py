# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import geojson
import sys
import overpass


@click.command()
@click.option('--timeout', default=25, help='Timeout in seconds.')
@click.option('--endpoint', default='http://overpass-api.de/api/interpreter',
    help='URL of your prefered API.')
@click.option('--responseformat', default='geojson', help="""Format to save the data.
    Options are 'geojson' and 'osm'. Default format is geojson.""")
@click.argument('query', type=str)
def cli(timeout, endpoint, responseformat, query):
    """Run query"""
    api = overpass.API(timeout=timeout, endpoint=endpoint)
    if responseformat not in api.SUPPORTED_FORMATS:
        print("format {} not supported. Supported formats: {}".format(
            responseformat,
            ", ".join(api.SUPPORTED_FORMATS)))
        sys.exit(1)
    result = api.Get(query, responseformat=responseformat)
    click.echo(result)