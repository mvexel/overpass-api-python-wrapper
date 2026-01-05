Deprecated README.rst
=====================

This file is deprecated. Please use ``README.md`` instead.

The Markdown version is the canonical documentation and is kept up to date.

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
