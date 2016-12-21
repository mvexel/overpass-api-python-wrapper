#!/usr/bin/env python3

import overpass

api = overpass.API()

# Turn restrictions in Toronto
turn_restrictions_query = "relation[type=restriction](area:3600324211)"

turn_restrictions_list = []

overpass_response = api.Get(
	turn_restrictions_query, 
	responseformat='csv(::"id",::"user",::"timestamp",restriction,"restriction:conditional")',
	verbosity='meta')

print(overpass_response)
#reader = csv.reader(response)
#turn_restrictions_list = list(reader)

for row in overpass_response.split('\n'):
	turn_restrictions_list.append([elem for elem in row.split('\t')])

print(turn_restrictions_list)