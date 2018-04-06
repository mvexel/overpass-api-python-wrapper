Overpass API python wrapper
===========================

This is a thin wrapper around the OpenStreetMap `Overpass
API <http://wiki.openstreetmap.org/wiki/Overpass_API>`__.

|Build Status|

Install it
==========

``pip install overpass``

Usage
-----

Simplest example:

.. code:: python

    import overpass
    api = overpass.API()
    response = api.get('node["name"="Salt Lake City"]')

``response`` will be a dictionary representing the JSON output you would
get `from the Overpass API
directly <https://overpass-api.de/output_formats.html#json>`__.

Note that the Overpass query passed to ``get()`` should not contain any
``out`` or other meta statements.

Another example:

.. code:: python

    >>> print [(
    ...     feature['properties']['name'],
    ...     feature['id']) for feature in response["features"]]
    [(u'Salt Lake City', 150935219), (u'Salt Lake City', 585370637)]

You can find more examples in the ``examples/`` directory of this
repository.

Response formats
~~~~~~~~~~~~~~~~

You can set the response type of your query using ``get()``\ ’s
``responseformat`` parameter to GeoJSON (``geojson``, the default),
plain JSON (``json``), CSV (``csv``), and OSM XML (``xml``).

.. code:: python

    response = api.get('node["name"="Salt Lake City"]', responseformat="xml")

Parameters
~~~~~~~~~~

The API object takes a few parameters:

``endpoint``
^^^^^^^^^^^^

The default endpoint is ``https://overpass-api.de/api/interpreter`` but
you can pass in another instance:

.. code:: python

    api = overpass.API(endpoint=https://overpass.myserver/interpreter)

``timeout``
^^^^^^^^^^^

The default timeout is 25 seconds, but you can set it to whatever you
want.

.. code:: python

    api = overpass.API(timeout=600)

``debug``
^^^^^^^^^

Setting this to ``True`` will get you debug output.

Simple queries
~~~~~~~~~~~~~~

In addition to just sending your query and parse the result, the wrapper
provides shortcuts for often used map queries. To use them, just pass
them like to normal query to the API.

MapQuery
^^^^^^^^

This is a shorthand for a `complete ways and
relations <https://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide#Recursing_up_and_down:_Completed_ways_and_relations>`__
query in a bounding box (the ‘map call’). You just pass the bounding box
to the constructor:

.. code:: python

    MapQuery = overpass.MapQuery(50.746,7.154,50.748,7.157)
    response = api.get(MapQuery)

WayQuery
^^^^^^^^

This is shorthand for getting a set of ways and their child nodes that
satisfy certain criteria. Pass the criteria as a Overpass QL stub to the
constructor:

.. code:: python

    WayQuery = overpass.WayQuery('[name="Highway 51"]')
    response = api.get(WayQuery)

Testing
-------

Using ``pytest``.

``py.test``

FAQ
---

I need help or have an idea for a feature
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a `new
issue <https://github.com/mvexel/overpass-api-python-wrapper/issues>`__.

Where did the CLI tool go?
~~~~~~~~~~~~~~~~~~~~~~~~~~

The command line tool was deprecated in version 0.4.0.

.. |Build Status| image:: https://travis-ci.org/mvexel/overpass-api-python-wrapper.svg?branch=master
   :target: https://travis-ci.org/mvexel/overpass-api-python-wrapper
