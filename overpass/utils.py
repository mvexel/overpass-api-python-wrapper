class Utils(object):

    @classmethod
    def to_overpass_id(self, osmid, area=False):
        AREA_BASE = 2400000000
        RELATION_BASE = 3600000000
        if area:
            return int(osmid) + AREA_BASE
        return int(osmid) + RELATION_BASE