import geojson
import overpass

class TestAPI:

    def test_initialize_api(self):
        api = overpass.API()
        assert isinstance(api, overpass.API)
        assert api.debug == False

    def test_geojson(self):
        api = overpass.API()
        #osm_elements = api.Get(overpass.MapQuery(37.86517,-122.31851,37.86687,-122.31635))
        #print 'DEB osm_elements:', geojson.dumps(osm_elements,sort_keys=True,indent=2)
        osm_geo  = api.Get(overpass.MapQuery(37.86517,-122.31851,37.86687,-122.31635), asGeoJSON=True)
        #with open('test.geojson','w') as f:
        #    geojson.dump(osm_geo,f,indent=2,sort_keys=True)
        assert len(osm_geo['features'])>1

    def run_tests(self):
        self.test_initialize_api()
        self.test_geojson()

if __name__ == '__main__':
    tapi = TestAPI()
    tapi.run_tests()
    print "overpass PASS" 
