#!/usr/bin/env python3

import overpass
import json

api = overpass.API()

def mPrintCoordinatesFunc(mCoordinateList):
    for mCoordinateListItem in mCoordinateList:
    	print(mCoordinateListItem[0],mCoordinateListItem[1])

def mOVERPASSStateArea(mISO):
    # Tags for state query
    # ISO3166-2 = mCountry + mState
    # is_in:country_code = mCountry
    mQueryState = "relation['ISO3166-2'='" + mISO + "']"
    # print(mQueryState)
    overpass_response = api.Get(
        mQueryState
        ,responseformat='json'
        ,verbosity='ids')
    # My_File = open('state.json','x')
    # json.dump(overpass_response, My_File)
    # My_File.close()
    # print(overpass_response['elements'][0]['id'])
    return str(int(overpass_response['elements'][0]['id']) + 3600000000)

# ISO3166-1
mCountry = 'US'

# ANSI state code
mState = 'KS'

# Tags for city query
# admin_level
# border_type = city
# name
# place = city
# type = boundary
mCity = 'Wichita'

mQueryCity = ("relation['type'='boundary']['boundary'='administrative']" 
    + "['name'='" + mCity + "']"
    + "(area:" + mOVERPASSStateArea(mCountry + "-" + mState) + ");"
    + "way(r);"
    )

#print(mQueryCity)

overpass_response = api.Get(
    mQueryCity
    ,responseformat='geojson'
    ,verbosity='geom')

mFeaturesList_of_Dict = overpass_response['features']
# mFeaturesList_of_Dict is list
for mListItem in mFeaturesList_of_Dict:
	mPrintCoordinatesFunc(mListItem['geometry']['coordinates'])

# References
# http://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL
# https://overpass-turbo.eu/
# Creat file to inspect overpass_response

#My_File = open('city.geojson','x')
#json.dump(overpass_response, My_File)
#My_File.close()
#mFile = open('city.geojson','r')
#mGeoJSON = json.load(mFile)
# mGeoJSON is dict
#mFeaturesList_of_Dict = mGeoJSON['features']
#mFile.close()
