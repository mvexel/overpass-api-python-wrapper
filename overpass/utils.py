class Utils(object):

    @staticmethod
    def to_overpass_id(osmid, area=False):
        area_base = 2400000000
        relation_base = 3600000000
        if area:
            return int(osmid) + area_base
        return int(osmid) + relation_base
