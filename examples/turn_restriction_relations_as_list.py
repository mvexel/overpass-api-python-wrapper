#!/usr/bin/env python3

# Retrieves a list of turn restriction relations in Toronto.

import overpass

api = overpass.API()

turn_restrictions_query = "relation[type=restriction](area:3600324211)"

turn_restrictions_list = []

overpass_response = api.get(
    turn_restrictions_query,
    responseformat='csv(::"id",::"user",::"timestamp",restriction,"restriction:conditional")',
    verbosity='meta')

print(overpass_response)
