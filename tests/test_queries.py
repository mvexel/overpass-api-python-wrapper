import pytest

from overpass import queries

PARAM_MAP_QUERY = ((1, 2, 3, 4, '(node(1,2,3,4);<;>;);'),
                   (4, 3, 2, 1, '(node(4,3,2,1);<;>;);'))

PARAM_WAY_QUERY = (('Alpha', '(wayAlpha);(._;>;);'), ('Beta', '(wayBeta);(._;>;);'))


@pytest.mark.parametrize('south, west, north, east, expected', PARAM_MAP_QUERY)
def test_map_query(south, west, north, east, expected):
    assert str(queries.MapQuery(south, west, north, east)) == expected


@pytest.mark.parametrize('query_parameters, expected', PARAM_WAY_QUERY)
def test_map_query(query_parameters, expected):
    assert str(queries.WayQuery(query_parameters)) == expected
