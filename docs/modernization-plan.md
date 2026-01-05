# 0.8 Modernization Plan

## Goals
- Keep sync `overpass.API` stable while adding a parallel async client.
- Introduce opt-in Pydantic models (v2) for responses and helpers for GeoJSON output.
- Improve test coverage to avoid regressions across all response formats and errors.

## Non-goals (for 0.8 alpha)
- Breaking changes to default return types.
- Full rewrite of the API surface.

## Design overview
- Split transport from parsing to make sync/async share code.
- Add a typed response layer:
  - Pydantic models for Overpass JSON and GeoJSON.
  - Dataclasses for configuration and small internal structures.
- Provide helpers on models (`to_geojson()`, `__geo_interface__`) while keeping
  existing dict return behavior by default.

## Implemented (current branch)
- Shared transport abstraction for sync/async HTTP.
- `AsyncAPI` alongside `API` (httpx-based).
- Opt-in Pydantic models for Overpass JSON + GeoJSON, plus CSV/XML wrappers.
- `to_geojson()` and `__geo_interface__` on GeoJSON models (Shapely round-trip test).
- Extended tests for response formats, error mapping, and async parity.
- Hardened JSON parsing with clearer errors when content is invalid.
- `Utils.to_overpass_id` now requires a source type (`way` or `relation`).

## Testing strategy
- Unit tests for:
  - Query construction (`MapQuery`, `WayQuery`, `build`, `verbosity`, `date`).
  - Response parsing for CSV/XML/JSON/GeoJSON.
  - Error mapping for HTTP status codes (400/429/504/other).
  - Overpass status endpoint parsing.
- Async parity tests for the same responses using mocked HTTP.
- Integration tests remain opt-in (`RUN_NETWORK_TESTS=1`).

## Open questions
- GeoJSON hardening for relations/multipolygons/routes/boundaries (#181).
