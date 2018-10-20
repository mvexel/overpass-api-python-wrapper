#!/usr/bin/env python

# Author: Florian Winkler (Fju) 2018
# This file is part of the overpass-api-python-wrapper project
# which is licensed under Apache 2.0.
# See LICENSE.txt for the full license text.

import os
import xml.etree.ElementTree
import matplotlib.pyplot as plt
import numpy as np
import overpass

MAX_SIZE = 400
XML_FILE = 'state_border_saxony.xml'
QUERY = """area[name="Sachsen"][type="boundary"]->.saxony;
	rel(area.saxony)[admin_level=4][type="boundary"][boundary="administrative"];
	out geom;"""

# the query is can be quite big (multiple MB) so we save the servers response in a file
# that can be re-opened the next time
if not(os.path.isfile(XML_FILE)):
	# increase timeout because the response can be pretty heavy
	api = overpass.API(timeout=60)

	response = api.get(QUERY, responseformat="xml")

	# write xml file
	f = open(XML_FILE, 'w')
	# encode response in UTF-8 because name translation contain non-ascii characters
	f.write(response.encode('utf-8'))
	f.close()

	# free up memory
	#del response

# open xml file
root = xml.etree.ElementTree.parse(XML_FILE).getroot()

# bounds element contains information of the width and height
bounds = root.find('relation').find('bounds')
min_lat = float(bounds.get('minlat'))
min_lon = float(bounds.get('minlon'))
max_lat = float(bounds.get('maxlat'))
max_lon = float(bounds.get('maxlon'))

# longitude: east - west (x)
# latitude: north - south (y)
box_width = max_lon - min_lon
box_height = max_lat - min_lat

# compute scale factors so that the biggest distance is equal to `MAX_SIZE`
scale_x = int(MAX_SIZE * box_width / max(box_width, box_height))
scale_y = int(MAX_SIZE * box_height / max(box_width, box_height))

def outside(x1, y1, x2, y2, tolerance):
	# check if distance between two points is bigger than the given tolerance
	# since tolerance is a constant it doesn't have to be squared
	dx = x1 - x2
	dy = y1 - y2
	return (dx*dx + dy*dy) > tolerance


point_count = 0
# look through all `member` nodes
for member in root.iter('member'):
	m_type, m_role = member.get('type'), member.get('role')

	# check if the element belongs to the outer border
	if m_type == 'way' and m_role == 'outer':
		# `nd` elements contain lon and lat coordinates
		m_points = member.findall('nd')

		prev_x, prev_y = -1, -1

		index = 0
		for mp in m_points:
			x, y = float(mp.get('lon')), float(mp.get('lat'))

			# convert lon and lat coordinates to pixel coordinates
			x = (x - min_lon) / box_width * scale_x
			y = (y - min_lat) / box_height * scale_y

			if index == 0:
				# first point
				prev_x = x
				prev_y = y
			elif outside(x, y, prev_x, prev_y, 1) or index == len(m_points) - 1:
				# check if points are not too close to each other (too much detail) or if it's the last point of the section
				# if the last point was ignored, there would be holes

				# draw line from current point to previous point
				plt.plot([x, prev_x], [y, prev_y], 'k-')
				point_count += 1
				# save coordinates
				prev_x = x
				prev_y = y

			index += 1

print(point_count)
# show plot
plt.show()
