# Overpass API python wrapper

This is a thin wrapper around the OpenStreetMap [Overpass API](http://wiki.openstreetmap.org/wiki/Overpass_API).

## Use it

```
>>> import Overpass
>>> api = Overpass.API()
>>> response = api.Get('node["name":"Salt Lake City"]')
```

Note that you don't have to include any of the output meta statements. The wrapper will, well, wrap those.

You will get your result as a dictionary, which (for now) represents the JSON output you would get [from the Overpass API directly](http://overpass-api.de/output_formats.html#json). So you could do this for example:

```
>>> print [(feature['tags']['name'], feature['id']) for feature in response['elements']]
[(u'Salt Lake City', 150935219), (u'Salt Lake City', 585370637), (u'Salt Lake City', 1615721573)]
```

### Parameters

The API takes a few parameters:

#### `endpoint`

The default endpoint is `http://overpass-api.de/api/interpreter` but you can pass in the rambler instance (`http://overpass.osm.rambler.ru/cgi/interpreter`) or your own:

    api = Overpass.API(endpoint=http://overpass.myserver/interpreter)

#### `timeout`

The default timeout is 25 seconds, but you can set it to whatever you want.

    api = Overpass.API(timeout=600)

#### `debug`

Setting this to `True` will get you debug output.

## Fork it

[Yes please](https://github.com/mvexel/overpass-api-python-wrapper/fork).