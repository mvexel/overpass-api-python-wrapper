# GeoJSON Fixtures (osmtogeojson reference)

We use `osmtogeojson` as a reference implementation to generate GeoJSON fixtures
for relation-heavy cases (multipolygons, routes, boundaries).

This does **not** add a runtime dependency. It is only for generating fixtures.

## Setup

Install Node and the converter:

```bash
npm install --global osmtogeojson
```

## Generate a fixture

Given an Overpass JSON response saved to `tests/fixtures/input.json`:

```bash
node tools/osmtogeojson_fixture.js tests/fixtures/input.json tests/fixtures/output.geojson
```

Commit the resulting `output.geojson` and use it as a golden file in tests.
