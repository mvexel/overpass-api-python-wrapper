#!/usr/bin/env python

# Copyright 2015-2018 Martijn van Exel.
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

# Retrieves a list of unique usernames and user IDs for a named area.

import overpass

# Change this to the name of the area you're interested in.
# Keep it small to not abuse the Overpass server.
area_name = "Kanab"

query = """area[name="{}"]->.a;(node(area.a);<;);""".format(area_name)
users = {"ids": [], "usernames": []}
message_urls = []
api = overpass.API(debug=False)
result = api.Get(query, responseformat="csv(::uid,::user)", verbosity="meta")
del result[0]  # header
for row in result:
    uid = int(row[0])
    username = row[1]
    if uid in users["ids"]:
        continue
    users["ids"].append(uid)
    users["usernames"].append(username)
    message_urls.append("https://www.openstreetmap.org/message/new/{}".format(username))
print(users)
print(message_urls)
