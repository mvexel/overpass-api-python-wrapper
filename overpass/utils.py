# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.


class Utils(object):

    @staticmethod
    def to_overpass_id(osmid: int, source: str = "relation") -> int:
        """Return the derived area id for a way or relation.

        Note: area ids are derived and not all ways/relations have a valid area.
        Prefer Overpass QL constructs like map_to_area/is_in when possible.
        """
        area_base = 2400000000
        relation_base = 3600000000

        if source == "way":
            return int(osmid) + area_base
        if source == "relation":
            return int(osmid) + relation_base

        raise ValueError("source must be 'way' or 'relation'")
