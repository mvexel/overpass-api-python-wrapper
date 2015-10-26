Overpass API python wrapper
===========================

This is a thin wrapper around the OpenStreetMap `Overpass
API <http://wiki.openstreetmap.org/wiki/Overpass_API>`__.

.. image:: https://travis-ci.org/mvexel/overpass-api-python-wrapper.svg
   :target: https://travis-ci.org/mvexel/overpass-api-python-wrapper


Install it
==========

.. code:: bash

    $ pip install overpass

If you get an error similar to

::

    OSError: Could not find library geos_c or load any of its variants ['libgeos_c.so.1', 'libgeos_c.so']

you can install the required libraries on linux with

.. code:: bash

    $ sudo apt-get install libgeos-c1 libgeos-3.4.2

Use it
======

You can use the overpass command line interface or use it as a Python
library.

Command line interface
---------------------

You can use the CLI to execute queries and save the result in a GeoJSON
file.

::

    Usage: overpass [OPTIONS] QUERY OUTPUT_FILE

    Run query and save the result in output_file

    Options:
    --timeout INTEGER  Timeout in seconds
    --endpoint TEXT    URL of your prefered API
    --help             Show this message and exit.

For example:

.. code:: bash

    overpass --timeout 50 'node(area:3602758138)[amenity=cafe]' brasilia-cafe.geojson

Python Library
-------------

.. code:: python

    >>> import overpass
    >>> api = overpass.API()
    >>> response = api.Get('node["name"="Salt Lake City"]')

Note that you don't have to include any of the output meta statements.
The wrapper will, well, wrap those.

You will get your result as a dictionary, which (for now) represents the
JSON output you would get `from the Overpass API
directly <http://overpass-api.de/output_formats.html#json>`__. So you
could do this for example:

.. code:: python

    >>> print [(feature['tags']['name'], feature['id']) for feature in response['elements']]
    [(u'Salt Lake City', 150935219), (u'Salt Lake City', 585370637), (u'Salt Lake City', 1615721573)]

Parameters
~~~~~~~~~~

The API takes a few parameters:

``endpoint``
^^^^^^^^^^

The default endpoint is ``http://overpass-api.de/api/interpreter`` but
you can pass in the rambler instance
(``http://overpass.osm.rambler.ru/cgi/interpreter``) or your own:

.. code:: python

    api = overpass.API(endpoint=http://overpass.myserver/interpreter)

``timeout``
^^^^^^^^^^

The default timeout is 25 seconds, but you can set it to whatever you
want.

.. code:: python

    api = overpass.API(timeout=600)

``debug``
^^^^^^^^^^

Setting this to ``True`` will get you debug output.

Simple queries
~~~~~~~~~~~

In addition to just send your query and parse the result, the wrapper
provides shortcuts for often used map queries. To use them, just pass
them like to normal query to the API.

MapQuery
^^^^^^^^

This is a shorthand for a `complete ways and
relations <http://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide#Completed_ways_and_relations>`__
query in a bounding box (the 'map call'). You just pass the bounding box
to the constructor:

.. code:: python

    >>> map_query = overpass.MapQuery(50.746,7.154,50.748,7.157)
    >>> response = api.Get(map_query)

WayQuery
^^^^^^^^

This is shorthand for getting a set of ways and their child nodes that
satisfy certain criteria. Pass the criteria as a Overpass QL stub to the
constructor:

.. code:: python

    >>> way_query = overpass.WayQuery('[name=Highway 51]')
    >>> response = api.Get(way_query)

Need help? Want feature?
=======================

Create a `new
issue <https://github.com/mvexel/overpass-api-python-wrapper/issues>`__.

Test it
-------

::

    py.test

Fork it
-------

`Yes
please <https://github.com/mvexel/overpass-api-python-wrapper/fork>`__.
`Help
wanted <https://github.com/mvexel/overpass-api-python-wrapper/labels/help%20wanted>`__.
