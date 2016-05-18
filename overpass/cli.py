# -*- coding: utf-8 -*-
from __future__ import print_function
import click
import geojson
import sys
import overpass


@click.command()
@click.option('--timeout', default=25, help='Timeout in seconds (default: 25).')
@click.option('--endpoint', default='http://overpass-api.de/api/interpreter',
    help='URL of your prefered API.')
@click.option('--responseformat', type=click.Choice(overpass.API.SUPPORTED_FORMATS), default='geojson',
        help="Required output format.")
@click.argument('query', type=str)
def cli(timeout, endpoint, responseformat, query):
    """Run query"""
    api = overpass.API(timeout=timeout, endpoint=endpoint)
    result = api.Get(query, responseformat=responseformat)
    click.echo(result)