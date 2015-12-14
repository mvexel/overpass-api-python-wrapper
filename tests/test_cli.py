# -*- coding: utf-8 -*-
from os.path import exists
from click.testing import CliRunner
from overpass.cli import cli
from nose.tools import nottest

#@nottest
def test_cli():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, [
            '--timeout', 40,
            '--endpoint', 'http://overpass-api.de/api/interpreter',
            'node(area:3600362504)[amenity=cafe]', 'out.geojson'
            ])
        assert result.exit_code == 0
        assert exists('out.geojson')

#@nottest
def test_cli_xml():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, [
            '--timeout', 40,
            '--endpoint', 'http://overpass-api.de/api/interpreter',
            '--responseformat', 'osm',
            'node(area:3600362504)[amenity=cafe]', 'out.osm'
            ])
        assert result.exit_code == 0
        assert exists('out.osm')