import pytest

from overpass import utils

PARAM_OVERPASS_ID = ((1, True, 2400000001),
                     (1, False, 3600000001))


@pytest.mark.parametrize('osmid, area, expected', PARAM_OVERPASS_ID)
def test_overpass_id(osmid, area, expected):
    assert utils.Utils.to_overpass_id(osmid, area) == expected
