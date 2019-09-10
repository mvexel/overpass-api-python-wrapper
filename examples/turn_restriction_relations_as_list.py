#!/usr/bin/env python

# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

# Retrieves a list of turn restriction relations in Toronto.

import overpass

api = overpass.API()

turn_restrictions_query = "relation[type=restriction](area:3600324211)"

turn_restrictions_list = []

overpass_response = api.get(
    turn_restrictions_query,
    responseformat='csv(::"id",::"user",::"timestamp",restriction,"restriction:conditional")',
    verbosity="meta",
)

print(overpass_response)
