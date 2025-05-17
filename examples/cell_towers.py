#!/bin/env python

# Retrieves a list of cell towers for a named area.

import overpass
api = overpass.API(debug=False)

import sys
pos=sys.argv[1]
rad=sys.argv[2]

# query = 'node["tower:type"=communication]around(around:1234,61,23)'
# query = 'node[man_made=mast](around:12345,61,23)'
query = 'node[man_made=mast](around:{},{})'.format(rad,pos)
print(query, file=sys.stderr)
# exit(0)

# result = api.Get(query, responseformat="csv(::towers)", verbosity="meta")
# result = api.Get(query, responseformat="json(::towers)", verbosity="meta")
result = api.Get(query, responseformat="json")
import json
print(json.dumps(result))
exit(0)

towers = {"type": []}
del result[0]  # header
for row in result:
    uid = int(row[0])
    username = row[1]
    if uid in towers["type"]:
        continue
    towers["type"].append(uid)
print(towers)
