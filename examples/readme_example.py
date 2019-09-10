#!/usr/bin/env python

# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

import overpass

api = overpass.API()
response = api.get('node["name"="Salt Lake City"]')
print(
    [(feature["id"], feature["properties"]["name"]) for feature in response["features"]]
)
