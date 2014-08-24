# Overpass API python wrapper

This is a thin wrapper around the OpenStreetMap [Overpass API](http://wiki.openstreetmap.org/wiki/Overpass_API).

## Use it

```
>>> import Overpass
>>> api = Overpass.API()
>>> response = api.Get('[out:json];node["name":"Salt Lake City"];out body;')
```

You will get your result as a dictionary, which (for now) represents the JSON output you would get [from the Overpass API directly](http://overpass-api.de/output_formats.html#json). So you could do this for example:

```
>>> print [(feature['tags']['name'], feature['id']) for feature in response['elements']]
[(u'Salt Lake City', 150935219), (u'Salt Lake City', 585370637), (u'Salt Lake City', 1615721573)]
```

## Fork it

[Yes please](https://github.com/mvexel/overpass-api-python-wrapper/fork).