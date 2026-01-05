# Live Query Runner

This script is a lightweight trust tool for running known Overpass QL examples against the live API.

## Usage

List examples:

```bash
python tools/live_queries.py --list
```

Run by index or key:

```bash
python tools/live_queries.py --run 1
python tools/live_queries.py --run cafes_sf_bbox
```

Custom query:

```bash
python tools/live_queries.py --query 'node["amenity"="cafe"](37.77,-122.45,37.79,-122.43)' --responseformat geojson
```

Notes:
- Uses the public Overpass API by default.
- `--model` enables Pydantic models.
- `--save` writes raw output to disk.
