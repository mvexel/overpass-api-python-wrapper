# -*- coding: utf-8 -*-


class MapQuery(object):
    """Query to retrieve complete ways and relations in an area."""

    _QUERY_TEMPLATE = "(node({bbox[0]},{bbox[1]},{bbox[2]},{bbox[2]});<;);"

    def __init__(self, bbox):
        """
        Initialize query with given bounding box.
        :param bbox Bounding box with limit values in format (s, w, n, e) in a sequence.
        """
        self.bbox = bbox

    def __str__(self):
        return self._QUERY_TEMPLATE.format(bbox=self.bbox)


class WayQuery(object):
    """Query to retrieve a set of ways and their dependent nodes satisfying the input parameters"""

    _QUERY_TEMPLATE = "way{query_parameters};(_.;>;);"

    def __init__(self, query_parameters):
        """
        Initialize a query for a set of ways satisfying the given parameters.
        :param query_parameters Overpass QL query parameters
        """
        self.query_parameters = query_parameters

    def __str__(self):
        return self._QUERY_TEMPLATE.format(query_parameters=self.query_parameters)
