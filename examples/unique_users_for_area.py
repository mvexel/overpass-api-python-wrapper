#!/usr/bin/env python

# Retrieves a list of unique usernames and user IDs for a named area.

import overpass

area_name = "Kanab"

query = """area[name="{}"]->.slc;(node(area.slc);<;);""".format(area_name)

users = {"ids": [], "usernames": []}
api = overpass.API(debug=False)
result = api.Get(
    query,
    responseformat="csv(::uid,::user)",
    verbosity="meta")
del result[0]  # header
for row in result:
    uid = int(row[0])
    username = row[1]
    if uid in users["ids"]:
        continue
    users["ids"].append(uid)
    users["usernames"].append(username)
print(users)
