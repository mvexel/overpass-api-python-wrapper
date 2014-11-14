import overpass


class TestAPI(object):

    def test_initialize_api(self):
        api = overpass.API()
        assert isinstance(api, overpass.API)
        assert api.debug is False
