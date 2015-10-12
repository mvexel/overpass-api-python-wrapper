# -*- coding: utf-8 -*-
from os.path import exists

from click.testing import CliRunner

from overpass.cli import cli


def test_cli():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, [
            '--timeout', 30,
            '--endpoint', 'http://overpass-api.de/api/interpreter',
            'node(area:3602758138)[amenity=cafe]', 'out.geojson'
            ])
        assert result.exit_code == 0
        assert exists('out.geojson')


def test_cli_xml():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, [
            '--timeout', 30,
            '--endpoint', 'http://overpass-api.de/api/interpreter',
            '--format', 'osm',
            'node(area:3602758138)[amenity=cafe]', 'out.osm'
            ])
        assert result.exit_code == 0
        assert exists('out.osm')