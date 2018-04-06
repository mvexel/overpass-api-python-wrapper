Overpass API python wrapper
===========================

This is a thin wrapper around the OpenStreetMap [Overpass
API](http://wiki.openstreetmap.org/wiki/Overpass_API).

[![Build Status](https://travis-ci.org/mvexel/overpass-api-python-wrapper.svg?branch=master)](https://travis-ci.org/mvexel/overpass-api-python-wrapper)

Install it
==========

`pip install overpass`

## Usage

Simplest example:

```python
import overpass
api = overpass.API()
response = api.get('node["name"="Salt Lake City"]')
```

Note that you don't have to include any of the output meta statements.
The wrapper will, well, wrap those.

You will get your result as a dictionary, which represents the
JSON output you would get [from the Overpass API
directly](https://overpass-api.de/output_formats.html#json). So you
could do this for example:

```python
print [(feature['tags']['name'], feature['id']) for feature in response['elements']]
[(u'Salt Lake City', 150935219), (u'Salt Lake City', 585370637), (u'Salt Lake City', 1615721573)]
```

You can specify the format of the response. By default, you will get GeoJSON using the `responseformat` parameter. Alternatives are plain JSON (`json`) and OSM XML (`xml`), as ouput directly by the Overpass API.

```python
response = api.get('node["name"="Salt Lake City"]', responseformat="xml")
```

### Parameters


The API object takes a few parameters:

#### endpoint

The default endpoint is `https://overpass-api.de/api/interpreter` but
you can pass in another instance:

```python
api = overpass.API(endpoint=https://overpass.myserver/interpreter)
```

#### timeout

The default timeout is 25 seconds, but you can set it to whatever you
want.

```python
api = overpass.API(timeout=600)
```

#### debug

Setting this to `True` will get you debug output.

### Simple queries

In addition to just send your query and parse the result, the wrapper
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

Using `nose`.

`py.test`

## FAQ

### I need help or have an idea for a feature

Create a [new
issue](https://github.com/mvexel/overpass-api-python-wrapper/issues).

### Where did the CLI tool go?

I decided that it does not belong in this repo. If you still want it, get version 0.4.0 or below.
