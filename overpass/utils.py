# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.


class Utils(object):

    @staticmethod
    def to_overpass_id(osmid, area=False):
        if area:
            area_base = 2400000000
            return int(osmid) + area_base
        relation_base = 3600000000
        return int(osmid) + relation_base
