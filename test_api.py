import Overpass


class TestAPI:

    def test_initialize_api(self):
        api = Overpass.API()
        assert isinstance(api, Overpass.API)
        assert api.debug == False