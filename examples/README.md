# Examples

Please contribute your examples, submit a pull request!

## Turn restrictions as a list

File: `turn_restriction_relations_as_list.py`

This example requests a CSV response from an Overpass query for turn restrictions within the Toronto city limits.

The result is then converted to a Python list and printed to stdout.

Sample output:

```python
['6809605', 'hoream_telenav', '2016-12-21T15:05:42Z', '', 'no_left_turn'], 
...
```

## Plot state border

File: `plot_state_border/main.py`

This example requests the boundary of a state of Germany called Saxony. The overpass response contains points that will be connected with each other to draw the outer border of the state. The lines are drawn using `matplotlib`.
Since the response is quite big (~2 MB) the response will be saved in a XML file.

Overpass query:
```osm
area[name="Sachsen"][type="boundary"]->.saxony;
rel(area.saxony)[admin_level=4][type="boundary"][boundary="administrative"];
out geom;
```

Output:
![Border of Saxony (Germany)](plot_state_border/output.png)

