import overpass


def test_initialize_api():
    api = overpass.API()
    assert isinstance(api, overpass.API)
    assert api.debug is False


def test_geojson():
    api = overpass.API()

    osm_geo = api.Get(
        overpass.MapQuery(37.86517, -122.31851, 37.86687, -122.31635),
        asGeoJSON=True
        )
    assert len(osm_geo['features']) > 1

    osm_geo = api.Get('node(area:3602758138)[amenity=cafe]',
        asGeoJSON=True
        )
    assert len(osm_geo['features']) > 1
