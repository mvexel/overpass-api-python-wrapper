# -*- coding: utf-8 -*-
from os.path import exists
from click.testing import CliRunner
from overpass.cli import cli
from nose.tools import nottest

def test_cli():
    
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, [
            'node(40.704,-74.010,40.708,-74.013)[amenity=cafe]'])
        assert result.exit_code == 0

def test_cli_xml():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, [
            '--responseformat', 'osm',
            'node(40.704,-74.010,40.708,-74.013)[amenity=cafe]'])
        assert result.exit_code == 0
