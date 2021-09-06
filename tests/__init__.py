import os

# Set temporary True to update example.json/example.response files with real overpass endpoint data
UPDATE_EXAMPLES = False

RESOURCE_PATH = os.path.join(os.path.dirname(os.path.abspath(os.path.relpath(__file__))), 'resources')


def save_resource(file_name, data):
    with open(os.path.join(RESOURCE_PATH, file_name), 'wb') as f:
        f.write(data)


def load_resource(file_name):
    with open(os.path.join(RESOURCE_PATH, file_name), 'rb') as f:
        result = f.read()
    return result


def update_examples():
    import pickle
    import geojson
    import overpass

    query = 'rel(6518385);out body geom;way(10322303);out body geom;node(4927326183);'
    api = overpass.API()
    osm_geo = api.get(query, verbosity='body geom')
    save_resource('example.response', pickle.dumps(api._get_from_overpass(f'[out:json];{query}out body geom;'),
                                                   protocol=2))
    save_resource('example.json', geojson.dumps(osm_geo).encode('utf8'))


if UPDATE_EXAMPLES:
    UPDATE_EXAMPLES = False
    update_examples()
