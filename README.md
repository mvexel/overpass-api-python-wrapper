# Overpass API python wrapper

This is a thin wrapper around the OpenStreetMap [Overpass API](http://wiki.openstreetmap.org/wiki/Overpass_API).

![travis](https://travis-ci.org/mvexel/overpass-api-python-wrapper.svg)

## Install it

```bash
$ python setup.py install
```

The module is not on PyPi yet.

## Use it

```python
>>> import overpass
>>> api = overpass.API()
>>> response = api.Get('node["name"="Salt Lake City"]')
```

Note that you don't have to include any of the output meta statements. The wrapper will, well, wrap those.

You will get your result as a dictionary, which (for now) represents the JSON output you would get [from the Overpass API directly](http://overpass-api.de/output_formats.html#json). So you could do this for example:

```python
>>> print [(feature['tags']['name'], feature['id']) for feature in response['elements']]
[(u'Salt Lake City', 150935219), (u'Salt Lake City', 585370637), (u'Salt Lake City', 1615721573)]
```

### Parameters

The API takes a few parameters:

#### `endpoint`

The default endpoint is `http://overpass-api.de/api/interpreter` but you can pass in the rambler instance (`http://overpass.osm.rambler.ru/cgi/interpreter`) or your own:

```python
api = overpass.API(endpoint=http://overpass.myserver/interpreter)
```

#### `timeout`

The default timeout is 25 seconds, but you can set it to whatever you want.

```python
api = overpass.API(timeout=600)
```

#### `debug`

Setting this to `True` will get you debug output.

#### `bbox`

This takes a list in the form `[minlon, minlat, maxlon, maxlat]`, the default is the world: `[-180.0, -90.0, 180.0, 90.0]`

### Simple queries

In addition to just send you query and parse it, the wrapper provides shortcuts for often used map queries. To use them, just pass them like to normal query to the API.

#### MapQuery

This is a shorthand for a [complete ways and relations](http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide#Completed_ways_and_relations) query in a bounding box (the 'map call').
You just pass the bounding box to the constructor:

```python
>>> map_query = overpass.MapQuery(50.746,7.154,50.748,7.157)
>>> response = api.Get(map_query)
```

#### WayQuery

This is shorthand for getting a set of ways and their child nodes that satisfy certain criteria.
Pass the criteria as a Overpass QL stub to the constructor:

```python
>>> way_query = overpass.WayQuery('[name=Highway 51]')
>>> response = api.Get(way_query)
```

## Need help? Want feature?

Create a [new issue](https://github.com/mvexel/overpass-api-python-wrapper/issues).

## Test it

```
py.test
```

_There are almost no tests yet._

## Fork it

[Yes please](https://github.com/mvexel/overpass-api-python-wrapper/fork). [Help wanted](https://github.com/mvexel/overpass-api-python-wrapper/labels/help%20wanted).

