# -*- coding: utf-8 -*-
from os.path import exists

from click.testing import CliRunner

from overpass.cli import cli


def test_cli():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli,
            ['--timeout', 30, 'node(area:3602758138)[amenity=cafe]', 'out.json']
            )
        assert result.exit_code == 0
        assert exists('out.json')