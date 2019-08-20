Overpass API python wrapper
===========================

Python bindings for the OpenStreetMap [Overpass
API](http://wiki.openstreetmap.org/wiki/Overpass_API).

[![Build Status](https://travis-ci.org/mvexel/overpass-api-python-wrapper.svg?branch=master)](https://travis-ci.org/mvexel/overpass-api-python-wrapper)

Install it
==========

`pip install overpass`

## Usage

### `API()` constructor

First, create an API object.

```python
import overpass
api = overpass.API()
```

The API constructor takes several parameters, all optional:

#### `endpoint`

The default endpoint is `https://overpass-api.de/api/interpreter` but
you can pass in another instance:

```python
api = overpass.API(endpoint="https://overpass.myserver/interpreter")
```

#### `timeout`

The default timeout is 25 seconds, but you can set it to whatever you
want.

```python
api = overpass.API(timeout=600)
```

#### `debug`

Setting this to `True` will get you debug output.

### Getting data from Overpass: `get()`

Most users will only ever need to use the `get()` method. There are some convenience query methods for common queries as well, see below.

```python
response = api.get('node["name"="Salt Lake City"]')
```

`response` will be a dictionary representing the
JSON output you would get [from the Overpass API
directly](https://overpass-api.de/output_formats.html#json). 

**Note that the Overpass query passed to `get()` should not contain any `out` or other meta statements.** See `verbosity` below for how to control the output.

Another example:

```python
>>> print [(
...     feature['properties']['name'],
...     feature['id']) for feature in response["features"]]
[(u'Salt Lake City', 150935219), (u'Salt Lake City', 585370637)]
```

You can find more examples in the `examples/` directory of this repository.

The `get()` method takes a few parameters, all optional having sensible defaults.

#### `verbosity`

You can set the verbosity of the [Overpass query `out` directive](https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL#out) using the same keywords Overpass does. In order of increased verbosity: `ids`, `skel`, `body`, `tags`, `meta`. As is the case with the Overpass API itself, `body` is the default.

```python
>>> import overpass
>>> api = overpass.API()
>>> data = api.get('way(42.819,-73.881,42.820,-73.880);(._;>;)', verbosity='geom')
>>> [f for f in data.features  if f.geometry['type'] == "LineString"]
```

(from [a question on GIS Stackexchange](https://gis.stackexchange.com/questions/294152/getting-all-information-about-ways-from-python-overpass-library/294358#294358))

#### `responseformat`

You can set the response type of your query using `get()`'s `responseformat` parameter to GeoJSON (`geojson`, the default), plain JSON (`json`), CSV (`csv`), and OSM XML (`xml`).

```python
response = api.get('node["name"="Salt Lake City"]', responseformat="xml")
```

#### `build`

We will construct a valid Overpass QL query from the parameters you set by default. This means you don't have to include 'meta' statements like `[out:json]`, `[timeout:60]`, `[out body]`, etcetera. You just supply the meat of the query, the part that actually tells Overpass what to query for. If for whatever reason you want to override this and supply a full, valid Overpass QL query, you can set `build` to `False` to make the API not do any pre-processing.

### Pre-cooked Queries: `MapQuery`, `WayQuery` 

In addition to just sending your query and parse the result, `overpass`
provides shortcuts for often used map queries. To use them, just pass
them like to normal query to the API.

#### MapQuery

This is a shorthand for a [complete ways and
relations](https://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide#Recursing_up_and_down:_Completed_ways_and_relations)
query in a bounding box (the 'map call'). You just pass the bounding box
to the constructor:

```python
MapQuery = overpass.MapQuery(50.746,7.154,50.748,7.157)
response = api.get(MapQuery)
```

#### WayQuery

This is shorthand for getting a set of ways and their child nodes that
satisfy certain criteria. Pass the criteria as a Overpass QL stub to the
constructor:

```python
WayQuery = overpass.WayQuery('[name="Highway 51"]')
response = api.get(WayQuery)
```

## Testing

Using `pytest`.

`py.test`

## FAQ

### I need help or have an idea for a feature

Create a [new
issue](https://github.com/mvexel/overpass-api-python-wrapper/issues).

### Where did the CLI tool go?

The command line tool was deprecated in version 0.4.0.
