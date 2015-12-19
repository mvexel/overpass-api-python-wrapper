import overpass


def test_initialize_api():
    api = overpass.API()
    assert isinstance(api, overpass.API)
    assert api.debug is False


def test_geojson():
    api = overpass.API()

    osm_geo = api.Get(
        overpass.MapQuery(37.86517, -122.31851, 37.86687, -122.31635))
    assert len(osm_geo['features']) > 1

    osm_geo = api.Get('node(area:3602758138)[amenity=cafe]')
    assert len(osm_geo['features']) > 1

def test_map_call():
	api = overpass.API()
	map_xml = api.Map(-111.4023,40.7172,-111.3838,40.7266)
	assert map_xml.startswith('<?xml version="1.0" encoding="UTF-8"?>\n<osm version="0.6" generator="Overpass API">')