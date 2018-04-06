import overpass


def test_initialize_api():
    api = overpass.API()
    assert isinstance(api, overpass.API)
    assert api.debug is False


def test_geojson():
    api = overpass.API(debug=True)

    MapQuery = overpass.MapQuery(37.86517, -122.31851, 37.86687, -122.31635)
    print MapQuery
    osm_geo = api.get(MapQuery)
    print osm_geo
    assert len(osm_geo['features']) > 1

    osm_geo = api.get('node(area:3602758138)[amenity=cafe]')
    assert len(osm_geo['features']) > 1

test_geojson()