import overpass

class TestAPI:

    def test_initialize_api(self):
        api = overpass.Api()
        assert isinstance(api, overpass.Api)
        assert api.debug == False
