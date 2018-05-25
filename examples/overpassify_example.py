#!/usr/bin/env python

# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

"""An as yet not working example of using overpassify."""

import overpass
from overpassify import overpassify

api = overpass.API()


@api.Get
@overpassify
def response():
    Settings(timeout=1400)
    search = Area(3600134503) + Area(3600134502)
    ways = Way(
        search,
        maxspeed=None,
        highway=NotRegex("cycleway|footway|path|service"),
        access=NotRegex("private"),
    )
    out(ways, body=True, geom=True, qt=True)
    noop()


print(response)
